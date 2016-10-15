##Python 学习（二） -- 初试抓取动车事件表

###没图没真相：
![这里写图片描述](http://img.blog.csdn.net/20161015234934915)

###确定需求
- 查询某日A到B地的列车班次，显示时间、地点、历时等信息
- 通过：Python3 run_railway.py [-gdtkz] \<from\> \<to\> \<date\> 调用查询

###数据分析
![这里写图片描述](http://img.blog.csdn.net/20161015235103056)

1.通过分析12306网站查询获取Json数据，格式：

```java
https://kyfw.12306.cn/otn/lcxxcx/query?purpose_codes=ADULT&queryDate={DATE}&from_station={FROM}&to_station={TO}
```
2.由于网站查询的地点是通过字母标识来实现的，而我们的查询格式是通过拼音来实现的，通过分析一下网址可以获取到标识：

```java
https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.8955
```
3.有了以上数据的支持，接下来就可以编码了。

###功能实现
1.首先需要引入三个支持包：

```python
# docopt __doc__获取
# requests 网络请求
# prettytable 表格绘制
pip3 install docopt,requests,prettytable
```

2.解析 \_\_doc__

```python
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
```

3.首先获取到查询地点对应的key,例如： beijing-->BJ ； shanghai-->SHH

```python
# 创建搜索文件的key/value,保存在一个txt文件方便获取
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
```

4.搭建显示需要的表格

```python
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
```

5.对数据进行加载，大功告成

```python
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
```

###初次尝试，欢迎issues和提需求
https://github.com/GHdeng/RailwayStation
