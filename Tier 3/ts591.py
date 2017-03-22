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
import googlemaps

class Ts591:   
    def __init__(self,stations,htype,minp,maxp,sales,b1,dist,ping): 
        '''
        stations : str , mrt station names want to search
        htype : int , 0 = 不限 , 1 = 整層 , 2 = 獨立套房 , 3 = 分租套房
        minp : int , minimum rent 
        maxp : int , maximun rent accepted
        sales : int , 0 = remove 仲介
        b1 : int , 0 = remove B1 & 頂加
        dist : int , minimum linear distant to mrt
        ping : int , minimum 坪數 accepted
        '''
        self.station_name = stations
        self.htype = htype
        self.minp = minp
        self.maxp = maxp
        self.sales = sales
        self.b1 = b1
        self.dist = dist
        self.ping = ping

    def all_mrtcode(self):
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
    
    def get_mrt_code(self):
        #給定捷運站名稱,自動找出代碼
        station_df = self.all_mrtcode()
        
        station_want = []    
        for each in self.station_name.split(','):
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
    
    def request_all(self):
        #給定代碼,爬取相對應頁數
        code_final = self.get_mrt_code()
        request_url = 'https://rent.591.com.tw/home/search/rsList?is_new_list=1&type=1&kind='+str(self.htype)+'&searchtype=4&region=1&mrt=1&mrtcoods='+str(code_final)+'&rentprice='+str(self.minp)+','+str(self.maxp) #&kind=1
        res = requests.get(request_url)
        data = json.loads(res.text)
        print('json loads over.')
        limit = int(data['records'])
        page = (limit // 30) + 1  
    
        request_all_url = []    
        for j in range(0,page):
            url = request_url + '&firstRow=' + str(j*30) + '&totalRows='+ str(limit)
            request_all_url.append(url)
        
        print(len(request_all_url),'pages total')
        
        return request_all_url
    
    def url_info(self):
        #爬取網頁內容      
        request_all_url = self.request_all()
        scraped_data = []    
        for each in request_all_url:
            res = requests.get(each)
            time.sleep(2)
            data = json.loads(res.text)
            lenth = len(data['data']['data'])
            for i in range(0,lenth):
                dict591 = OrderedDict()
                location = data['data']['data'][i]
                '''
                if (self.htype == 0) & (self.htype == 1) :
                    match_room = re.match(r'(?P<room>[\d])\D(?P<livingroom>[\d])\D(?P<toilet>[\d])',location['layout'])
                    try:
                        dict591['rooms'] = int(match_room.groupdict()['room'])
                        dict591['livingroom'] = match_room.groupdict()['livingroom']
                        dict591['toilet'] = match_room.groupdict()['toilet']
                    except:
                        continue
                '''
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
        
        df = pd.DataFrame(scraped_data)
            
        return df
    
    def clean_dataframe(self):
        
        df = self.url_info()
        week_ago = (datetime.now() - timedelta(days=7)).date()
        df.time = pd.to_datetime(df.time)
        df = df[df.time > week_ago]
        df = df[df.nearby_dis <= self.dist] 
        if self.sales == 0:
            df = df[df.broker != "仲介"]
        if self.b1 == 0:
            df = df[df.floor != "頂樓加蓋"]
            df = df[df.floor != "B1"]
        '''
        df = df[df.rooms >= self.room]
        '''
        df = df[df.ping >= self.ping]
        df = df[df.photoNum > 2]
        df2 = df.reset_index(drop=True)
        
        return df2

    def get_no_item(self):
        hdr = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36','Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
           'Connection': 'keep-alive'}
        
        final_df = self.clean_dataframe()
        no_list = []
        n = 0
        for each in final_df.house_url:
            try:
                no_dict = {}
                q = pq(each,headers=hdr)
                '''
                no_dict['balcony'] = int(''.join(re.findall(r'[\d]+',q('div.detailInfo.clearfix > ul > li:nth-child(1)').text().split('衛')[1])))
                '''
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
        result_df = pd.concat([final_df, no_df], axis=1, join_axes=[final_df.index])
        
        return result_df
    
    def last_clean(self):
        result_df = self.get_no_item()
        result_df = result_df[result_df.amount < 6 ]
        '''
        result_df = result_df[result_df.balcony >= self.balcony ]
        '''
        result_df = result_df[result_df.facility_len > 3]
        result_df = result_df[['title','address','house_url','price','nearby','nearby_dis','ping','floor']] #,'no_item'
        result_df = result_df.rename(columns={'title':"標題","house_url":"網址","nearby":"捷運站","nearby_dis":"距離捷運站","ping":"坪數","floor":"樓層"}) #,"no_item":"未配備家電"
        result_df2 = result_df.sort_values(by='price')
        result_df2 = result_df2.reset_index(drop=True)
        parse_date =  date.today()
        result_df2['parse_date'] = parse_date
        
        return result_df2
    
    def google_map(self):
        gmaps = googlemaps.Client(key='AIzaSyAE0UIvpeqrVti3j4pZiNgofHFPHzrKI0Y')
        gplace = googlemaps.Client(key ='AIzaSyDXQ-A5bi8BBBcz3EH3IgBcWd1rbLw0JZc')
        gcode = googlemaps.Client(key ='AIzaSyBSaBEiyxn7SO8qhq8-KVWOD8XSY1BGZf8')
        
        result_df2 = self.last_clean()
        address_series = pd.Series(result_df2['address'])
        info_list = []
        for each in range(len(address_series)):
            info = {}
            geocode_result = gcode.geocode(address_series[each])[0]['geometry']['location']
            mrt_result = gplace.places_nearby(location = geocode_result,keyword ='捷運',rank_by='distance',language='zh-TW')['results'][0]['name']
            info['nearest_mrt'] = mrt_result
            temp = gmaps.distance_matrix(origins = address_series[each],destinations = mrt_result,mode = 'walking',language='zh-TW')
                
            json_loc = temp['rows'][0]['elements'][0]
            info['mrt_distance'] = json_loc['distance']['text']
            info['mrt_walktime'] = json_loc['duration']['text']
            
            info_list.append(info)
            
        gg_frame = pd.DataFrame(info_list)
        gg_house = result_df2.join(gg_frame)
            
        return gg_house
        
    
if __name__ == '__main__':  
    
    stations_hwau = "古亭站,大安站,六張犁站,萬隆站,科技大樓,中正紀念堂,永安市場"  #麟光站,辛亥站
    house_hwua = Ts591(stations_hwau,htype = 1,minp = 10000,maxp = 20000,sales = 0,b1 = 0,dist = 700,ping = 16)
    gg_house_hwua = house_hwua.google_map()
    gg_house_hwua.to_csv(r'C:\Users\GN1504301\Desktop\gg_house_hwua.csv',index = None)
     
    stations_shin = "南港展覽館,南港軟體園,東湖站"    
    house_shin = Ts591(stations_shin,htype = 0,minp = 6000,maxp = 12000,sales = 0,b1 = 0,dist = 700,ping = 7)
    gg_house_shin = house_shin.google_map()
    gg_house_shin.to_csv(r'C:\Users\GN1504301\Desktop\gg_house_shin.csv',index = None)
    
    
    
        
        