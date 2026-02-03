from typing import Dict, Any, List
import logging


class ConstellationService:
    """Service for constellation-related operations"""
    
    async def get_all_constellations(self) -> List[Dict[str, Any]]:
        """
        Get all constellations from database
        
        Returns:
            List of constellation data
        """
        from constellation_app import get_app
        app = get_app()
        pool = app.state.clickhouse_pool
        client = await pool.acquire()
        
        try:
            query = """
            SELECT constellation, constellation_name, constellation_type
            FROM constellations
            """
            result = await client.execute(query)
            
            rows = [{"constellation": r[0], "constellation_name": r[1], "constellation_type": r[2]} for r in result]
            logging.info("已成功返回所有星座数据")
            return rows
        except Exception as e:
            logging.error(f"星座数据返回出错: {e}")
            raise
        finally:
            await pool.release(client)
    
    async def find_constellation(self, constellation_id: str) -> Dict[str, Any]:
        """
        Find constellation by ID and return all satellite IDs
        
        Args:
            constellation_id: Constellation identifier
            
        Returns:
            Dict containing constellation data and satellite IDs
        """
        from constellation_app import get_app
        app = get_app()
        pool = app.state.clickhouse_pool
        client = await pool.acquire()
        
        try:
            query_sat = """
                        SELECT ID
                        FROM satellites
                        WHERE constellation = %(constellation_id)s
                        """
            values = {"constellation_id": constellation_id}
            results = await client.execute(query_sat, values)
            result = [r[0] for r in results]
            logging.info(f"已查询到ID为{constellation_id}的星座的所有卫星数据")
            return {"constellation": constellation_id, "satellites": result}
        except Exception as e:
            logging.error(f"星座信息查询出错: {e}")
            raise
        finally:
            await pool.release(client)
    
    async def upload_constellation(self, data: Dict[str, Any], constellation_type: str) -> Dict[str, Any]:
        """
        Upload constellation data to database
        
        Args:
            data: Constellation upload data containing constellation_name and satellites
            constellation_type: Constellation type
            
        Returns:
            Dict containing upload result
        """
        from constellation_app import get_app
        app = get_app()
        pool = app.state.clickhouse_pool
        client = await pool.acquire()
        
        try:
            if not all(para in data.keys() for para in ('constellation_name', 'satellites')):
                return {'status': 'failed', 'message': '请按照规定的格式输入json文件！'}

            constellation_name = data['constellation_name']
            # Set New Constellation ID
            rows = await client.execute("SELECT toUInt64(constellation) FROM constellations")  # Retrieve all existing IDs
            used_ids = {row[0] for row in rows}
            # Increment from 1 to find an unused ID
            new_id = 1
            while new_id in used_ids:
                new_id += 1
            new_con_id = str(new_id)
            # Insert a new constellation row into the constellation table
            query_con = """
                            INSERT INTO constellations (constellation, constellation_name, constellation_type)
                            VALUES (%(constellation)s, %(constellation_name)s, %(constellation_type)s)
                """
            values = {"constellation": new_con_id, "constellation_name": constellation_name, "constellation_type": constellation_type}
            await client.execute(query_con, values)
            logging.info(f"新的星座{constellation_name}已在数据库中创建")

            # Extract satellite information from the read JSON file
            sat_datas_dict = data['satellites']
            sat_datas = []
            for k, v in sat_datas_dict.items():
                if not all(para in v for para in ('tle1', 'tle2', 'name')):
                    return {'status': 'failed', 'message': '请按照规定的格式输入json文件！'}
                sat_datas.append(v) 

            # Satellite data to be inserted/updated
            keys = [
                    "Mass", "adcs", "altName", "bus", "configuration", "country", "diameter",
                    "dryMass", "equipment", "launchDate", "launchMass", "launchPad",
                    "launchSite", "launchVehicle", "length", "manufacturer", "mission",
                    "motor", "name", "owner", "payload", "purpose", "rcs", "shape", "sources",
                    "span", "stableDate", "status", "tle1", "tle2", "transmitterFrequencies",
                    "type", "vmag"
                   ]
            rows = []  # Satellite Data

            for item in sat_datas:
                if not isinstance(item, dict):
                    continue

                tle2 = item.get("tle2", "")
                parts = tle2.split()
                ID = parts[1] if len(parts) > 1 else ""

                row = [ID, 1, new_con_id]
                for k in keys:
                    if k == 'type':
                        value = item.get(k, -1)  
                    elif k == 'vmag':
                        value = str(item.get(k, -1))  
                    else:
                        value = item.get(k, "")
                    row.append(value)
                rows.append(tuple(row))
            # Insert new satellite data into the satellite table
            columns = ["ID", "User_create", "constellation"] + keys
            query_sat = f"INSERT INTO satellites ({', '.join(columns)}) VALUES"
            await client.execute(query_sat, rows)
            # Merge data with identical primary keys
            merge_sql = f"OPTIMIZE TABLE satellites FINAL"
            await client.execute(merge_sql)
            logging.info(f"新增/更新 {len(rows)} 条卫星数据")

            # Sensor parameter data to be inserted/updated
            keys = ['name', 'sensor_type', 'sensor_value']
            rows_sensor = []  # Sensor Data
            for item in sat_datas:
                if not isinstance(item, dict):
                    continue

                tle2 = item.get("tle2", "")
                parts = tle2.split()
                ID = parts[1] if len(parts) > 1 else ""
                row_sensor = [ID]
                for k in keys:
                    if k == 'sensor_type':
                        value = item.get(k, 1)
                    elif k == 'sensor_value':
                        value = [str(para) for para in item.get(k, ['10', '10', '0', '-90', '0', '10', '1'])]

                    else:
                        value = item.get(k)
                    row_sensor.append(value)
                rows_sensor.append(tuple(row_sensor))
            
            columns = ['ID'] + keys
            query_sensor = f"INSERT INTO sensor_paras ({', '.join(columns)}) VALUES"
            await client.execute(query_sensor, rows_sensor)
            # Merge data with identical primary keys
            merge_sql_sen = f"OPTIMIZE TABLE sensor_paras FINAL"
            await client.execute(merge_sql_sen)
            logging.info(f"新增/更新 {len(rows_sensor)} 条卫星传感器数据")
            return {'status': 'success', 'message': ''}

        except Exception as e:
            logging.error(f"星座文件导入失败: {e}")
            raise
        finally:
            await pool.release(client)
    
    async def delete_constellation(self, con_id: str) -> Dict[str, Any]:
        """
        Delete constellation by ID
        
        Args:
            con_id: Constellation identifier
            
        Returns:
            Dict containing deletion result
        """
        from constellation_app import get_app
        app = get_app()
        pool = app.state.clickhouse_pool
        client = await pool.acquire()
        
        try:
            dele_conid = f"""
                          ALTER TABLE constellations
                          DELETE WHERE constellation ={con_id}
                          """
            await client.execute(dele_conid)
            merge_sql_con = f"OPTIMIZE TABLE constellations FINAL"
            await client.execute(merge_sql_con)

            # Clean up satellite data originally belonging to this constellation from the satellites table
            satellite_to_update = await client.execute(f"""
                                                       SELECT *
                                                       FROM satellites
                                                       WHERE constellation = {con_id}
                                                       """)
             # Remove the constellation field
            new_rows = []
            for row in satellite_to_update:
                row = list(row)
                # constellation in the third column
                row[2] = ''
                new_rows.append(tuple(row))
            await client.execute("INSERT INTO satellites VALUES", new_rows)
            merge_sql_sen = f"OPTIMIZE TABLE satellites FINAL"
            await client.execute(merge_sql_sen)
            logging.info(f"{con_id}号星座数据已经删除！")
            return {'status': 'success', 'message': ''}
        except Exception as e:
            logging.error(f"{con_id}号星座数据删除失败: {e}")
            raise
        finally:
            await pool.release(client)
