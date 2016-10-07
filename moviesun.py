# -*- coding: utf-8 -*-
"""
Created on Thu Sep 22 00:14:35 2016

@author: GN1504301
"""

from bs4 import BeautifulSoup as bs
import requests
import pickle
import re

def get_seriesname(initial_url):
    result = requests.get(initial_url)
    soup = bs(result.text, "lxml")
    series_name = []
    tags = ['.home-8 a','.home-9 a','.home-10 a']
    for tag in tags:
        for category in soup.select(tag):
            name = category.text.split(' ')[1:]
            text = text_preprocessing(name)
            series_name.append(text)
            
    return series_name
    
def text_preprocessing(text):
    text =' '.join(x for x in text)
    new_text = re.findall(r'[^\u4e00-\u9fa5]', text)
    new_text = ''.join(new_text)
    new_text = new_text.lstrip()
    drop = set("()/")
    filterpunt = ''.join(filter(lambda x : x not in drop , new_text))
    
    return filterpunt

if __name__ == '__main__':
    url = 'http://moviesunusa.net/'
    series_name = get_seriesname(url)
    print(series_name)
    with open(r'E:\IpythonNotebook\美劇盒\moviesun_series_name','ab') as f:
        pickle.dump(series_name,f)
    f.close()
