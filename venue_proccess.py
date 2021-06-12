import pandas as pd
from pandas import Series, DataFrame
import numpy as np
import re

def find_people(x):
    people_list = re.findall(r'\d+', x)
    people = int(people_list[0])
    return people
def find_area(x):
    area_list = re.findall(r'\d+', x)
    area = int(area_list[0])
    return area
def find_price(x):
    if '元/天 起' in x:        
        price_list = re.findall(r'\d+', x)
        price = int(price_list[0])
    elif '元/半天 起' in x:        
        price_list = re.findall(r'\d+', x)
        price = int(price_list[0]) * 2
    elif ('元/小时 起' in x) or ('元/时 起' in x):        
        price_list = re.findall(r'\d+', x)
        price = int(price_list[0]) * 8
    else :
        price = x
    return price

df = pd.read_csv('venue.csv')

df['场地价格(元/天 起)'] = df['场地价格'].astype(str).apply(find_price)
df['场地大小(平米起)'] = df['场地大小'].apply(find_area)
df['推荐人数(人)'] = df['推荐人数'].apply(find_people)
# df.columns
df = df[['平台', '区域', '场地名称','场地活动类型', '场地价格', '场地价格(元/天 起)', '场地大小(平米起)', '推荐人数(人)', '场地主人', '联系方式',  '场地位置', '服务设施', '浏览量', '咨询量', '场地链接']]

df.to_csv('venue_process.csv', encoding='utf_8_sig')
