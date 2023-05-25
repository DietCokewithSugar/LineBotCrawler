from selenium import webdriver
import time
from bs4 import BeautifulSoup
from datetime import datetime,timedelta
import json


'''
设置停留时间
'''
def sleep_time():
    time.sleep(10)

'''
加载浏览器驱动

'''
def load_driver(url,browser,path):
    # Chrome驱动加载
    if browser == 'Chrome':
        driver = webdriver.Chrome(path)
    # Edge驱动加载
    elif browser == 'Edge':
        driver = webdriver.Edge(path)
    driver.maximize_window()  # 最大化界面
    # 发起请求
    driver.get(url)
    return driver

'''
模拟登录
'''
def login(driver,username_xpath,password_xpath,button_xpath,username,password):
    username_field = driver.find_element_by_xpath(username_xpath)
    password_field = driver.find_element_by_xpath(password_xpath)
    # 输入用户名和密码
    username_field.send_keys(username)
    password_field.send_keys(password)
    # 提交form
    button = driver.find_element_by_xpath(button_xpath)
    button.click()
    return driver


'''
根据xpath跳转到对应界面
'''
def find_element(driver,xpath):
    element = driver.find_element_by_xpath(xpath)
    element.click()
    return driver


'''
更新driver
'''
def switch(driver):
    handlers = driver.window_handles
    driver.switch_to.window(handlers[-1])
    return driver


'''
关闭页面
'''
def quit(driver):
    driver.quit()


'''
模拟用户到达群聊界面
'''
def driver_chat(url,username,password,browser,driver_path):
    driver = load_driver(url,browser,driver_path)
    #link = '/html/body/div/div[1]/main/div/div/div[1]/div/div/div/div[2]/div[2]/div/a[1]'   #这是之前的xpath，但是后面官方修改了界面，变成了下面这个链接
    link = '/html/body/div/div[1]/div[1]/div[3]/div/div[2]/a'
    driver = find_element(driver,link)
    sleep_time()
    login1 = '/html/body/div[2]/div/div[3]/div/form/div/input'
    driver = find_element(driver,login1)
    username_xpath = '/html/body/div/div/div/div/div/div[2]/div/form/fieldset/div[1]/input'
    password_xpath = '/html/body/div/div/div/div/div/div[2]/div/form/fieldset/div[2]/input'
    button_xpath = '/html/body/div/div/div/div/div/div[2]/div/form/fieldset/div[3]/button'
    driver = login(driver,username_xpath,password_xpath,button_xpath,username,password)
    sleep_time()
    message = '/html/body/div/div/div/aside/div/div/div/section/div[2]/div/ul/li/a'
    driver = find_element(driver,message)
    sleep_time()
    user = '/html/body/div/div/div/section/div/div/section/div/div[2]/a/a/article/section'
    driver = find_element(driver,user)
    sleep_time()
    account = '/html/body/div/div/div/section/div/div/section/div/div/section[1]/p/p/a'
    driver = find_element(driver,account)
    sleep_time()
    driver = switch(driver)
    chats = '/html/body/div/div[1]/nav/div/ul[1]/li[8]/a'
    driver = find_element(driver,chats)
    sleep_time()
    driver = switch(driver)
    '''/html/body/div[2]/div/div[1]/div/div[2]/nav/div[1]/a
    basic = '/html/body/div[2]/div/div[1]/div[1]/div[2]/nav/div[3]/div[2]/div[2]/a'
    driver = find_element(driver,basic)'''
    return driver

'''
获取每个群聊的url地址
'''
def get_group_url(driver,group):
    driver = find_element(driver,group)
    driver = switch(driver)
    url = driver.current_url
    sleep_time()
    return driver,url


'''
下载群聊文件
'''
def download(driver):
    download = '/html/body/div[2]/div/div[1]/div[1]/main/div/div[2]/section[4]/div[3]/div/button'
    driver = find_element(driver,download)
    sleep_time()

'''
从html中获取群聊对应的div
'''
def get_div(driver,url):
    driver.get(url)
    html_content = driver.page_source
    sleep_time()
    div_list = driver.find_elements_by_css_selector('div[class="position-relative"]')
    return div_list

'''
创建群聊消息保存文件
'''
def create_file(path):
    file = open(path,'w',encoding='utf-8')
    return file


