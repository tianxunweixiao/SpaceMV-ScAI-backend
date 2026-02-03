from typing import Dict, Any, List
import logging


class SatelliteService:
    """Service for satellite-related operations"""
    
    async def get_all_satellites(self) -> List[Dict[str, Any]]:
        """
        Get all satellites from database
        
        Returns:
            List of satellite data
        """
        from constellation_app import get_app
        app = get_app()
        pool = app.state.clickhouse_pool
        client = await pool.acquire()
        
        if not client:
            return []
        
        try:
            keys = [
                "Mass", "adcs", "altName", "bus", "configuration", "country", "diameter",
                "dryMass", "equipment", "launchDate", "launchMass", "launchPad",
                "launchSite", "launchVehicle", "length", "manufacturer", "mission",
                "motor", "name", "owner", "payload", "purpose", "rcs", "shape", "sources",
                "span", "stableDate", "status", "tle1", "tle2", "transmitterFrequencies",
                "type", "vmag"
            ]
            rows = await client.execute(f"SELECT {','.join(keys)} FROM satellites", columnar=False)

            result = []
            for row in rows:
                if not isinstance(row, dict):
                    row = dict(zip(keys, row))

                filtered_row = {}
                for k, v in row.items():
                    if v == "":
                        continue  
                    if k == "type" and v == -1:
                        continue
                    if k == "vmag" and v == '-1':
                        continue
                    if k == 'vamg' and v != '-1':
                        v = float(v)
                    filtered_row[k] = v

                result.append(filtered_row)

            logging.info("已成功返回所有卫星数据")
            return result
        except Exception as e:
            logging.error(f"卫星数据返回出错: {e}")
            raise
        finally:
            await pool.release(client)
    
    async def update_sensor(self, satellite_id: str, sensor_type: int, hha: float, vha: float, 
                           max_pa: float, min_pa: float, max_aa: float, min_aa: float,
                           roll: float, pitch: float, yaw: float, Mobility: float, Band: int) -> Dict[str, Any]:
        """
        Update sensor parameters
        
        Args:
            satellite_id: Satellite identifier
            sensor_type: Sensor type (1 for optical, 2 for SAR)
            hha: Horizontal half-angle
            vha: Vertical half-angle
            max_pa: Maximum pitch angle
            min_pa: Minimum pitch angle
            max_aa: Maximum azimuth angle
            min_aa: Minimum azimuth angle
            roll: Roll angle
            pitch: Pitch angle
            yaw: Yaw angle
            Mobility: Mobility capability
            Band: Band/spectrum
            
        Returns:
            Dict containing update result
        """
        from constellation_app import get_app
        app = get_app()
        pool = app.state.clickhouse_pool
        client = await pool.acquire()
        
        if not client:
            return {"error": "数据库未连接"}
        
        if sensor_type == 1:
            paras = [hha, vha, roll, pitch, yaw, Mobility, Band]
        else:
            paras = [max_pa, min_pa, max_aa, min_aa, roll, pitch, yaw, Mobility, Band]

        paras = list(map(str, paras))
        query = """
                ALTER TABLE sensor_paras UPDATE
                    sensor_type = %(sensor_type)s,
                    sensor_value = %(paras)s
                    WHERE ID = %(satellite_id)s \
                """
        values = {
            "sensor_type": sensor_type,
            "paras": paras,
            "satellite_id": satellite_id,
        }

        try:
            await client.execute(query, values)
            logging.info(f"已更新ID为 {satellite_id} 的卫星的传感器参数")
            return {"status": "success"}
        except Exception as e:
            logging.error(f"ID为 {satellite_id} 的卫星的传感器参数更新失败: {e}")
            raise
        finally:
            await pool.release(client)
    
    async def find_sensors(self, satellite_id: str) -> Dict[str, Any]:
        """
        Find sensors by satellite ID
        
        Args:
            satellite_id: Satellite identifier
            
        Returns:
            Dict containing sensor data
        """
        from constellation_app import get_app
        app = get_app()
        pool = app.state.clickhouse_pool
        client = await pool.acquire()
        
        if not client:
            return {"error": "数据库未连接"}
        
        query = """
                SELECT sensor_type, sensor_value
                FROM sensor_paras
                WHERE ID = %(satellite_id)s \
                """
        values = {"satellite_id": str(satellite_id)}

        try:
            result = await client.execute(query, values)
            if not result:
                return {"error": f"ID为 {satellite_id} 的卫星不存在"}
            result = result[0]
            optic_keys = ['hha', 'vha']
            sar_keys = ['max_pa', 'min_pa', 'max_aa', 'min_aa']
            same_keys = ['roll','pitch','yaw','Mobility','Band']

            keys_dict = ["sensor_type"] + optic_keys + sar_keys + same_keys

            if result[0] == 1:
                output = [result[0]] + list(map(float,result[1][0:2])) + [-1,-1,-1,-1] + list(map(float,result[1][2:-1])) + [int(result[1][-1])]
            else:
                output = [result[0]] + [-1,-1] + list(map(float, result[1][0:-1])) + [int(result[1][-1])]

            logging.info(f"已查询到ID为 {satellite_id} 的卫星的传感器参数")
            return dict(zip(keys_dict, output))
        except Exception as e:
            logging.error(f"ID为 {satellite_id} 的卫星的传感器参数查询失败: {e}")
            raise
        finally:
            await pool.release(client)
