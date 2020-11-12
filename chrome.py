#!/user/bin/python3

import os
import time
import numpy
from selenium import webdriver, common
from PIL import Image
import pickle
import util


class Chrome:
    __driver = None
    __window = None
    __url = None
    __cookie_dir = util.PathUtil.get_cookie_dir()
    __cookie_name = 'chrome.cookie'
    __driver_location = util.PathUtil.get_driver_location()

    # 初始化, 并加载 天眼查根目录
    def __init__(self, url, window=None):
        self.__driver = webdriver.Chrome(self.__driver_location)
        self.__url = url
        self.__window = window
        self.login()

    def login(self):
        cookie_path = os.path.join(self.__cookie_dir, self.__cookie_name)
        if os.path.exists(cookie_path):
            try:
                self.__driver.get(self.__url)
                open_file = open(cookie_path, 'rb')
                cookies = pickle.load(open_file)
                open_file.close()
                for co in cookies:
                    self.__driver.add_cookie(co)
                self.__driver.get(self.__url)
                self.__driver.implicitly_wait(5)
                if self.is_login():
                    return
                else:
                    self.login_get_cookie(cookie_path)
            except EOFError:
                self.login_get_cookie(cookie_path)
        else:
            self.login_get_cookie(cookie_path)

    def login_get_cookie(self, cookie_path):
        # 没有登录成功
        # 我在开发的时候， 刚好在双十一， 一进入该页面， 会弹出一个促销dialog， 故需要close
        self.__driver.get(self.__url)
        self.__driver.implicitly_wait(5)
        try:
            self.__driver.find_element_by_css_selector('.modal-close').click()
        except (common.exceptions.NoSuchElementException, common.exceptions.ElementNotInteractableException,
                common.exceptions.ElementNotInteractableException):
            print("no ad dialog")
        # 点击登录
        self.__driver.find_element_by_css_selector("[onclick='header.loginLink(event)']").click()
        # 循环直到登录成功
        while True:
            try:
                self.__driver.find_element_by_css_selector('.scan-title').text != '手机扫码登录'
            except (common.exceptions.NoSuchElementException,
                    common.exceptions.ElementNotInteractableException,
                    common.exceptions.ElementNotInteractableException,
                    common.exceptions.StaleElementReferenceException
                    ):
                break
            time.sleep(1)
            # print("请扫码登录")
            self.__window.write_event_value('-Chrome State-', "请扫码登录")
        # 获取了很多个cookie, 类似这样[{'domain':...}, {}, {}]
        # 其实只有一个cookie dict是有效的
        # cookie = {
        #     'domain': 'tianyania.com',
        #     'httpOnly': False,
        #     'path': '/',
        #     'secure': False
        # }
        cookie = self.__driver.get_cookies()
        open_file = open(cookie_path, 'wb')
        pickle.dump(cookie, open_file)
        open_file.close()
        print(cookie)

    def is_login(self):
        try:
            user_name = self.__driver.find_element_by_css_selector('.nav-user-name').text
            return True
        except (common.exceptions.NoSuchElementException, common.exceptions.ElementNotInteractableException,
                common.exceptions.ElementNotInteractableException):
            return False

    def read_cookie(self, cookie_path):
        return

    def save_pic(self, pic_root_dir, company):
        """
        截图后， crop成指定大小
        :param pic_root_dir:
        :param company:
        :return:
        """
        company_code = company[1]
        company_name = company[2]
        company_address = company[3]

        self.__driver.get("https://www.tianyancha.com/search?key={value}".format(value=company_name))
        # 获取第一条记录的公司的超链接
        company_url = self.__driver.find_element_by_css_selector('.name,.select-none').get_attribute('href')
        self.__driver.get(company_url)
        detail_address = self.__driver.find_element_by_css_selector('.detail-content').text
        detail_element = self.__driver.find_element_by_css_selector('.box > .content')
        location = detail_element.location
        size = detail_element.size
        left = location['x']
        top = location['y']
        right = left + size['width']
        bottom = top + size['height']
        rect = (left, top, right, bottom)
        saved_image_path = "{code}_{name}.png".format(code=company_code, name=company_name)
        # 最终保存的图片路径
        saved_image_path = os.path.join(pic_root_dir, saved_image_path)
        self.__driver.save_screenshot(saved_image_path)
        if util.IS_CROP_IMAGE:
            try:
                im = Image.open(saved_image_path)
                cropped_image = im.crop(rect)
                cropped_image.save(saved_image_path)
            except OSError:
                print(OSError.strerror)
        ret_company = numpy.append(company, [detail_address, util.Util.is_same_address(company_address, detail_address)])
        return ret_company

    def quit(self):
        # quit Chrome browser
        self.__driver.quit()

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
