from selenium import webdriver
import time
from bs4 import BeautifulSoup
from datetime import datetime,timedelta
import json


'''
设置停留时间
'''
def sleep_time():
    time.sleep(20)
'''
加载浏览器驱动

'''
def load_driver(url,browser,path):
    if browser == 'Chrome':
        driver = webdriver.Chrome(path)
    elif browser == 'Edge':
        driver = webdriver.Edge(path)
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
    '''username = 'xiguo_gu@126.com'
    password = 'gxg19980709'''
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
    
    '''basic = '/html/body/div[2]/div/div[1]/div[1]/div[2]/nav/div[3]/div[2]/div[2]/a'
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
    crawler_time = str(datetime.now())
    group_all_information = {}
    content_list1 = []
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
        soup = BeautifulSoup(div.get_attribute('innerHTML'),'html.parser')
        date_list = soup.find_all('div',{'class': 'chatsys-content'})
        #print('data_list{}',format(len(date_list)))
        user_name_list = soup.find_all('div',{'class': 'chat-header'})
        #print('user_list{}',format(len(user_name_list)))
        content_mains = soup.find_all('div',{'class': 'chat-main w-max-480'})
        #print(content_mains)
        content_list = []
        for content_main in content_mains:
            content_text_div = content_main.find('div', {'class': 'chat-item-text user-select-text'})
            content_img = content_main.find('img', {'id': '__test__sticker_image'})
            if content_text_div:
                #print(content_text_div)
                content_list.append(content_text_div)
            elif content_img:
                content_list.append(content_img)

        time_list = soup.find_all('div', {'class': 'chat-sub'})
        if date_list == [] and user_name_list == []:
            continue
        else:
            date = date_list[0].text.strip()
            if str(date) == 'Today':
                date = datetime.now()
                date = date.strftime("%a, %b, %d")
            if str(date) == 'Yesterday':
                date = datetime.now()-timedelta(days=1)
                date = date.strftime("%a, %b, %d")
            for user_name_div,content_div,time_div in zip(user_name_list,content_list,time_list):
                json_object = {}
                if content_div.name == 'img':
                    content = content_div['src']
                else: 
                    content = content_div.text
                if user_name_div.text.strip() == 'Auto-response':
                    sender_type = 'Account'
                else:
                    sender_type = 'User'
                Massage_id = Massage_id+1
                json_object['Massage id'] = Massage_id
                json_object['Group name'] = group_name
                json_object['Sender type'] = sender_type
                json_object['Sender name'] = user_name_div.text.strip()
                json_object['Date'] = str(date)
                json_object['Time'] = time_div.text.strip()
                json_object['Message'] = content.strip()
                content_list1.append(json_object)
    group_all_information['Intime'] = str(datetime.now())
    group_all_information['Content'] = content_list1      
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
    for i in range(1,group_number+1):
        try:
            group = '/html/body/div[2]/div/div[1]/div/main/div/div[1]/div/div[2]/div[2]/div/div['+str(i)+']/a'
            #group = '/html/body/div[2]/div/div[1]/div[1]/main/div/div[1]/div/div[2]/div[2]/div/div['+str(i)+']/a'
            driver,url1 = get_group_url(driver,group)
            driver.get(url1)
            #print(url1)
            sleep_time()
            group_number = str(url1)[61:]
            group_user_number_tag = driver.find_element_by_css_selector('span[class="cursor-pointer"]')
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

    
    






