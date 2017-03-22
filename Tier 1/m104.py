# -*- coding: utf-8 -*-
from datetime import datetime,timedelta
from collections import OrderedDict
import multiprocessing
import pandas as pd
import requests
import re
from pyquery import PyQuery as pq
import pymysql

def find_page():
    #找出總共有幾頁
    page_domain = 'https://www.104.com.tw/jobbank/joblist/joblist.cfm?jobsource=n104bank1&ro=0&keyword=資料科學&order=1&asc=0&page='
    page_url = page_domain + str(2) + '&psl=N_B'
    q = pq(page_url)
    page_total = int(''.join(re.findall(r'[\d]+',q('.next_page #loadDone_3').text().split('，')[1])))
    
    return page_total
    
def all_url(page_total):
    #每頁的工作機會url
    domain = 'http://www.104.com.tw'
    page_domain = 'https://www.104.com.tw/jobbank/joblist/joblist.cfm?jobsource=n104bank1&ro=0&keyword=資料分析&order=1&asc=0&page='
    all_urls_list = []
    page_list = []
    for i in range(1,page_total+1):
        urls = page_domain + str(i) + '&psl=N_B'
        q = pq(urls)
        urls_node = q('.line_bottom[itemtype="http://schema.org/JobPosting"] .job_name a')
        for each in urls_node:
            each_url = domain + str(pq(each).attr('href'))
            all_urls_list.append(each_url)
            page_list.append(i)
        print(i,len(all_urls_list))
        
        s1 = pd.Series(all_urls_list,name = 'url')
        s2 = pd.Series(page_list,name = 'page')
        
        s3 = pd.concat([s2,s1],axis = 1 ,join_axes=[s1.index])  
            
    return s3
    
def element_parse(url):
    element = OrderedDict()
    try:
        element = OrderedDict()
        q = pq(url)
        element['url'] = url
        element['update_time'] = re.sub(r'[：\u4e00-\u9fa5]+',"",q('time.update').text())
        jobname = q('.main .center h1').text().split(' ')[0]
        element['jobname'] = jobname
        element['company'] = q('.company a.cn').text()
        element['competitors'] = ''.join(re.findall(r'[^\u4e00-\u9fa5]+',q('.function .sub img[src]').attr('alt').split(' ')[1]))
        element['job_content'] = q('.main .info .content p:nth-child(1)').text()
        element['job_category'] = q('.main .info .content dd.cate').text().split(' ')[0]
        
        q2 = q('.main > section:nth-child(2) .content')
        element['experience'] = q2('dd:nth-child(4)').text()
        element['degree'] = q2('dd:nth-child(6)').text()
        element['department'] = q2('dd:nth-child(8)').text()
        element['tools'] = q2('dd:nth-child(12)').text()
        element['skills'] = q2('dd:nth-child(14)').text()
        element['others'] = q2('dd:nth-child(16)').text()
        
        '''
        company_cate_url = q('.company a.cn').attr('href')
        company_q = pq(company_cate_url)
        company_cate_loc = company_q('#cont_main > div:nth-child(2) > dl > dd:nth-child(2)').text()
        company_cate_loc = company_cate_loc.encode('utf8')
        '''
    except:
        pass
  
    return element
    
if __name__ == '__main__':
    now = datetime.now()    
    
    page_total = find_page()
    s3 = all_url(page_total)
    url_list = list(s3['url'])
    pool = multiprocessing.Pool(4)
    result = pool.map(element_parse,url_list)
    
    n = 0
    parse_data = []
    for each in result:
        parse_data.append(each)
        n += 1
        
    df = pd.DataFrame(parse_data)
    final_df = pd.merge(df,s3,on='url',how='inner')
    
    later = datetime.now()
    diff = later - now
    print('總共爬取',n,'個案子，花費',str(round(diff.seconds/60.0,2)),'分鐘') 
       
    final_df.to_csv(r'E:\IpythonNotebook\真104\m_0106.csv',encoding='utf-8',index=None)