'''
依次遍历div,并从中获取需要的内容
'''
def read_div(div_list,file,group_number,is_group,group_name,group_user_number,i,url):
    # 采集时间获取，获取系统时间
    crawler_time = str(datetime.now())
    group_all_information = {}  # json中存入的字典
    content_list1 = [] # 存储群聊消息
    group_all_information['Id'] = i
    group_all_information['Group number'] = group_number
    group_all_information['Group url'] = url
    group_all_information['Is group'] = is_group
    group_all_information['Group name'] = group_name
    group_all_information['Group user number'] = group_user_number
    group_all_information['Crawler time'] = crawler_time
    group_all_information['Nation category'] = '1-境外'
    group_all_information['Data source'] = 'LINE'
    Massage_id = 0
    for div in div_list:
        # 这里每一天的聊天记录是一个div，class为position-relative
        soup = BeautifulSoup(div.get_attribute('innerHTML'),'html.parser')
        # 获取消息发送的时间
        date = soup.find('div',{'class': 'chatsys-content'})
        date = date.text.strip()
        # 获取聊天消息的主体，每一条消息为一个div，但是同一个用户连续发送的消息在一个div中
        chat_content = soup.find_all('div',{'class': 'chat-content'})
        # 遍历消息主体
        for content_main in chat_content:
            content_list = []
            json_object ={}
            # 获取用户名称
            user_name = content_main.find('div',{'class': 'chat-header'})
            # 获取该用户在该时间段发送的消息
            content_text_div = content_main.find_all('div', {'class': 'chat-item-text user-select-text'})
            # 获取发送的表情包及图片
            content_img = content_main.find_all('img')
            # 获取发送的语音
            voices = content_main.find_all('div', {'class': 'chat-item-voice-text'})
            #print(voices)
            # 发送消息的具体时间
            time = content_main.find_all('div', {'class': 'chat-sub'})
            # 这里用户分为用户发送和机器人发送或自动回复
            if user_name == None or user_name.text.strip() == 'Auto-response':
                user_name = 'Auto-response'
                sender_type = 'Account'
            else:
                user_name = user_name.text.strip()
                sender_type = 'User'
            # 同一时间段发送的消息只有一个time，其他为空，所以遍历判断是否有值
            for time1 in time:
                if time1.text.strip() == '':
                    continue
                else:
                    true_time = time1.text.strip()
            # 获取具体的聊天记录
            if content_text_div:
                for content in content_text_div:
                    content_list.append(content.text.strip())
            if content_img:
                for content in content_img:
                    content_list.append(content['src'])
            if voices:
                for voice in voices:
                    content_list.append(voice.text.strip())
            # 在页面上如果是今天或昨天发送的内容则转换为具体的时间，方便存储
            if str(date) == 'Today':
                date = datetime.now()
                date = date.strftime("%a, %b %d")
            if str(date) == 'Yesterday':
                date = datetime.now()-timedelta(days=1)
                date = date.strftime("%a, %b %d")
            Massage_id = Massage_id+1
            json_object['Massage id'] = Massage_id
            json_object['Group name'] = group_name
            json_object['Sender type'] = sender_type
            json_object['Sender name'] = user_name
            json_object['Date'] = str(date)
            json_object['Time'] = true_time
            json_object['Message'] = content_list
            content_list1.append(json_object)
    group_all_information['Intime'] = str(datetime.now())
    group_all_information['Content'] = content_list1 
    # 写进json     
    json.dump(group_all_information,file,ensure_ascii=False)    
                
'''
读取配置文件
'''
def open_config_file(path):
    with open(path,'r',encoding='utf-8') as file:
        config = json.load(file)
    return config

'''
程序入口
'''
if __name__ == '__main__':
    url = 'https://developers.line.biz/en/'
    path = 'config.json'
    config = open_config_file(path)
    save_path = config['save_path']
    username = config['username']
    password = config['password']
    browser = config['browser']
    driver_path = config['driver_path']
    driver = driver_chat(url,username,password,browser,driver_path)
    file = create_file(save_path)
    group_number = config['group_number']
    # 依次遍历每个群聊，并获取其内容
    for i in range(1,group_number+1):
        try:
            group = '/html/body/div[2]/div/div[1]/div/main/div/div[1]/div/div[2]/div[2]/div/div['+str(i)+']/a'
            #group = '/html/body/div[2]/div/div[1]/div[1]/main/div/div[1]/div/div[2]/div[2]/div/div['+str(i)+']/a'
            driver,url1 = get_group_url(driver,group)
            driver.get(url1)
            sleep_time()
            group_number = str(url1)[61:]
            group_user_number_tag = driver.find_element_by_css_selector('span[class="cursor-pointer"]')
            # 判断是用户还是群
            if group_user_number_tag == []:
                is_group = 'user'
                group_name_tag = driver.find_element_by_css_selector('h4[class="mb-0 text-truncate"]')
                group_name = group_name_tag.text
                group_user_number = ''
            else:
                is_group = 'group'
                group_name_tag = driver.find_element_by_css_selector('h4[class="mb-0 text-truncate cursor-pointer"]')
                group_name = group_name_tag.text
                group_user_number = group_user_number_tag.text
            div_list = get_div(driver,url1)
            read_div(div_list,file,group_number,is_group,group_name,group_user_number,i,url1)
        except Exception:
            continue
    quit(driver)

