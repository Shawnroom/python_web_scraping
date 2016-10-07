# -*- coding: utf-8 -*-

from datetime import datetime
import json
import requests
from pyquery import PyQuery as pq
import multiprocessing
from collections import OrderedDict
import pandas as pd
import pymysql

def page_boundary():
    # 頁面資訊藏在get請求中，若網頁已到底，則返回的json中'html'變數為空
    request_url = 'https://crazymike.tw/proList4/index/ch-5/disp-RNDESC/page-'
    n = 0
    for numbers in range(1,250):
        url = request_url + str(numbers)
        q = requests.get(url)
        data = json.loads(q.text)
        if data['html'] != '':
            n += 1
        else:
            break
            
    return n
    
def get_item_url(n):
    #抓取個別商品url
    domain = 'https://crazymike.tw/index/ch-5/page-'
    item_url_list = []
    for i in range(1,n+1):    
        url = domain + str(i)
        try:        
            q = pq(url)
            page_info = q('.lnkList.trace')
            for each in page_info:
                item_url = pq(each).attr('href')
                if item_url not in item_url_list:
                    item_url_list.append(item_url)
                else:
                    continue
        except:
            print('page',i,'is not good.')
            
    return item_url_list

def element_parse(item_url):
    
    q = pq(item_url)
    ele_dict = OrderedDict()
    ele_dict['category'] = q('.navi a').text()
    ele_dict['name'] = q('#item_name').text()[0:20]
    ele_dict['ori_price'] = q('s').text()
    ele_dict['price'] = q('.item_price_text').text()
    try:
        ele_dict['love'] = q('.love > div').text()
    
    except:
        try:
            ele_dict['love'] = q('.purchase_count > .number').text()
        except:
            ele_dict['love'] = 'na'
    
    return ele_dict
    
    
    

if __name__ == '__main__':
    
    now = datetime.now()
    scraped_data = []
    
    n = page_boundary()
    item_url_list = get_item_url(n)
    pool = multiprocessing.Pool(4)
    results = pool.map(element_parse,item_url_list)
    
    n = 1 
    for each in results:
        scraped_data.append(each)
        n += 1       
        
    later = datetime.now()
    diff = later - now
    print('總共爬取',n,'個案子，花費',str(round(diff.seconds/60.0,2)),'分鐘') 
    
    df = pd.DataFrame(scraped_data)
'''
    conn= pymysql.connect(host='localhost', port=3306,user='root',passwd='',db ='life',charset='utf8')
    df.to_sql(con=conn, name='crazy', if_exists='replace', flavor='mysql')
    conn.close()
'''
