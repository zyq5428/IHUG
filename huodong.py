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
import json

import pyautogui
pyautogui.PAUSE = 0.5 

chromedriver_path = r"D:\python\chromedriver.exe" #改成你的chromedriver的完整路径地址

# 获取免费IP池 IP
def get_proxy():
    return requests.get("http://127.0.0.1:5010/get/").json()

def delete_proxy(proxy):
    requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))

# 获取购买的IP池 IP，一段时间后需要在芝麻代理中换API链接
def get_my_proxy():
    try:
        proxy_json = requests.get("http://webapi.http.zhimacangku.com/getip?num=1&type=2&pro=&city=0&yys=0&port=1&time=1&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions=").json()
        proxy_data = proxy_json.get('data')[0]
    except Exception:
        print('需要更换代理API接口')
        return ''
    proxy = proxy_data.get('ip') + ':' + str(proxy_data.get('port'))
    return proxy

def get_timezone_geolocation(ip):
    url = f"http://ip-api.com/json/{ip}"
    response = requests.get(url)
    return response.json()

# IP检查网站：'https://browserleaks.com/ip'
# 机器人识别网站: 'https://bot.sannysoft.com/'
# 浏览器的时区和地理位置检测网站: 'https://whoer.net/'
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
        
        # prefs = {"profile.managed_default_content_settings.images": 2, "webrtc.ip_handling_policy": "disable_non_proxied_udp", "webrtc.multiple_routes_enabled": False, "webrtc.nonproxied_udp_enabled": False}
        prefs = {"webrtc.ip_handling_policy": "disable_non_proxied_udp", "webrtc.multiple_routes_enabled": False, "webrtc.nonproxied_udp_enabled": False}

        self.options.add_experimental_option("prefs", prefs)

        # self.options.add_argument('--disable-extensions')
        # self.options.add_experimental_option('excludeSwitches',['ignore-certificate-errors'])
        self.options.add_argument('--start-maximized')
        
        self.options.add_argument('disable-blink-features=AutomationControlled') #告诉chrome去掉了webdriver痕迹

        if self.proxy != '':
            self.options.add_argument('--proxy-server=http://' + self.proxy)
 
    def open_web(self, geo, tz):
        self.browser = webdriver.Chrome(executable_path=chromedriver_path, options=self.options)
        self.wait = WebDriverWait(self.browser, 10) #超时时长为10s
        if self.proxy != '':
            self.browser.execute_cdp_cmd("Emulation.setGeolocationOverride", geo)
            self.browser.execute_cdp_cmd("Emulation.setTimezoneOverride", tz)
        
    def get_html(self, url):
        self.url = url
        try:
            self.browser.get(self.url)
            self.browser.implicitly_wait(30) #智能等待，直到网页加载完毕，最长等待时间为30s
            return self.browser
        except:
            print('无法打开该网页')
            return None
    
    def close_web(self):
        self.browser.close()

def open_with_proxy(web):
    global proxy

    if proxy != '':
        res_json = get_timezone_geolocation(proxy.split(':')[0])
        # print(res_json)
        geo = {
            "latitude": res_json["lat"],
            "longitude": res_json["lon"],
            "accuracy": 1
        }
        tz = {
            "timezoneId": res_json["timezone"]
        }
    else:
        geo = {}
        tz = {}
    web.open_web(geo, tz)  

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
#                 print(key_text)
                if key['text'] == key_text:
#                     print('网页确认符合要求')
                    return html
                else:
                    print('网页错误')
                    retry_count -= 1
            except:
                print('网页重定向')
                retry_count -= 1
    return None

def get_with_proxy(url, key):
    global proxy_change
    global free_proxy
    global proxy
    global captured
    global web

    # 同一个网页，最多使用两个代理尝试打开
    retry_N = 2
    while retry_N > 0:
        if proxy_change:
            if free_proxy:
                proxy = get_proxy().get("proxy")
            else:
                proxy = get_my_proxy()
            print('当前代理：{}'.format(proxy))
            proxy_change = False
            web = web_process(proxy)
            open_with_proxy(web)
            login(web)
        html = get(web, url, key)
        if html == None:
            print('{} 第{}次打开失败'.format(url, (-retry_N + 3)))
            proxy_change = True
            web.close_web()
            if free_proxy:
                delete_proxy(proxy)
        else:
            return html
        retry_N -= 1
    print('记录：网页 {} 无法打开，跳过！'.format(url))
    captured = True

def save_cookies(web, name):
    global no_cookie
    fp = open(name, 'w')
    cookies = web.browser.get_cookies()
    json.dump(cookies, fp)
    fp.close()
    no_cookie = False
    return cookies

def load_cookies(web, name):
    fp = open(name, 'r')
    cookies = json.load(fp)
    fp.close()
    # 需要先删除网页自动加载的cookies
    web.browser.delete_all_cookies()
    for cookie in cookies:
        web.browser.add_cookie(cookie)

# 活动行APP扫码登录
def login(web):
    global no_cookie
    no_login = True

    cookies_file = 'cookies.json'
    url = 'https://www.huodongxing.com/login'
    
    html = get_with_proxy(url, key)

    #加载cookies前需要先打开对应的登录页面
    if no_cookie:
        try:
            html.find_element_by_xpath('/html/body/div[2]/div[2]/div[2]/div[2]/div[1]/img[1]').click()
        except:
                print('没有扫码登陆界面')               
        while no_login:
            try:
                element = WebDriverWait(web.browser,30).until(EC.presence_of_element_located((By.CLASS_NAME,'class-name__link')))
                print(element.text)
                no_login = False
            except:
                print('登录失败，请扫码登录')
        return save_cookies(web, cookies_file)
    else:
        load_cookies(web, cookies_file)
        try:
            web.browser.refresh()
        except:
            print('刷新异常')
            sleep(30)
        try:
            element = WebDriverWait(web.browser,30).until(EC.presence_of_element_located((By.CLASS_NAME,'class-name__link')))
            print(element.text)
            no_login = False
        except:
            print('Cookies登录失败，请处理')
            return None

