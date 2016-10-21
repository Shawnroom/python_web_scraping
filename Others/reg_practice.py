# -*- coding: utf-8 -*-

import re
import pandas as pd

target = '555-555-5555.'
pattern = r'\d{3}-\d{3}-\d{4}.'

def match_count(count,string):
    #返回count字數以上的string
    pattern = r"\w{"+str(count)+",}"
    match = re.findall(pattern,string)
    return match
    
target = email_address
pattren = r'[-_+\.\w\d]+@[\w\d]+\.[\w\d]+\.?[\w\d]+'
# set -> [] 在set中的元素都會被丕配 []+則代表一個以上 也可在後加{}限制長度

target = 'i want treeHouse not tree house not tree not house but treehouse ok?'
pattern = r"\b[trehous]{9}\b"
# \b限定單字開頭結尾
match = re.findall(pattern,target,re.I)
print(match)
# re.I代表配對時不區分大小寫

string = 'Perotto, Pier Giorgio'
names = re.match(r"(\w+), ([\w\s]+)",string)

string = '''Love, Kenneth, kenneth+challenge@teamtreehouse.com, 555-555-5555, @kennethlove
Chalkley, Andrew, andrew@teamtreehouse.co.uk, 555-555-5556, @chalkers
McFarland, Dave, dave.mcfarland@teamtreehouse.com, 555-555-5557, @davemcfarland
Kesten, Joy, joy@teamtreehouse.com, 555-555-5558, @joykesten'''

# get email and phone
contacts = re.search(r'(?P<email>[\w.+]+@[\w]+\.[\w]+\.?[\w]+),\s(?P<phone>\d{3}-\d{3}-\d{4})',string)
twitters = re.search(r'@[\w]+$',string,re.M)

string = '''Love, Kenneth: 20
Chalkley, Andrew: 25
McFarland, Dave: 10
Kesten, Joy: 22
Stewart Pinchback, Pinckney Benton: 18'''

players = re.match(r'''
    ^(?P<last_name>[\w\s]+),\s
    (?P<first_name>[\w\s]+):\s
    (?P<score>[\d]+)$
''',string,re.X|re.M)

#re.VERBOSE or re.X - flag that allows regular expressions to span multiple lines and comments. 但同時也會忽略空白" ",所以要空白要用\s
#re.M MULTIPLELINE,可用^與$表示每一行開始與結尾

text591 = 'ssubway[100]=[{"pid":"100","sid":"101","name":"南港展覽館","lat":"25.0552650","lng":"121.6173590","zoom":"16","nid":"4257"},{"pid":"100","sid":"102","name":"南港軟體園","lat":"25.0595760","lng":"121.6159210","zoom":"16","nid":"4314"},{"pid":"100","sid":"103","name":"東湖站","lat":"25.0671810","lng":"121.6114790","zoom":"16","nid":"4315"},'

# 將pattern compile後 可直接調用
match591 = re.compile(r'''[name\":]+
(?P<name>[\u4e00-\u9fa5]+)[\",lat:]+   #591的捷運名稱
(?P<lat>[\d.]+)[\",lng:]+   #591的捷運緯度
(?P<lng>[\d.]+)[\",zoom:\d]+[\"nid:]+   #591的捷運緯度
(?P<code>[\d]+)   #591的捷運代碼
''',re.X)
# group -> () 返回tuple
# ?P<name> tuple該變數的名稱
# 用group須注意group間必須為完整串連之關係(合起來full search一樣沒問題)

#利用迴圈,找出所有符合pattern的資料   
    
text711='''
var AREACODE = {    
    _mCity : {
		TW:new Array(
	        new AreaNode('',       new bu(121517166,25048055), '00'),
	        new AreaNode('台北市', new bu(121517166,25048055), '01'), 
	        new AreaNode('基隆市', new bu(121768104,25151627), '02'),
	        new AreaNode('新北市', new bu(121459043,25009605), '03'),
	        new AreaNode('桃園市', new bu(121301782,24993918), '04'),
	        new AreaNode('新竹市', new bu(120973664,24805210), '05'),
	        new AreaNode('新竹縣', new bu(121004279,24839621), '06'),
	        new AreaNode('苗栗縣', new bu(120819108,24561589), '07'),
        '''
match711 = re.compile(r'''AreaNode\(\'
(?P<city>[\u4e00-\u9fa5]+)\',\s #711縣市
(?P<abandon>[\s\w]+\([\d,]+\)),\s\' #711雜魚
(?P<code>[\d]+) #711代碼
''',re.X)

#法二 : AreaNode[\(\']+([^,]+)(,[^,]+){3}
#法三 : AreaNode[\(\']+(?P<city>[\u4e00-\u9fa5]+)\'[^\']+\'(?P<code>[\d]+)
#法四 : AreaNode[(](?P<city>\'[^\']+)(?P<code>\'[^\']+){2}

for match in match711.finditer(text711):
    print('{city} {abandon} {code}'.format(**match.groupdict()))
