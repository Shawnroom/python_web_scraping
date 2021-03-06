# -*- coding: utf-8 -*-

from datetime import datetime,timedelta,date
from collections import OrderedDict
import pandas as pd
import numpy as np
import json
import requests
import re
import time
from pyquery import PyQuery as pq
import pymysql

def all_mrtcode():
    #爬取所有捷運站名稱與對應代碼
    request_url = 'https://rent.591.com.tw/static/public/list/mapsubway.js?v=de6935c65f' 
    res = requests.get(request_url)
    text = res.text
    pattern = re.compile(r'''[name\":]+
        (?P<name>[\u4e00-\u9fa5]+)\"[^d]+[d\":]+
        (?P<code>[\d]+)        
        ''',re.X)
        
    list_station = [] 
    
    for match in pattern.finditer(text):
        if match.groupdict() not in list_station:
            list_station.append(match.groupdict())
        
    station_df = pd.DataFrame(list_station)
    
    return station_df

def get_mrt_code(station_df):
    #給定捷運站名稱,自動找出代碼
    station_name = "南港展覽館,南港軟體園"
    #永安市場,七張站,麟光站,辛亥站
    
    station_want = []    
    for each in station_name.split(','):
        station_want.append(each)
        
    code_list = []    
    for every in station_want:
        try:        
            want = station_df[station_df.name == every]
            code = int(want.code)
            code_list.append(str(code))
            print(every,"進行中,code為:",code)
        except:
            print('查無此捷運站名稱：',every)

        code_final = ','.join(code_list)
        
    return code_final

def request_all(code_final):
    #給定代碼,爬取相對應頁數
    request_url = 'https://rent.591.com.tw/home/search/rsList?is_new_list=1&type=1&kind=2&searchtype=4&region=1&mrt=1&mrtcoods='+str(code_final)+'&rentprice=2'
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
    #爬取網頁內容
    hdr = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36','Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
       'Connection': 'keep-alive'}
    
    scraped_data = []    
    for each in request_all_url:
        res = requests.get(each,headers=hdr)
        time.sleep(2)
        data = json.loads(res.text)
        lenth = len(data['data']['data'])
        for i in range(0,lenth):
            dict591 = OrderedDict()
            location = data['data']['data'][i]
            match_room = re.match(r'(?P<room>[\d])\D(?P<livingroom>[\d])\D(?P<toilet>[\d])',location['layout'])
            try:
                dict591['rooms'] = int(match_room.groupdict()['room'])
                dict591['livingroom'] = match_room.groupdict()['livingroom']
                dict591['toilet'] = match_room.groupdict()['toilet']
            except:
                continue
            
            dict591['time'] = location['ltime'].split(' ')[0]
            dict591['house_url'] = 'https://rent.591.com.tw/rent-detail-' + str(location['houseid']) + '.html'
            dict591['floor'] = location['floorInfo'].split("：")[1].split("/")[0]
            dict591['ping'] = location['area']
            dict591['title'] = location['address_img_title']
            dict591['address'] = location['section_name'] + location['street_name'] + location['alley_name']            
            dict591['post_time'] = location['posttime']
            dict591['price'] = location['price']
            dict591['nearby'] = location['search_name']
            dict591['nearby_dis'] = location['distance']
            dict591['broker'] = location['nick_name'].split(' ')[0]
            dict591['photoNum'] = int(location['photoNum'])
            
            scraped_data.append(dict591)
        
    return scraped_data

'''    
def clean_dataframe(df):
   # week_ago = (datetime.now() - timedelta(days=7)).date()
    #df.time = pd.to_datetime(df.time)
    #df = df[df.time > week_ago]
    df = df[df.nearby_dis < 800] 
    df = df[df.broker != "仲介"]
    df = df[df.floor != "頂樓加蓋"]
    df = df[df.floor != "B1"]
    #df = df[df.rooms > 1]
    #df = df[df.ping > 15]
    df = df[df.photoNum > 2]
    df = df.reset_index(drop=True)
    
    return df     

def get_no_item(df):
    hdr = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36','Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
       'Connection': 'keep-alive'}
       
    no_list = []
    n = 0
    for each in final_df.house_url:
        try:
            no_dict = {}
            q = pq(each,headers=hdr)
            no_dict['balcony'] = int(''.join(re.findall(r'[\d]+',q('div.detailInfo.clearfix > ul > li:nth-child(1)').text().split('衛')[1])))
            no_dict['no_item'] = q('.no').parent('li').text()     
            no_dict['amount'] = len(no_dict['no_item'].split(' '))
            facility = q('.facility.clearfix').text()
            no_dict['facility_len'] = len(facility)

            no_list.append(no_dict)
            time.sleep(2)
        except:
            n += 1
            print(each,'is not available  total:',n)
            continue
        
    no_df = pd.DataFrame(no_list)
    
    return no_df
    
def last_clean(result_df):
    result_df = result_df[result_df.amount < 6 ]
    #result_df = result_df[result_df.balcony > 0 ]
    #result_df = result_df[result_df.facility_len > 3]
    result_df = result_df[['title','address','house_url','price','nearby','nearby_dis','ping','floor','no_item']]
    result_df = result_df.rename(columns={'title':"標題",'address':"地址","house_url":"網址","nearby":"捷運站","nearby_dis":"距離捷運站","ping":"坪數","floor":"樓層","no_item":"未配備家電"})
    result_df2 = result_df.sort_values(by='price')
    result_df2 = result_df2.reset_index(drop=True)
    parse_date =  date.today()
    result_df2['parse_date'] = parse_date
    
    return result_df2
'''    
if __name__ == '__main__':
    now = datetime.now()
    station_df = all_mrtcode()
    code_final = get_mrt_code(station_df)
    
    request_all_url = request_all(code_final)
    data_all = url_info(request_all_url)
    
    later = datetime.now()
    diff = later - now
    
    df = pd.DataFrame(data_all)
    '''
    final_df = clean_dataframe(df)
    no_df = get_no_item(final_df)
    result_df = pd.concat([final_df, no_df], axis=1, join_axes=[final_df.index])
    
    result_df2 = last_clean(result_df)
    '''
    df.to_csv(r'C:\Users\GN1504301\Desktop\ts591.csv')
    
    
    print('總共花費',str(round(diff.seconds/60.0,2)),'分鐘') 
    
    
    
        
        