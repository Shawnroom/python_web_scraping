# -*- coding: utf-8 -*-

from datetime import datetime
from pyquery import PyQuery as pq
import multiprocessing
from collections import OrderedDict
import json
import requests
import pandas as pd
from selenium import webdriver

def page_limit():
    request_url = 'http://www.taaze.tw/beta/viewDataAgent.jsp?a=05&d=00&l=0&t=11&c=00&k=03&startNum=540&endNum=569&sortType=2&shc=&shn=&shd=&discNo=&classNo='
    res = requests.get(request_url)
    data = json.loads(res.text)
    total_item = int(data['totalsize'])
    page = (total_item // 30) + 1
    
    return page

def book_url(page=2):
    list_url = []
    for i in range(1,page+1): 
        driver = webdriver.PhantomJS(r'C:\Users\GN1504301\Desktop\phantomjs-2.1.1-windows\phantomjs-2.1.1-windows\bin\phantomjs.exe')
        
        domain = 'http://www.taaze.tw/container_snd_actview.html?t=11&k=03&d=00&c=00&l=0&a=05#AA'+str(i)+'%2C2%2C30%2C2'
        driver.get(domain)
        
        location = driver.find_elements_by_css_selector('.bookview_result_b .bookview_result_m .linkA a')
        for each in location:
            url = each.get_attribute('href')
            list_url.append(url)

        driver.close()
            
    return list_url
    
def info_parse(url):
    book_dict = OrderedDict()
    q = pq(url)
    book_dict['url'] = url
    book_dict['author'] = q('#prodInfo3 > li:nth-child(1) > span > span > a').text()
    #以此類推，利用靜態爬蟲爬想要的項目
    
    return book_dict
    
if __name__ == '__main__':
    
    now = datetime.now()
    page = page_limit()
    list_url = book_url() #page
    
    scraped_data = []

    pool = multiprocessing.Pool(4)
    data = pool.map(info_parse,list_url)
    
    n = 1 
    for each in data:
        scraped_data.append(each)
        n += 1       
    
    later = datetime.now()
    diff = later - now
    print('總共爬取',n,'個案子，花費',str(round(diff.seconds/60.0,2)),'分鐘') 

    
    df = pd.DataFrame(scraped_data)  
    print(df[0:3])

    
    
        