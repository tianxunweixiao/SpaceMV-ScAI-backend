import os
from agi.stk12.stkruntime import STKRuntime
from agi.stk12.stkobjects import *
from agi.stk12.stkutil import AgEYPRAnglesSequence
from libs.stk_backprogress import *
import argparse
import json
import socket
import contextlib

def main():
    '''
    start_time: str # Simulation start time 20130912032513
    end_time: str # Simulation end time 20130915032619
    step: str # Step size
    satellites: list # Satellite and sensor parameter data
           [{ “ID”: xxx,
             “name”: xxx,
             “tle1”: xxx,
             “tle2”: xxx,
             “sensor_type”: xxx,
             “sensor_para”: xxx
           }, ...... ]
    path: str # Folder path for storing simulation result reports
    point: str # Point data (longitude first, latitude second) “123 41”
    line: str # Line data “123 31|124 31”
    area: str # Area data “123 34|134 41|127 37”
    :return:
    '''

     # Search for an available port
    def get_free_port():
        with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            s.bind(('', 0))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            return s.getsockname()[1]


    parser = argparse.ArgumentParser(description="stk engine api")
    parser.add_argument("--start_time", type=str, required=True, help="仿真任务开始时间")
    parser.add_argument("--end_time", type=str, required=True, help="仿真任务结束时间")
    parser.add_argument("--step", type=str, required=True, help="仿真步长")
    parser.add_argument("--satellites", type=json.loads, required=True, help="存储卫星ID、name、TLE、传感器视场角、传感器姿态角的dict")
    parser.add_argument("--path", type=str, required=True, help="存储仿真结果报告的文件夹路径")
    parser.add_argument("--point", type=str, required=True, help="点目标经纬度")
    parser.add_argument("--line", type=str, required=True, help="线目标经纬度")
    parser.add_argument("--area", type=str, required=True, help="面目标经纬度")

    args = parser.parse_args()  
    # Dynamically obtain an available port
    free_port = get_free_port()

    stk = None
    try:
        # ------------------------------Create an STK instance-------------------------------------------
        stk = STKRuntime.StartApplication(grpc_host="0.0.0.0", grpc_port=free_port, userControl=False)
        root=stk.NewObjectRoot()
        root.NewScenario("MyScenario")

        scenario = root.CurrentScenario
        scenario.SetTimePeriod(trans_date_stk(args.start_time), trans_date_stk(args.end_time))

        # ------------------------------Create Ground Point Target--------------------------------------------
        target_point = scenario.Children.New(23, 'PointTarget')
        point_lat = float(args.point.split(' ')[1])
        point_lon = float(args.point.split(' ')[0])
        # 纬度在前，经度在后
        target_point.Position.AssignGeodetic(point_lat, point_lon, 0)

        # ------------------------------Create Ground Line Target--------------------------------------------
        target_line = scenario.Children.New(2, 'LineTarget')
        line_coords = args.line.split('|')
        target_line.AreaType = AgEAreaType.ePattern
        line_pattern = target_line.AreaTypeData
        for coords in line_coords:
            coord_lat = coords.split(' ')[1]
            coord_lon = coords.split(' ')[0]
            line_pattern.Add(coord_lat, coord_lon)

        line_pattern.Add(line_coords[0].split(' ')[1], line_coords[0].split(' ')[0])  

        # ------------------------------Create a ground surface target---------------------------------------------
        target_area = scenario.Children.New(2, 'AreaTarget')
        area_coords = args.area.split('|')
        target_area.AreaType = AgEAreaType.ePattern
        area_pattern = target_area.AreaTypeData
        for coords in area_coords:
            coord_lat = coords.split(' ')[1]
            coord_lon = coords.split(' ')[0]
            area_pattern.Add(coord_lat, coord_lon)

        # -------------------------Create satellite------------------------------------
        satellite = scenario.Children.New(18, "Satellite")  

        # ------------------------Create Sensor------------------------------------
        sensor = satellite.Children.New(20, "Sensor") 

        # ------------------------Create Ground Cover Analysis Target----------------------------
        coveragedefinition = scenario.Children.New(7, 'GroundCoverage')  # CoverageDefinition

        coveragedefinition.Grid.BoundsType = AgECvBounds.eBoundsCustomBoundary
        bounds = coveragedefinition.Grid.Bounds
        bounds.BoundaryObjects.AddObject(target_area)

        coveragedefinition.Grid.ResolutionType = AgECvResolution.eResolutionLatLon
        coveragedefinition.Grid.Resolution.LatLon = 0.1

        coveragedefinition.AssetList.Add(sensor.Path)

        constellation_simu = len(args.satellites) > 1

        for item in args.satellites:
            if constellation_simu:
                save_path = args.path + '/' + item['name'] + '_' + item['ID']
            else:
                save_path = args.path

            os.makedirs(save_path, exist_ok=True)
            # --------------------------------------Save TLE file---------------------------------------------
            line1_fmt, line2_fmt = format_tle(item['tle1'], item['tle2'])
            tle1 = line1_fmt + '\n'
            tle2 = line2_fmt + '\n'

            with open(save_path + "/TLE.txt", "w", encoding="utf-8") as f:
                f.write(tle1)
                f.write(tle2)

            # --------------------------------------Set satellite orbital parameters------------------------------------------
            satellite.SetPropagatorType(4)  # 4 = ePropagatorSGP4
            propagator = satellite.Propagator
            # Load Tracks from TLE File
            propagator.CommonTasks.AddSegsFromFile(str(item['ID']), save_path + "/TLE.txt")
            propagator.Propagate()

            # --------------------------------------Set sensor parameters------------------------------------------
            sensor.CommonTasks.SetPatternRectangular(float(item['sensor_para'][0]) * 2, float(item['sensor_para'][1]) * 2)  # 矩形视场
            yaw = item['sensor_para'][4]
            pitch = item['sensor_para'][3]
            roll = item['sensor_para'][2]
            sensor.CommonTasks.SetPointingFixedYPR(AgEYPRAnglesSequence.eYPR, float(yaw), float(pitch), float(roll))  # 传感器姿态角

            # ------------------------------------LLA POSITION----------------------------------------------

            lla_DP = satellite.DataProviders["LLA State"].Group.Item(1)

            startTime = scenario.StartTime
            stopTime = scenario.StopTime
            result = lla_DP.Exec(startTime, stopTime, float(args.step))

            time_table = result.DataSets.GetDataSetByName("Time").GetValues()
            lons = result.DataSets.GetDataSetByName("Lon").GetValues()
            lats = result.DataSets.GetDataSetByName("Lat").GetValues()
            alts = result.DataSets.GetDataSetByName("Alt").GetValues()

            posLLA(save_path, time_table, lons, lats, alts)

            # -------------------------------------Sensor Projection----------------------------------------
            sensor_dp = sensor.DataProviders['Pattern Intersection']

            # float(args.step)
            result = sensor_dp.Exec(startTime, stopTime, float(args.step)).DataSets 
            element_names = result.ElementNames
            latitude_indices = [i for i, name in enumerate(element_names) if name == 'Latitude']
            longitude_indices = [i for i, name in enumerate(element_names) if name == "Longitude"]

            all_latitudes = []
            for idx in latitude_indices:
                ds = result.Item(idx)
                values = ds.GetValues()
                all_latitudes.append(values)

            all_longitudes = []
            for idx in longitude_indices:
                ds = result.Item(idx)
                values = ds.GetValues()
                all_longitudes.append(values)

            sensorProjection(save_path, all_latitudes, all_longitudes)

            # ---------------------------------------simulation report-----------------------------------------

            # ----------point
            access = sensor.GetAccessToObject(target_point)
            access.ComputeAccess()
            dp = access.DataProviders.Item('Access Data')
            results = dp.Exec(scenario.StartTime, scenario.StopTime)
            if results.DataSets.Count != 0:
                # Overlapping results
                start_times = results.DataSets.GetDataSetByName('Start Time').GetValues()
                stop_times = results.DataSets.GetDataSetByName('Stop Time').GetValues()
                durations = results.DataSets.GetDataSetByName('Duration').GetValues()
            else:
                start_times = []
                stop_times = []
                durations = []

            paras_point = [start_times, stop_times, durations]
            stk_report(save_path, paras_point, 1)

            # -----------line
            access = sensor.GetAccessToObject(target_line)
            access.ComputeAccess()
            dp = access.DataProviders.Item('Access Data')
            results = dp.Exec(scenario.StartTime, scenario.StopTime)

            if results.DataSets.Count != 0:
                start_times = results.DataSets.GetDataSetByName('Start Time').GetValues()
                stop_times = results.DataSets.GetDataSetByName('Stop Time').GetValues()
                durations = results.DataSets.GetDataSetByName('Duration').GetValues()
            else:
                start_times = []
                stop_times = []
                durations = []

            paras_line = [start_times, stop_times, durations]
            stk_report(save_path, paras_line, 2)

            # -----------area
            coveragedefinition.ComputeAccesses()

            coverage_access = coveragedefinition.DataProviders['All Regions By Pass']
            coverage_result = coverage_access.Exec().DataSets

            if coverage_result.Count != 0:
                start_times = coverage_result.GetDataSetByName('Access Start').GetValues()
                stop_times = coverage_result.GetDataSetByName('Access End').GetValues()
                durations = coverage_result.GetDataSetByName('Duration').GetValues()
                coverage_percent = coverage_result.GetDataSetByName('Percent Coverage').GetValues()
            else:
                start_times = []
                stop_times = []
                durations = []
                coverage_percent = []

            paras_area = [start_times, stop_times, durations, coverage_percent]
            stk_report(save_path, paras_area, 3)
    finally:
        if stk is not None:
            stk.ShutDown() # Terminate the STK process

if __name__ == "__main__":
    main()


