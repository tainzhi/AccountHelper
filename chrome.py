#!/user/bin/python3

import os
import time
from platform import system
from selenium import webdriver, common
from PIL import Image


class Chrome:
    root = ''
    chrome = None

    # 初始化, 并加载 天眼查根目录
    def __init__(self, url):
        self.root = url
        driver_location = self.get_driver()
        if driver_location is None:
            print('不支持的系统类型！')
            exit(-1)
        self.chrome = webdriver.Chrome(driver_location)
        self.chrome.implicitly_wait(3)
        self.chrome.get(url)

    def save_pic(self, company):
        company_code = company[1]
        company_name = company[2]
        company_address = company[3]

        # 切换到第一个tab
        self.chrome.switch_to.window(self.chrome.window_handles[0])
        self.chrome.get("https://www.tianyancha.com/search?key={value}".format(value=company_address))
        # self.chrome.find_element_by_css_selector('input[type=search]').send_keys(company_address)
        print(self.chrome.page_source)
        self.chrome.find_element_by_css_selector('.input-group-btn').click()
        # 获取第一条记录的公司的超链接
        company_url = self.chrome.find_element_by_css_selector('.name,.select-none').get_attribute('href')
        self.chrome.get(company_url)
        # self.chrome.find_element_by_css_selector('.name,.select-none').click()
        # 切换到新tab
        # self.chrome.switch_to.window(self.chrome.window_handles[1])
        
        detail_address = self.chrome.find_element_by_css_selector('.detail-content').text
        
        # 最终保存的图片路径
        saved_image_path = "{code}_{name}.png".format(code=company_code, name=company_name)
        self.chrome.save_screenshot(saved_image_path)
        try:
            im = Image.open(saved_image_path)
            im.crop(0, 0, 100, 100)
            im.save(saved_image_path)
        except OSError:
            print(OSError.strerror)
        self.chrome.close()
        
    def quit(self):
        # quit Chrome browser
        self.chrome.quit()

    @staticmethod
    def get_driver():
        os_type = system()
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

    def lazy_click(self, driver,
                   element):  # 简单的封装了一下click方法，页面未加载完成的时候会出现NoSuchElementException或者ElementNotInteractableException错误，捕获错误并重试，默认重试50次，相当于最大等待时长50s
        f = False
        n = 0
        while (not f and n < 50):
            n = n + 1
            try:
                driver.find_element_by_css_selector(element).click()
                f = True
            except (common.exceptions.NoSuchElementException, common.exceptions.ElementNotInteractableException):
                print('lazy-click :页面未加载完成，等待中。')
                time.sleep(1)
                f = False

    def lazy_send(self, driver, element, KeyBords):  # 这里也是等待直到找到元素并成功推送按键命令
        f = False
        n = 0
        while (not f and n < 50):
            n = n + 1
            try:
                driver.find_element_by_css_selector(element).send_keys(KeyBords)
                f = True
            except (common.exceptions.NoSuchElementException, common.exceptions.ElementNotInteractableException,
                    common.exceptions.ElementNotInteractableException):
                print('lazy-send页面未加载完成，等待中。')
                time.sleep(1)
                f = False
