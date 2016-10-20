# -*- coding: utf-8 -*-

from datetime import datetime
from collections import OrderedDict
import pandas as pd
import json
import requests
import re
from pyquery import PyQuery as pq
import pymysql

def all_mrtcode():
    
    request_url = 'https://rent.591.com.tw/static/public/list/mapsubway.js?v=de6935c65f' 
    res = requests.get(request_url)
    text = res.text
    pattern = re.compile(r'''[name\":]+
        (?P<name>[\u4e00-\u9fa5]+)\"[^d]+[d\":]+
        (?P<code>[\d]+)        
        ''',re.X)
        
    list_station = [] 
    
    for match in pattern.finditer(text):
        list_station.append(match.groupdict())
        
    station_df = pd.DataFrame(list_station)
    
    return station_df

def get_mrt_code(station_df):
    
    station_name = "頂溪站,永安市場"
    
    station_want = []    
    for each in station_name.split(','):
        station_want.append(each)
        
    code_list = []    
    for every in station_want:
        try:        
            want = station_df[station_df.name == every]
            code = int(want.code)
            code_list.append(str(code))
        except:
            print('查無此捷運站名稱')

        code_final = ','.join(code_list)
        
    return code_final

def request_all(code_final):
    
    request_url = 'https://rent.591.com.tw/home/search/rsList?is_new_list=1&type=1&kind=0&searchtype=4&region=3&mrt=1&mrtcoods='+str(code_final)+'&kind=1&rentprice=10000,20000'
    res = requests.get(request_url)
    data = json.loads(res.text)
    limit = int(data['records'])
    page = (limit // 30) + 1  

    request_all_url = []    
    for j in range(0,page):
        url = request_url + '&firstRow=' + str(j*30) + '&totalRows='+ str(limit)
        request_all_url.append(url)
    
    return request_all_url
    
def url_info(request_all_url):
    hdr = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36','Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
       'Connection': 'keep-alive'}
    
    scraped_data = []    
    for each in request_all_url:
        res = requests.get(each,headers=hdr)
        data = json.loads(res.text)
        lenth = len(data['data']['data'])
        for i in range(0,lenth):
            dict591 = OrderedDict()
            location = data['data']['data'][i]
            dict591['time'] = location['ltime']
            dict591['house_url'] = 'https://rent.591.com.tw/rent-detail-' + str(location['houseid']) + '.html'
            dict591['floor'] = location['floorInfo'].split("：")[1]
            dict591['ping'] = location['area']
            dict591['address'] = location['fulladdress']
            dict591['rooms'] = location['layout']
            dict591['time'] = location['posttime']
            dict591['price'] = location['price']
            dict591['nearby'] = ''.join(re.findall(r'[\u4e00-\u9fa5]',location['distance_info']))
            dict591['nearby_dis'] = location['distance']
            dict591['broker'] = location['nick_name']
            
            #q = pq(dict591['house_url'],headers=hdr)
            #dict591['no_item'] = q('.no').parent('li').text()
            
            scraped_data.append(dict591)
        
    return scraped_data
    
if __name__ == '__main__':
    now = datetime.now()
    station_df = all_mrtcode()
    code_final = get_mrt_code(station_df)
    
    request_all_url = request_all(code_final)
    data_all = url_info(request_all_url)
    
    later = datetime.now()
    diff = later - now
    print('總共花費',str(round(diff.seconds/60.0,2)),'分鐘') 
    
    df = pd.DataFrame(data_all)
    
    conn= pymysql.connect(host='localhost', port=3306,user='root',passwd='',db ='life',charset='utf8')
    df.to_sql(con=conn, name='rent591', if_exists='replace', flavor='mysql')
    conn.close()
    
        
        