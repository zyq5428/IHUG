import pandas as pd
from pandas import Series, DataFrame
import numpy as np
from datetime import datetime

def make_date(x):
    date = '2021年' + x
    new_date = datetime.strptime(date, '%Y年%m月%d日%H:%M')
    return new_date

df = pd.read_csv('activity.csv')
df['date'] = pd.to_datetime(df['活动时间'].apply(make_date))
df['week'] = df['date'].dt.dayofweek+1
df.columns
df = df[['Unnamed: 0', '宣传平台', '活动分类', '组织名称', '具体活动', '活动类型', '活动场地', '活动时间', 'date', 'week', '活动收藏量', '浏览量', '活动频率', '活动价格', '联系方式', '活动链接',
       '针对用户群体']]
df.sort_values('date', inplace=True)
df.to_csv('activity_process.csv', encoding='utf_8_sig')
