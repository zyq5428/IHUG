import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from pyquery import PyQuery as pq
from time import sleep

import pandas as pd
from pandas import Series, DataFrame

import random

import re

import pyautogui
pyautogui.PAUSE = 0.5 

chromedriver_path = r"D:\python\chromedriver.exe" #改成你的chromedriver的完整路径地址

def get_my_proxy():
    #5000：settings中设置的监听端口，不是Redis服务的端口
    proxy_json = requests.get("http://webapi.http.zhimacangku.com/getip?num=1&type=2&pro=&city=0&yys=0&port=1&time=1&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions=").json()
    proxy_data = proxy_json.get('data')[0]
    proxy = proxy_data.get('ip') + ':' + str(proxy_data.get('port'))
    return proxy

class web_process:
    def __init__(self, proxy):
        self.proxy = proxy
        
        self.options = webdriver.ChromeOptions()
        # self.options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2}) # 不加载图片,加快访问速度
        self.options.add_experimental_option('excludeSwitches', ['enable-automation']) # 此步骤很重要，设置为开发者模式，防止被各大网站识别出来使用了Selenium

        self.options.add_experimental_option('useAutomationExtension', False)
        
        self.options.add_argument('lang=zh-CN,zh,zh-TW,en-US,en')
        self.options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36')
        # self.options.add_argument('user-agent="Mozilla/5.0 (iPod; U; CPU iPhone OS 2_1 like Mac OS X) AppleWebKit/525.18.1 (KHTML, like Gecko) Version/3.1.1 Mobile/5F137 Safari/525.20"')

        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument('--ignore-ssl-errors')
        
        prefs = {"profile.managed_default_content_settings.images": 2}
        self.options.add_experimental_option("prefs", prefs)

        # self.options.add_argument('--disable-extensions')
        # self.options.add_experimental_option('excludeSwitches',['ignore-certificate-errors'])
        self.options.add_argument('--start-maximized')
        
        self.options.add_argument('disable-blink-features=AutomationControlled') #告诉chrome去掉了webdriver痕迹

        if self.proxy != '':
            self.options.add_argument('--proxy-server=http://' + self.proxy)
 
    def open_web(self):
        self.browser = webdriver.Chrome(executable_path=chromedriver_path, options=self.options)
        self.wait = WebDriverWait(self.browser, 10) #超时时长为10s
        
    def get_html(self, url):
        self.url = url
        try:
            self.browser.get(self.url)
            self.browser.implicitly_wait(10) #智能等待，直到网页加载完毕，最长等待时间为30s
            return self.browser
        except:
            print('无法打开该网页')
            return None
    
    def close_web(self):
        self.browser.close()

def get(web, url, key):        
    # 同一个代理，最多查找同一网页两次
    retry_count = 2
    # print('xpath is: {}'.format(key['xpath']))
    # print('text is: {}'.format(key['text']))
    while retry_count > 0:
        html = web.get_html(url)
        if html == None:
            retry_count -= 1
        else:
            try:
                key_text = html.find_element_by_xpath(key['xpath']).text
                print(key_text)
                if key['text'] == key_text:
                    print('网页确认符合要求')
                    return html
                else:
                    print('网页错误')
                    retry_count -= 1
            except:
                print('网页重定向')
                retry_count -= 1
    return None

# def get_with_proxy(web, url, key):
#     global proxy_change

#     retry_N = 2
#     while retry_N > 0:
#         if proxy_change:
#             proxy = get_my_proxy()
#             print(proxy)
#             proxy_change = False
#             web = web_process(proxy)
#             web.open_web()
#         html = get(web, url, key)
#         if html == None:
#             print('{} 第{}次打开失败'.format(url, (-retry_N + 3)))
#             proxy_change = True
#             web.close_web()
#         else:
#             ele = html.find_element_by_xpath(key['xpath'])
#             print(ele.text)
#             break
#         retry_N -= 1

def get_with_proxy(url, key):
    global proxy_change
    global web

    retry_N = 2
    while retry_N > 0:
        if proxy_change:
            proxy = get_my_proxy()
            print(proxy)
            proxy_change = False
            web = web_process(proxy)
            web.open_web()
        html = get(web, url, key)
        if html == None:
            print('{} 第{}次打开失败'.format(url, (-retry_N + 3)))
            proxy_change = True
            web.close_web()
        else:
            return html
        retry_N -= 1
    print('记录：网页 {} 无法打开，跳过！'.format(url))

