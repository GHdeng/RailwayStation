#!/usr/bin/python3
# -*- coding: UTF-8 -*-

#Example:
#    python3 run_railway.py beijing shanghai 2016-10-14


"""
Train tickets query via command-line.

Usage:
    tickets [-gdtkz] <from> <to> <date>

Options:
    -h,--help       显示帮助信息
    -g              高铁
    -d              动车
    -t              特快
    -k              快车
    -z              直达

Example:
    tickets beijing shanghai 2016-10-14
"""

from docopt import docopt
from pprint import pprint
import os
import time
import re
import requests

from prettytable import PrettyTable

# 修改 出发/到达站 出发/到达时间 的颜色
def colored(color, text):
        table = {
            'red': '\033[91m',
            'green': '\033[92m',
            # no color
            'nc': '\033[0m'
        }
        cv = table.get(color)
        nc = table.get('nc')
        return ''.join([cv, text, nc])

# 搭建表格
class TrainCollection(object):
    header = '显示车次 出发/到达站 出发/到达时间 历时 一等坐 二等坐 软卧 硬卧 硬座'.split()

    def __init__(self, rows):
        self.rows = rows

    def _get_duration(self, row):
        """
        获取车次运行时间
        """
        duration = row.get('lishi').replace(':', 'h') + 'm'
        if duration.startswith('00'):
            return duration[4:]
        if duration.startswith('0'):
            return duration[1:]
        return duration

    @property
    def trains(self):
        for row in self.rows:
            train = [
                # 车次
                row['station_train_code'],
                # 出发、到达站
                '\n'.join([colored('green', row['from_station_name']),colored('red', row['to_station_name'])]),
                '\n'.join([colored('green', row['start_time']),colored('red', row['arrive_time'])]),
                # 历时
                self._get_duration(row),
                # 一等坐
                row['zy_num'],
                # 二等坐
                row['ze_num'],
                # 软卧
                row['rw_num'],
                # 软坐
                row['yw_num'],
                # 硬坐
                row['yz_num']
            ]
            yield train

    def pretty_print(self):
        pt = PrettyTable()
        # 设置每一列的标题
        pt._set_field_names(self.header)
        for train in self.trains:
            pt.add_row(train)
        print(pt)

# 创建搜索文件的key/value
def create():
    url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.8955'

    r = requests.get(url, verify=False)

    stations = re.findall(r'([A-Z]+)\|([a-z]+)', r.text)

    stations = dict(stations)

    # zip就是把2个数组糅在一起
    # x=[1, 2, 3, 4, 5 ]
    # y=[6, 7, 8, 9, 10]
    # zip(x, y)就得到了
    # [(1, 6), (2, 7), (3, 8), (4, 9), (5, 10)]
    stations = dict(zip(stations.values(), stations.keys()))
    # pprint(stations.values())
    # pprint(stations, indent=4)
    file = open('stations.txt', mode='w', encoding='utf-8')
    file.write(str(stations))
    file.close()


def client():
    """
    command-line interface
    """
    arguments = docopt(__doc__)
    # print(arguments)

    file = open('stations.txt','r')
    stations = eval(file.read())

    from_station = stations.get(arguments['<from>'])
    to_station = stations.get(arguments['<to>'])
    date = arguments['<date>']

    url = 'https://kyfw.12306.cn/otn/lcxxcx/query?purpose_codes=ADULT&queryDate={}&from_station={}&to_station={}' \
        .format(date, from_station, to_station)
    r = requests.get(url, verify=False)
    # pprint(r.json())
    rows = r.json()['data']['datas']
    trains = TrainCollection(rows)
    trains.pretty_print()


if __name__ == '__main__':
    create()
    while True:
        client()
        time.sleep(60)
        #i = os.system('cls') #window 下清屏
        i = os.system('clear')
