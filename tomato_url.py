# -*- coding: utf-8 -*-

from datetime import datetime
from pyquery import PyQuery as pq
import multiprocessing
import pickle

def get_seriesurl(series_name):

    #proxy = {'http': 'http://114.42.5.242:808','http': 'http://111.253.90.141:808'}    
    #找每齣美劇每一季的 review url
    domain ='https://www.rottentomatoes.com'

    series_name =  ''.join(x for x in series_name)
    series_name_text = series_name.replace(' ','_')
    series_name_text = series_name_text.lower()
    url = domain +  '/tv/' + str(series_name_text)
    
    try:
        q = pq(url)
        return get_review_url(q,url)
        
    except:
        series_name_text = series_name_text.replace('_','%20')
        search_url = domain + '/search/?search=' + series_name_text
        search_q = pq(search_url)
        tv_location = search_q('.details a') #需在改
        tv_url = domain + str(pq(tv_location).attr('href'))
        try:
            q2 = pq(tv_url)
            return get_review_url(q2,tv_url)
        
        except:
            pass            
            

def get_review_url(q,url):
    
    domain ='https://www.rottentomatoes.com'
    
    try:
        url.index('tv')    
    except:
        pass       
        
    site_url= []
    single_url = []
    
    if len(q('strong a')) > 0:
        for link in q('strong a'):              
            if 'tv' in pq(link).attr('href'):
                site = domain + str(pq(link).attr('href')) + 'reviews'
                try:
                    site.index("s0")
                    site_url.append(site)
                except:
                    continue
        return site_url
                    
    else:
        site_simple = url + 'reviews'
        try:
            site_simple.index("s0")
            single_url.append(site_simple)
            return single_url
            
        except:
            pass    

def unlist(results):
    series_mainurl=[]
    for url in results:
        if url is not None:
            for each in url:
                series_mainurl.append(each)    
    
    return series_mainurl
    
    
if __name__ == '__main__':
    now = datetime.now()
    series_name = pickle.load(open(r'E:\IpythonNotebook\美劇盒\moviesun_series_name', 'rb'))

    pool = multiprocessing.Pool(3)
    results = pool.map(get_seriesurl,series_name)
    series_mainurl = unlist(results)

    with open (r'E:\IpythonNotebook\美劇盒\rottentomato_url24','ab') as f:
        pickle.dump(series_mainurl,f)
        f.close()

    later = datetime.now()
    diff = later - now
    print('花費',str(round(diff.seconds/60.0,2)),'分鐘')
    