def get_content():
    devp = '活动行-活动场地'
    area = ['福田区', '罗湖区', '南山区', '宝安区', '龙岗区', '盐田区', '龙华区', '光明新区', '坪山区', '大鹏新区']
    # area = ['坪山区', '盐田区']
    key = {'xpath':'/html/body/div[1]/footer/div/div/p[2]', 'text':'活动行 v4.3 © huodongxing.com All Rights Reserved.'}
    url = 'http://venue.huodongxing.com/venue/search?sort=1&city=%E6%B7%B1%E5%9C%B3&asc=0&pi=1'

    for a in range(len(area)):
        print(area[a])
        url = 'http://venue.huodongxing.com/venue/search?sort=1&city=%E6%B7%B1%E5%9C%B3&district=' + area[a] + '&asc=0&pi=1'
        html = get_with_proxy(url, key)
        page_table = html.find_element_by_xpath('//*[@id="layui-laypage-1"]')
        page = re.findall(r'\d+', page_table.text)
        print(page)
        if len(page) == 1:
            new_page_table = re.findall(r'\d', page[0])
            num_str = new_page_table[len(new_page_table)-1]
        elif len(page) == 2:
            num_str = page[1]
        else:
            break

        num = int(num_str)
        print(num)

        for n in range(1, num+1):
            # print("start {} page".format(n))
            sleep(random.randint(5,9))
            page_url = 'http://venue.huodongxing.com/venue/search?sort=1&city=%E6%B7%B1%E5%9C%B3&district=' + area[a] + '&asc=0&pi=' + str(n)

            html = get_with_proxy(page_url, key)

            for i in range(1, 11):
                indent = '/html/body/div[1]/section/section/section[2]/section/section[2]/div[2]/div[' + str(i) + ']'
                try:
                    activity = html.find_element_by_xpath(indent)
                    # print("find {} activity".format(i))
                    # print(activity.text)
                except:
                    print("no {} activity".format(i))
                    break

                activity_url = activity.find_element_by_xpath(".//div/h4")
                activity_url_text = activity_url.get_attribute('onclick')
                activity_url_text = re.findall(r'\d+', activity_url_text)
                activity_url_text = 'http://venue.huodongxing.com/venue/detail/' + activity_url_text[0]
                activity_price = activity.find_element_by_xpath(".//div/div/div[1]")
                activity_size = activity.find_element_by_xpath(".//div/div/div[3]/div[1]")
                activity_people = activity.find_element_by_xpath(".//div/div/div[3]/div[2]")
                activity_position = activity.find_element_by_xpath(".//div/div/div[4]/p") 
                activity_tag = activity.find_element_by_xpath(".//div/div/div[5]/div")

                activity_dict = {'平台':devp, '区域':area[a], '场地名称':activity_url.text, '场地主人':'', '联系方式':'', '场地活动类型':activity_tag.text, '场地价格': activity_price.text, '场地大小':activity_size.text, '推荐人数':activity_people.text, '场地位置':activity_position.text, '服务设施':'', '浏览量':'', '咨询量':'', '场地链接':activity_url_text}

                activity_list.append(activity_dict)

def get_details():
    length = len(activity_list)
    key = {'xpath':'/html/body/div[1]/footer/div/div/p[2]', 'text':'活动行 v4.3 © huodongxing.com All Rights Reserved.'}
    for i in range(length):
        sleep(random.randint(3,6))
        activity_link = activity_list[i]['场地链接']
        # print(activity_link)
        html = get_with_proxy(activity_link, key)

        try:
            activity_price_detail = html.find_element_by_xpath('/html/body/div[1]/section/section/section/section/div/div/section[1]/article/div[2]/div[1]/div[1]')
            activity_attention = html.find_element_by_xpath('/html/body/div[1]/section/section/section/section/div/div/section[1]/article/div[2]/div[3]/div[1]/span[3]')
            activity_advisory = html.find_element_by_xpath('/html/body/div[1]/section/section/section/section/div/div/section[1]/article/div[2]/div[3]/div[1]/span[6]')
            activity_tag = html.find_element_by_xpath('/html/body/div[1]/section/section/section/section/div/div/section[1]/article/div[2]/div[4]/div')
            activity_traffic = html.find_element_by_xpath('/html/body/div[1]/section/section/section/section/div/div/section[2]/section[2]/div')
            activity_facility = html.find_element_by_xpath('/html/body/div[1]/section/section/section/section/div/div/section[2]/section[3]/div')
            activity_owner = html.find_element_by_class_name('admin-inform-person')
            activity_phone = html.find_element_by_class_name('admin-pnone-pp')   

            activity_list[i]['场地价格'] = activity_price_detail.text
            activity_list[i]['浏览量'] = activity_attention.text
            activity_list[i]['咨询量'] = activity_advisory.text
            activity_list[i]['场地活动类型'] = activity_tag.text
            # activity_list[i]['交通指南'] = activity_traffic.text
            activity_list[i]['服务设施'] = activity_facility.text.replace('\n', ' ').replace('\r', '')
            activity_list[i]['场地主人'] = activity_owner.text
            activity_list[i]['联系方式'] = activity_phone.text

        except:
            print("no item,url: {}".format(activity_link))
            activity_list[i]['场地价格'] = ''
            activity_list[i]['浏览量'] = ''
            activity_list[i]['咨询量'] = ''
            activity_list[i]['场地活动类型'] = ''
            # activity_list[i]['交通指南'] = ''
            activity_list[i]['服务设施'] = ''
            activity_list[i]['场地主人'] = ''
            activity_list[i]['联系方式'] = ''

if __name__ == "__main__":
    activity_list = []

    proxy_change = False
    # proxy_change = True

    # 首次打开网页
    proxy = get_my_proxy()
    print(proxy)
    web = web_process(proxy)
    # web = web_process('')
    web.open_web()

    get_content()
    get_details()

    frame = pd.DataFrame(activity_list)
    frame.to_csv('venue.csv', encoding='utf_8_sig')

    # 最后关闭网页
    web.close_web()