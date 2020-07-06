import json
import time
from datetime import datetime
from random import random

import pymysql
import requests
from config import *
from db import *
from mail import *
from requests.cookies import RequestsCookieJar
from multiprocessing import Process

requests.packages.urllib3.disable_warnings()


class QQShareFile(object):
    def __init__(self, prefix='cookies', website='qqzone'):
        self.website = website
        self.prefix = prefix
        self.cookies_db = RedisClient(self.prefix, self.website)
        self.db = pymysql.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, port=MYSQL_PORT,
                                  db=MYSQL_DATABASE)
        self.cursor = self.db.cursor()
        self.cookie_jar = RequestsCookieJar()
        value = 0
        str_cookies = self.cookies_db.get(QQ)
        dictCookies = json.loads(str_cookies)
        for i in range(0, len(dictCookies)):
            key = dictCookies[i]['name']
            if key == 'p_skey' or key == 'skey' or key == 'rv2':
                value = dictCookies[i]['value']
            self.cookie_jar.set(dictCookies[i]['name'], dictCookies[i]['value'], domain=dictCookies[i]['domain'])
        t = 5381
        for i in range(0, len(value)):
            t += (t << 5) + ord(value[i])
        self.g_tk = t & 2147483647

    def delete(self):
        """
        Delete cookie
        :return: None
        """
        if self.cookies_db:
            self.cookies_db.delete(QQ)

    def extract(self, splitstr):
        beg = splitstr.find('(')
        end = splitstr.rfind(');')
        retult = splitstr[beg + 1:end]
        return retult

    def get_group_list(self):
        params = {
            'groupcount': 4,
            'count': 4,
            'callbackFun': '_GetGroupPortal',
            'uin': QQ,
            'g_tk': str(self.g_tk),
            'ua': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'
        }

        response = requests.get(url=GROUP_LIST_URL, params=params, verify=False, headers=HEADERS,
                                cookies=self.cookie_jar, allow_redirects=False)
        if response.status_code == 200:
            resp = self.extract(response.text)
            return resp

    def get_group_share_info(self, response):
        print(response)
        jsonData = json.loads(response)
        items = jsonData['data']['group']
        for item in items:
            if groupid in target_group_list:
                groupid = item['groupid']
                params = {
                    'uin': QQ,
                    'groupid': groupid,
                    'bussinessid': 0,
                    'r': str(random.random()),
                    'charset': 'utf-8',
                    'g_tk': self.g_tk
                }
                response = requests.get(url=GROUP_FILE_SHARE_URL, params=params, verify=False, headers=HEADERS,
                                        cookies=self.cookie_jar, allow_redirects=False)
                if response.status_code == 200:
                    resp = self.extract(response.text)
                yield {
                    'response': resp,
                    'groupid': groupid
                }

    def get_file_download_url(self, d):
        jsonData = json.loads(d['response'])
        data = jsonData.get('data', None)
        if data is not None:
            items = data.get('item', None)
            if items is not None:
                for item in items:
                    params = {
                        'uin': QQ,
                        'groupid': d['groupid'],
                        'pa': item['filepath'],
                        'r': str(random.random()),
                        'charset': 'utf-8',
                        'g_tk': self.g_tk
                    }
                    response = requests.get(url=DOWNLOAD_URL, params=params, headers=HEADERS, verify=False,
                                            cookies=self.cookie_jar, allow_redirects=False)
                    if response.status_code == 200:
                        resp = self.extract(response.text)
                        jsonData = json.loads(resp)
                        try:
                            url = jsonData['data']['url']
                            yield {
                                'id': item['filepath'].split('/')[-1],
                                'create_time': datetime.strftime(datetime.utcfromtimestamp(int(item['createtime'])),
                                                                 '%Y-%m-%d %H:%M:%S'),
                                'filename': item['filename'],
                                'url': url,
                                'modify_time': datetime.strftime(datetime.utcfromtimestamp(int(item['modifytime'])),
                                                                 '%Y-%m-%d %H:%M:%S'),
                                'owner_nick': item['ownernick'],
                                'owner_uin': item['owneruin'],
                                'upload_nick': item['uploadnick'],
                                'upload_uin': item['uploaduin'],
                                'filepath': '',
                                'gc': d['groupid']
                            }
                        except:
                            continue

    def save_to_mysql(self, item):
        data = dict(item)
        print(data)
        keys = ', '.join(data.keys())
        values = ', '.join(['%s'] * len(data))
        sql = 'INSERT INTO {table}({keys}) VALUES ({values}) ON DUPLICATE KEY UPDATE'.format(table=MYSQL_TABLE,
                                                                                             keys=keys,
                                                                                             values=values)
        update = ','.join([" {key} = %s".format(key=key) for key in data])
        sql += update
        try:
            if self.cursor.execute(sql, tuple(data.values()) * 2):
                self.db.commit()
        except pymysql.MySQLError as e:
            print(e.args)
            self.db.rollback()

    def main(self):
        for item in self.get_group_share_info(self.get_group_list()):
            time.sleep(random.random() * 5)
            for ite in self.get_file_download_url(item):
                self.save_to_mysql(ite)


if __name__ == '__main__':
#     while True:
#         try:
            qq = QQShareFile()
            qq.main()
            time.sleep(300)
#         except Exception as e:
#             print(e.args)
#             p = Process(target=send_mail, args=())
#             p.start()
#             p.join()
#             time.sleep(300)
#             continue
#         finally:
#             qq.delete()
#             del qq
