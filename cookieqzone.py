import json
import time
import platform

import requests
from config import *
from db import *
from selenium import webdriver

requests.packages.urllib3.disable_warnings()


class QQShareFile(object):
    def __init__(self, website='qqzone'):
        self.website = website
        self.cookies_db = RedisClient('cookies', self.website)
        result = self.cookies_db.get(QQ)
        if result:
            self.cookies_db.delete(QQ)
            print("Succeeded to delete cookie")
        self.chrome_options = webdriver.ChromeOptions()
        if platform.platform().startswith('Windows'):
            self.browser = webdriver.Chrome(chrome_options=self.chrome_options,
                                            executable_path=r'D:\WORKSPACE\Subtitle\qzone\chromedriver.exe')
        else:
            self.browser = webdriver.Chrome(chrome_options=self.chrome_options,
                                            executable_path=r'/usr/local/bin/chromedriver')
        self.browser.get(LOGIN_URL)
        time.sleep(8)
        # 获取cookie
        dictCookies = self.browser.get_cookies()
        try:
            if self.cookies_db.set(QQ, json.dumps(dictCookies)):
                print('Cookie保存成功')
                print('Cookie: ', dictCookies)
            else:
                print('Failed to save cookie!')
        except Exception as e:
            print(e.args)
        finally:
            self.browser.close()


if __name__ == '__main__':
    qq = QQShareFile()
