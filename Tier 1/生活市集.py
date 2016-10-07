# -*- coding: utf-8 -*-
"""
Created on Sun Sep 18 00:03:22 2016

@author: GN1504301
"""

from collections import OrderedDict
import pandas as pd
from datetime import datetime,date
from pyquery import PyQuery as pq
import pymysql
import multiprocessing
import re

def get_url(initial_url):
    q = pq(initial_url)
    product_url = []
    for deal in q('.deals a') :
        product_url.append('https://www.buy123.com.tw' + pq(deal).attr('href'))
    return product_url

def get_num(text):
    new_text=''
    if text:
        new_text = re.findall(r'[^\u4e00-\u9fa5]', text)
        new_text = ''.join(new_text)               
        if '$' in new_text:
            new_text = new_text.replace('$','')
        new_text = new_text.strip()
        if ')' in new_text:
            new_text = new_text.split(')')[0]
            new_text = new_text.replace('(','')
        if '】' in new_text:
            new_text = new_text.split('】')[0]
            new_text = new_text.replace('【','')
    return new_text
    
def product_parse(product_url,date = date.today()):
    q = pq(product_url)
    project_dict = OrderedDict()
    project_dict['date'] = date
    project_dict['name'] = q('.deal-title h1').text()
    project_dict['price'] = get_num(q('#price').text())
    project_dict['sold'] = get_num(q('.deal_sold_count').text())
    try:    
        project_dict['ori_price'] = get_num(q('.content_wapper font').eq(0).text())
    except:
        project_dict['ori_price'] = 'na'
        
    return project_dict
   
if __name__ == '__main__':
    url = 'https://www.buy123.com.tw/?sid=gs_123&from=gs_123&gclid=Cj0KEQjwpNm-BRCJ3rDNmOuKi9IBEiQAlzDJH-sTkLAu4fkNHh4_NHrg-zfJ5oNLjXnBSzVnt13-pEcaAmsY8P8HAQ'
    now = datetime.now()
    product_url = get_url(url)
    scraped_data = []
    
    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    results = pool.map(product_parse,product_url)
    n = 1 
    for each in results:
        scraped_data.append(each)
        n += 1       

    later = datetime.now()
    diff = later - now
    print('總共爬取',n,'個案子，花費',str(round(diff.seconds/60.0,2)),'分鐘')  #6.93分鐘
    df = pd.DataFrame(scraped_data)

    #將資料存到 mysql中    
    conn= pymysql.connect(host='localhost', port=3306,user='root',passwd='',db ='life',charset='utf8')
    df.to_sql(con=conn, name='sales', if_exists='append', flavor='mysql')
    conn.close()

