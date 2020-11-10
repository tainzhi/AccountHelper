#!/user/bin/python3

import os
import time
import numpy
from difflib import SequenceMatcher
from selenium import webdriver, common
from PIL import Image


class Chrome:
    __driver = None

    # 初始化, 并加载 天眼查根目录
    def __init__(self, driver_location, url):
        self.__driver = webdriver.Chrome(driver_location)
        self.__driver.get(url)
        self.__driver.implicitly_wait(5)

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
        try:
            im = Image.open(saved_image_path)
            cropped_image = im.crop(rect)
            cropped_image.save(saved_image_path)
        except OSError:
            print(OSError.strerror)
        same_ratio = '{:.3f}'.format(SequenceMatcher(None, company_address, detail_address).ratio())
        ret_company = numpy.append(company, [detail_address, same_ratio])
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
