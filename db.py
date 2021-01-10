import os
import shelve
from util import Util


class Db:
    __path = None
    __d = None

    def __init__(self):
        root_dir = Util.get_config_dir()
        # 配置保存在./config/config.*中
        config_name = 'config'
        self.__path = os.path.join(root_dir, config_name)
        self.__d = shelve.open(self.__path)

    def get_need_login(self):
        try:
            need = self.__d['need_login']
            return need
        except KeyError:
            # 默认不需要登录，容易被爬虫检测到
            return False

    def save_need_login(self, need):
        self.__d['need_login'] = need

    def get_recent_excel(self):
        try:
            excel = self.__d['recent_excel']
            return excel
        except KeyError:
            # 不存在最近的excel记录
            return None

    def save_recent_excel(self, recent_excel):
        self.__d['recent_excel'] = recent_excel

    def get_browser_cookie(self, browser_name):
        try:
            cookie = self.__d[browser_name]
            return cookie
        except KeyError:
            return None

    def save_browser_cookie(self, browser_name, cookie):
        self.__d[browser_name] = cookie

    def save_handled_companies(self, companies):
        self.__d['handled_company'] = companies

    def get_handled_companies(self):
        try:
            companies = self.__d['handled_company']
            return companies
        except (KeyError, EOFError) as e:
            return dict()

    def close(self):
        self.__d.close()
