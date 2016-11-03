# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup as bs
import pandas as pd
import codecs
import os

# 檔案路徑
xml_dir = os.path.abspath('.')

for filename in os.listdir(xml_dir):
    if '.xml' in filename:
        print ("Loading: %s" % filename)
        loadFile = codecs.open(os.path.join(xml_dir, filename),'rb',"utf-8")
        file_1 = loadFile.read()
        soup = bs(file_1)
        loadFile.close()
        
        inputTags = soup.findAll(attrs={"isreviewed" : "true"})
    
        data = []
        for tag in inputTags:
            dict_mod = {}
            try:
                dict_mod['source'] = tag.find('source').text
                dict_mod['target'] = tag.find('target').text
                dict_mod['modify'] = tag.find(attrs={"match-quality" : "review"}).text
                dict_mod['comment'] = tag.find('comment').text
                data.append(dict_mod)
            except:
                pass
            
        data_DF = pd.DataFrame(data)
        data_DF = data_DF[['source','target','modify','comment']]
        
        filename_mod = str(filename.split(".")[0])
        data_DF.to_csv(xml_dir +'/' + filename_mod +'.csv',index=None)
        
    else:
        continue

        
    
    
