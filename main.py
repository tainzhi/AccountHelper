import os
import time
import platform
import pandas as pd
from selenium import webdriver
from selenium import webdriver,common
from selenium.webdriver.common.keys import Keys


def lazyClick(driver, element):#简单的封装了一下click方法，页面未加载完成的时候会出现NoSuchElementException或者ElementNotInteractableException错误，捕获错误并重试，默认重试50次，相当于最大等待时长50s
    f = False
    n = 0
    while(not f and n<50):
        n = n+1
        try:
            driver.find_element_by_css_selector(element).click()
            f = True
        except (common.exceptions.NoSuchElementException, common.exceptions.ElementNotInteractableException):
            print('lazy-click :页面未加载完成，等待中。')
            time.sleep(1)
            f = False


def lazySend(driver, element, KeyBords):#这里也是等待直到找到元素并成功推送按键命令
    f = False
    n = 0
    while(not f and n<50):
        n = n+1
        try:
            driver.find_element_by_css_selector(element).send_keys(KeyBords)
            f = True
        except (common.exceptions.NoSuchElementException, common.exceptions.ElementNotInteractableException, common.exceptions.ElementNotInteractableException):
            print('lazy-send页面未加载完成，等待中。')
            time.sleep(1)
            f = False


def get_driver():
    os_type = platform.system()
    root_dir = os.path.dirname(os.path.abspath(__file__))
    drivers_dir = os.path.join(root_dir, 'drivers')
    if os_type == 'Darwin':
        return os.path.join(drivers_dir, 'chromedriver_mac64')
    elif os_type == 'Windows':
        return os.path.join(drivers_dir, 'chromedriver_win32.exe')
    elif os_type == 'Linux':
        return os.path.join(drivers_dir, 'chromedriver_linux64')
    else:
        return None


def select_excel():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    excels_dir = os.path.join(root_dir, 'excels')
    excels = []
    for file in os.listdir(excels_dir):
        file_path = os.path.join(excels_dir, file)
        if os.path.isfile(file_path):
            excels.append(file_path)
    if len(excels) > 0:
        print("选择要处理的excel：\n")
        for i in range(0, len(excels)):
            print(str(i) + " : " + excels[i])
    choose_index = input("请输入数字选择：")
    return excels[int(choose_index)]


def read_excel(excel):
    read = pd.read_excel(excel)
    # 从第2行开始， 获取每行的第3列， 序号，代码，单位，收件地址
    data = read.iloc[2:,[0,1,2,3]]
    # print("获取到所有的值:\n{0}".format(data))  # 格式化输出
    return data.values


def save_pic(company):
    company_code = company[1]
    comapny_name = company[2]
    company_address = company[3]
    driver_location = get_driver()
    if driver_location is None:
        print('不支持的系统类型！')
        exit(-1)

    option = webdriver.ChromeOptions()
    # headless chrome, 但是会被反爬虫 403 forbidden
    # option.add_argument('--headless')
    # option.add_argument('--disable-gpu')
    chrome = webdriver.Chrome(driver_location, options=option)
    # chrome.maximize_window()
    # # scroll down
    # chrome.execute_script('var q=document.documentElement.scrollTop=980')
    # 反爬虫
    # script = 'Object.defineProperty(navigator,"webdriver",{get:() => false,});'
    # chrome.execute_script(script)

    # 等待防止网络不稳定
    chrome.implicitly_wait(5)
    tian_yan_cha = 'https://www.tianyancha.com/'
    chrome.get(tian_yan_cha)
    chrome.find_element_by_css_selector('input[type=search]').send_keys(company_address)
    # print(chrome.page_source)
    # lazySend(chrome, 'input[type=search]', '无锡明宇机械有限公司')
    # lazyClick(chrome, '.input-group-btn')
    chrome.find_element_by_css_selector('.input-group-btn').click()
    # time.sleep(5)
    chrome.find_element_by_css_selector('.name,.select-none').click()
    # lazyClick(chrome, '.name,.select-none')
    # 切换到新tab
    chrome.switch_to.window(chrome.window_handles[1])
    #
    # chrome.current_url
    # driver.page_source
    detail_address = chrome.find_element_by_css_selector('.detail-content').text
    chrome.save_screenshot(company_code + '_' + comapny_name + '.png')
    # print(detail_address)
    # chrome.close()


if __name__ == "__main__":
    excel = select_excel()
    companies = read_excel(excel)
    for com in companies:
        save_pic(com)

