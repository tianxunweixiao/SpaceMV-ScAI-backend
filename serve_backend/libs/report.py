import os
import json
import asyncio
import zipfile
import math
from datetime import datetime, timedelta

async def create_report(level, simulation_dict, interval):
    """
    simulation_dict={'point':(1,2),'line':[(1,2),(2,3)],
                    'polygon':[(1,2),(2,3),(3,4)], start_time:20130512041203,end_time:20130512041204,
                    'save_dir':xxxxxxxx
                    'result':{'id1': {'name':'starlink1', 'satellite_dir':'xxxxxx'},
                              'id2': {......},
                              'id3': {......}
                              },
                    'payload': xxxxxxxx   Single-star simulation refers to the name of a single star / Constellation simulation refers to the name of a constellation.
                    }
    # The latitude comes first, followed by the longitude in the above coordinates
    """
    report_filename_dict = {1: '/point.txt', 2: '/line.txt', 3: '/area.txt'}
    revisit_filename_dict = {1: '/revisit_time_point.txt', 2: '/revisit_time_line.txt', 3: '/revisit_time_area.txt'}

    # Extract single-satellite report data to generate constellation coverage analysis reports and re-entry time calculations
    def extract_data(report_list, save_dir, geo_type):
        report_data = []  
        revisit_data = []  # When calculating the return period, load the array of observation periods for the entire constellation
        for item in report_list:
            with open(item[1], 'r', encoding='utf-8') as f:
                line_count = sum(1 for _ in f)  
                f.seek(0)
                for i, line in enumerate(f):
                    if i not in (0, 1, line_count - 1):
                        line = list(map(lambda x: x.strip(), line.strip().split('|')))
                        report_data.append(item[0] + '       ' + '       '.join(line))
                        revisit_data.append(datetime.strptime(line[0], "%Y-%m-%d %H:%M:%S.%f"))

        with open(save_dir + '/simulation_report/' + report_filename_dict[geo_type], "a", encoding='utf-8') as f:
            f.write(
                '                  卫星名称(编号)                           开始时间（UTC）                  结束时间（UTC）               持续时间（s）  覆盖百分比（%）\n')
            for item in report_data:
                f.write(item + '\n')

        # Calculate Return Time
        start_time = datetime.strptime(simulation_dict['start_time'], "%Y%m%d%H%M%S")
        end_time = datetime.strptime(simulation_dict['end_time'], "%Y%m%d%H%M%S")
        revisit_time_report = []

        current_time = start_time
        while current_time <= end_time:
             # formatted: 2025-09-13 04:08:13.143
            candidates = [t for t in revisit_data if t > current_time]
            if candidates:
                revisit_time = (min(candidates) - current_time).total_seconds()  # 以秒为单位
            else:
                revisit_time = ''
            formatted = current_time.strftime("%Y-%m-%d %H:%M:%S")
            revisit_time_report.append(formatted + '                       ' + str(revisit_time))
            current_time += timedelta(seconds=1)

        with open(save_dir +  '/simulation_report/' + revisit_filename_dict[geo_type], "a", encoding='utf-8') as f:
            f.write('              时间戳                                        重返周期(s)\n')
            for item in revisit_time_report:
                f.write(item + '\n')

    # posLLA and sensor projection post-processing functions
    def back_progress(report_dir, pay_load, out_dir, interval):
        # Processing posLLA.txt files
        data_dict = {}
        with open(os.path.join(report_dir, 'posLLA.txt'), "r", encoding="utf-8") as f:
            lines = f.readlines()
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            
            time_str = parts[0] + " " + parts[1]
            lon = float(parts[2])
            lat = float(parts[3])
            height = float(parts[4])
            data_dict[time_str] = [lon, lat, height]
        # Write to JSON file
        with open(os.path.join(out_dir, 'poslla', f'posLLA_{pay_load}.json'), "w", encoding="utf-8") as f:
            json.dump(data_dict, f, ensure_ascii=False, indent=4)

        # Processing sensor projection files
        sen_projection = {}
        with open(os.path.join(report_dir, 'sensorProjection.txt'), "r", encoding="utf-8") as f:
            lines = f.readlines()

            t1 = datetime.strptime(simulation_dict['start_time'], "%Y%m%d%H%M%S")
            t2 = datetime.strptime(simulation_dict['end_time'], "%Y%m%d%H%M%S")

            time_step = float(interval) # Time step
            diff_seconds = (t2 - t1).total_seconds() # Total Time (s)
            time_length = math.ceil(diff_seconds / time_step) + 1  # Number of timestamps
            row_step = int((len(lines) - 1) / time_length) # Line length of the txt file

            fmt_out = "%Y-%m-%d %H:%M:%S.%f"

            t = t1
            row_start = 1
            while t <= t2:
                latlon_list = []
                for i in range(row_start, row_start + row_step):
                    line = lines[i].strip()
                    if not line:
                        continue

                    parts = line.split()

                    lat = float(parts[0])
                    lon = float(parts[1])

                    latlon_list.append([lat, lon])

                sen_projection[t.strftime(fmt_out)[:-3]] = latlon_list

                t += timedelta(seconds=time_step)
                row_start += row_step

        # Write to JSON file
        with open(os.path.join(out_dir, 'sensorprojection', f'sensorProjection_{pay_load}.json'), "w", encoding="utf-8") as f:
            json.dump(sen_projection, f, ensure_ascii=False, indent=4)

        # Add point, line, and surface coordinate JSON
        with open(os.path.join(out_dir, 'targets', f'targets.json'), "w",
                  encoding="utf-8") as f:
            targets_dict = {'point': simulation_dict['point'],
                            'line': simulation_dict['line'],
                            'polygon': simulation_dict['polygon']
                            }
            json.dump(targets_dict, f, ensure_ascii=False, indent=4)

    # Extract the posLLA.txt and sensorprojection.txt files from the simulation report to their respective folders for dynamic visualization
    def visual_json_extract(simulation_dict, interval):
        visual_dir = os.path.join(simulation_dict['save_dir'], simulation_dict['payload'])
        os.makedirs(visual_dir, exist_ok=True)
        os.makedirs(os.path.join(visual_dir, 'poslla'), exist_ok=True)
        os.makedirs(os.path.join(visual_dir, 'sensorprojection'), exist_ok=True)
        os.makedirs(os.path.join(visual_dir, 'targets'), exist_ok=True)

        for k, v in simulation_dict['result'].items():
            back_progress(v['satellite_dir'], v['name'], visual_dir, interval)

    if level == 1:
        # Consolidate all coverage visibility period reports
        point_report = []
        line_report = []
        polygon_report = []
        for key, value in simulation_dict['result'].items():
            point_report.append((value['name'] + '_' + key, value['satellite_dir'] + '/point.txt'))
            line_report.append((value['name'] + '_' + key, value['satellite_dir'] + '/line.txt'))
            polygon_report.append((value['name'] + '_' + key, value['satellite_dir'] + '/area.txt'))

        await asyncio.to_thread(extract_data, point_report, simulation_dict['save_dir'], 1)
        await asyncio.to_thread(extract_data, line_report, simulation_dict['save_dir'], 2)
        await asyncio.to_thread(extract_data, polygon_report, simulation_dict['save_dir'], 3)

    if level == 1:
        files_dir = ["satellites_data", "simulation_report"]
    else:
        files_dir = ["simulation_report"]

    zip_path = os.path.join(simulation_dict['save_dir'], "report.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for folder_name in files_dir:
            folder_path = os.path.join(simulation_dict['save_dir'], folder_name)
            if os.path.exists(folder_path):
                for root, dirs, files in os.walk(folder_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, simulation_dict['save_dir'])
                        zipf.write(file_path, arcname)

    visual_json_extract(simulation_dict, interval)
