from pyquery import PyQuery as pq
from collections import OrderedDict
import pandas as pd
import multiprocessing
from datetime import datetime

def url_get(domain):
    url_list = []
    for i in range(0,1000): #4000
        main_url = domain+'/?page='+str(i)
        q = pq(main_url)
        url_nodes = q('h2 a')
        for node in url_nodes:
            url = domain +str(pq(node).attr('href'))
            url_list.append(url)
        if i % 50 == 0:
            print(i,'is done.')
    return url_list

def element_parse(news_url):
    newsq = pq(news_url)
    info = OrderedDict()
    info['title'] = newsq('.article-list .title').text()
    info['author'] = newsq('.submitted_username a').text()
    info['time'] = newsq('.submitted_datetime span').text()
    info['content'] = newsq('.content p').text()
    info['click'] = newsq('.selectorgadget_selected').text()
    info['share'] = newsq('.active .active').text()
    info['tags'] = newsq('.taxonomy-links').text()
    return info
    
if __name__ == '__main__':
    domain = 'http://www.zerohedge.com'
    now = datetime.now()
    
    url_list = url_get(domain)
    scraped_data = []
    
    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    results = pool.map(element_parse,url_list)
    
    n = 0
    for each in results:
        scraped_data.append(each)
        n += 1

    later = datetime.now()
    diff = later - now
    
    print('總共爬取',n,'個案子，花費',str(round(diff.seconds/60.0,2)),'分鐘')  #總共爬取 20000 個案子，花費 76.33 分鐘
    data = pd.DataFrame(scraped_data)
    data.to_csv(r'C:\Users\GN1504301\Desktop\zerohedge.csv',encoding='utf-8',index=None)
