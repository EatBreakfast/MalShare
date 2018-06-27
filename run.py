import datetime
import os
import json

start = '2018-06-21'
end = '2018-06-22'

date_start = datetime.datetime.strptime(start, '%Y-%m-%d')
date_end = datetime.datetime.strptime(end, '%Y-%m-%d')

sample_f = open('samples.txt', 'w')
while date_start < date_end:
    date_start += datetime.timedelta(days=1)
    date_str = date_start.strftime('%Y-%m-%d')
    print(date_str)
    pass

sample_f.close()