def get_content():
    devp = '活动行-生活'
    area = ['文艺', '手工', '户外出游', '运动健康', '聚会交友', '休闲娱乐']
    # area = ['文艺', '手工']
    key = {'xpath':'/html/body/section/section[5]/section/div[1]/div/div[2]/span', 'text':'城市:'}

    for a in range(len(area)):
        print(area[a])
        url = 'https://www.huodongxing.com/events?orderby=o&channel=%E7%94%9F%E6%B4%BB&tag=' + area[a] + '&city=%E6%B7%B1%E5%9C%B3&isChannel=true&page=1'
        html = get_with_proxy(url, key)
        try :
            page_table = html.find_element_by_xpath('//*[@id="layui-laypage-10001"]')
            page = re.findall(r'\d+', page_table.text)
            print(page)
            if len(page) == 1:
                new_page_table = re.findall(r'\d', page[0])
                num_str = new_page_table[len(new_page_table)-1]
            elif len(page) == 2:
                num_str = page[1]
            else:
                break
        except :
            num_str = '1'

        num = int(num_str)
        print(num)

        for n in range(1, num+1):
            # print("start {} page".format(n))
            sleep(random.randint(5,9))
            page_url = 'https://www.huodongxing.com/events?orderby=o&channel=%E7%94%9F%E6%B4%BB&tag=' + area[a] + '&city=%E6%B7%B1%E5%9C%B3&isChannel=true&page=' + str(n)

            html = get_with_proxy(page_url, key)

            for i in range(1, 21):
                indent = '/html/body/section/section[5]/section/div[2]/div[2]/div[' + str(i) + ']'
                try:
                    activity = html.find_element_by_xpath(indent)
                    # print("find {} activity".format(i))
                    # print(activity.text)
                except:
                    print("no {} activity".format(i))
                    break

                activity_url = activity.find_element_by_xpath(".//a")
                activity_url_text = activity_url.get_attribute('href')
                activity_title = activity.find_element_by_xpath(".//a/div[1]/div[1]")
                activity_date = activity.find_element_by_xpath(".//a/div[1]/p")
                activity_address = activity.find_element_by_xpath(".//a/div[1]/div[2]/p")
                activity_tag = activity.find_element_by_xpath(".//a/div[2]/div[1]/div")
                tag = activity_tag.text.replace('\n', '').replace('\r', '')
                activity_attention = activity.find_element_by_xpath(".//a/div[2]/div[2]/div")

                activity_dict = {'宣传平台':devp, '活动分类':area[a], '组织名称':'', '联系方式':'', '活动类型':tag, '具体活动':activity_title.text, '活动链接':activity_url_text, '针对用户群体':'','活动时间':activity_date.text, '活动频率':'', '活动场地':activity_address.text, '活动价格':'', '活动收藏量':'', '浏览量':activity_attention.text}
				
                activity_list.append(activity_dict)

def get_details():
    global captured
    length = len(activity_list)
    key = {'xpath':'/html/body/footer/div/div[2]/div[2]/p[2]', 'text':'活动行 v6.4.15 © huodongxing.com All Rights Reserved.'}

    error_num = []
    for i in range(1, length):
        sleep(random.randint(5,9))
        activity_link = activity_list[i]['活动链接']
        # print(activity_link)
        html = get_with_proxy(activity_link, key)
        
        #判断是否被网站识别
        if captured:
            error_num.append(i)
            captured = False
            k = len(error_num)
            if (error_num[k-1] - error_num[k-2] == 1):
                print('已被网站识别！未抓取链接序号为：{}'.format(error_num))
                break

        try:
            activity_organize = html.find_element_by_xpath('//*[@id="container-lg"]/div[1]/div[1]/div/div[4]/a')
            activity_favorites = html.find_element_by_xpath('//*[@id="home_register_group_funcs"]/button[2]/span[3]')        
            activity_price_list = html.find_element_by_xpath('//*[@id="home_register_group_base"]/div[1]/div')
            activity_price = activity_price_list.find_element_by_xpath('.//ul/li[1]/div/table/tbody/tr/td/h4/span')

            activity_list[i]['组织名称'] = activity_organize.text
            activity_list[i]['活动收藏量'] = activity_favorites.text
            activity_list[i]['活动价格'] = activity_price.text
        except:
            print("no item,url: {}".format(activity_link))
            activity_list[i]['组织名称'] = ''
            activity_list[i]['活动收藏量'] = ''
            activity_list[i]['活动价格'] = ''

if __name__ == "__main__":
    activity_list = []

    captured = False

    no_cookie = False
    # no_cookie = True

    #设置代理
    # no_proxy = False
    no_proxy = True

    free_proxy = False
    # free_proxy = True

    # 默认代理切换为关，只有打开网页失败后切换为开，切换代理后自动关闭
    proxy_change = False
    # proxy_change = True

    if no_proxy:
        proxy = ''
    elif free_proxy:
        proxy = get_proxy().get("proxy")
    else:
        proxy = get_my_proxy()
    print('代理设置为: {}'.format(proxy))

    # 首次打开网页
    web = web_process(proxy)
    open_with_proxy(web)

    cookies = login(web)

    get_content()
    get_details()

    frame = pd.DataFrame(activity_list)
    frame.to_csv('activity.csv', encoding='utf_8_sig')

    # 最后关闭网页
    web.close_web()