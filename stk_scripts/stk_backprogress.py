from datetime import datetime

def trans_date_stk(date1):
    dt = datetime.strptime(date1, "%Y%m%d%H%M%S")
    date2 = dt.strftime("%d %b %Y %H:%M:%S.%f")[:-3]
    return date2

def trans_date(date1):
    '''
    :param date1: Original time format, eg: '20 Jun 2023 20:31:27.744707798'
    :return:  Converted time format, eg: '2023-06-20 20:31:27.745'
    '''
    date_part = date1.split('.')[0]
    nanosec = date1.split('.')[1]

    millis = float('0.' + nanosec)

    dt = datetime.strptime(date_part, "%d %b %Y %H:%M:%S")

    date2 = dt.strftime("%Y-%m-%d %H:%M:%S.") + f"{format(millis, ".3f").split('.')[1][:3]}"
    return date2

def posLLA(save_path, time_table, lons, lats, alts):
    '''
    :param time_table: Time table
    :param lats: Latitude projection list
    :param lons: Longitude projection list
    :param alts: Elevation list
    :return: Generate a text file for position LLA
    '''

    header_label = "时间                         经度(°)         纬度(°)        高度(km)\n"
    with open(save_path + "/posLLA.txt", "w", encoding="utf-8") as f:
        f.write(header_label)
        for t in zip(time_table, lons, lats, alts):
            new_row = '     '.join([trans_date(t[0]), format(t[1], ".6f"), format(t[2], ".6f"), format(t[3], ".6f")]) + '\n'
            f.write(new_row)

def sensorProjection(save_path, all_latitudes, all_longitudes):

    header_label = "  lat(deg)       lon(deg)\n"
    with open(save_path + "/sensorProjection.txt", "w", encoding="utf-8") as f:
        f.write(header_label)
        for t in zip(all_latitudes, all_longitudes):
            for i in zip(t[0], t[1]):
                new_row = '      ' + '      '.join([format(i[0], ".3f"), format(i[1], ".3f")]) + '\n'
                f.write(new_row)

def stk_report(save_path, paras, target_type):
    # Obtain Coverage Analysis Reports for Point/Line/Area Targets

    hearder_label_dict = {1: "start|          |点位可见时段：\n",
                          2: "start|          |线可见时段：\n",
                          3: "start|          |面可见时段：\n"}
    sec_headers_label_dict = {1: "                  开始时间（UTC）             结束时间（UTC）    持续时间（s）\n",
                              2: "                  开始时间（UTC）             结束时间（UTC）    持续时间（s）\n",
                              3: "                  开始时间（UTC）             结束时间（UTC）    持续时间（s）    覆盖百分比（%）\n"
    }
    file_name_dict = {1: "/point.txt",
                      2: "/line.txt",
                      3: "/area.txt"}

    with open(save_path + file_name_dict[target_type], "w", encoding="utf-8") as f:
        f.write(hearder_label_dict[target_type])
        f.write(sec_headers_label_dict[target_type])
        if target_type == 1 or target_type == 2:
            for t in zip(paras[0], paras[1], paras[2]):
                new_row = f"{trans_date(t[0])} |  {trans_date(t[1])} |  {t[2]:6.3f}" + "\n"
                f.write(new_row)
        else:
            for t in zip(paras[0], paras[1], paras[2], paras[3]):
                new_row = f"{trans_date(t[0])} |  {trans_date(t[1])} |  {t[2]:10.3f} |  {t[3]:10.2f}%" + "\n"
                f.write(new_row)
        f.write("end")

def format_tle_line1(line1: str) -> str:
    """
    Format the first line of the TLE
    """
    paras = [x for x in line1.split(' ') if x != '']
    line1 = list(" ") * 69
    line1[0] = '1'
    line1[7-len(paras[1]) + 1 :8] = list(paras[1])
    line1[9: 9+len(paras[2])] = list(paras[2])
    line1[18: 18+len(paras[3])] = list(paras[3])
    line1[42-len(paras[4]) + 1 :43] = list(paras[4])
    line1[51-len(paras[5]) + 1 :52] = list(paras[5])
    line1[60-len(paras[6]) + 1 :61] = list(paras[6])
    line1[62] = paras[7]
    line1[68-len(paras[8]) + 1 :69] = list(paras[8])

    line1 = "".join(line1)
    return line1

def format_tle_line2(line2: str) -> str:
    """
    Format the second line of the TLE
    """
    paras = [x for x in line2.split(' ') if x != '']
    line2 = list(" ") * 69
    line2[0] = '2'
    line2[6-len(paras[1]) + 1 :7] = list(paras[1])
    line2[15-len(paras[2]) + 1 :16] = list(paras[2])
    line2[24-len(paras[3]) + 1 :25] = list(paras[3])
    line2[32-len(paras[4]) + 1 :33] = list(paras[4])
    line2[41-len(paras[5]) + 1 :42] = list(paras[5])
    line2[50-len(paras[6]) + 1 :51] = list(paras[6])
    line2[52:69] = list(paras[7])

    line2 = "".join(line2)

    return line2


def format_tle(tle1: str, tle2: str) -> (str, str):
    """
    Complete TLE formatting
    """
    return format_tle_line1(tle1), format_tle_line2(tle2)

