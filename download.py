# http://k2xmx.gyxza3.eymlz.com/a3/rj_sp1/suningxiaodian.apk

import os
import random
import platform
from contextlib import closing

import pymysql
import requests
from config import *

requests.packages.urllib3.disable_warnings()


class MySQL(object):
    def __init__(self):
        self.db = pymysql.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, port=MYSQL_PORT,
                                  db=MYSQL_DATABASE, charset='utf8')
        self.cursor = self.db.cursor()

    def query(self, sql):
        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            self.db.commit()
            return result
        except Exception as e:
            print(e.args)
            self.db.rollback()

    def update(self, sql):
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            print(e.args)
            self.db.rollback()

    def close(self):
        self.db.close()


class ProgressBar(object):
    def __init__(self, title, count=0.0, run_status=None, fin_status=None, total=100.0, unit='', sep='/',
                 chunk_size=1.0):
        super(ProgressBar, self).__init__()
        self.info = "[%s] %s %.2f %s %s %.2f %s"
        self.title = title
        self.total = total
        self.count = count
        self.chunk_size = chunk_size
        self.status = run_status or ""
        self.fin_status = fin_status or " " * len(self.statue)
        self.unit = unit
        self.seq = sep

    def __get_info(self):
        # 【名称】状态 进度 单位 分割线 总数 单位
        _info = self.info % (
            self.title, self.status, self.count / self.chunk_size, self.unit, self.seq, self.total / self.chunk_size,
            self.unit)
        return _info

    def refresh(self, count=1, status=None):
        self.count += count
        # if status is not None:
        self.status = status or self.status
        end_str = "\r"
        if self.count >= self.total:
            end_str = '\n'
            self.status = status or self.fin_status


def get_headers():
    user_agent_list = [
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    ]
    UserAgent = random.choice(user_agent_list)
    headers = {'User-Agent': UserAgent}
    return headers


def main():
    obj = MySQL()
    items = obj.query('select filename, url, gc, upload_uin, id from {}'.format(MYSQL_TABLE))
    for item in items:
        with closing(requests.get(item[1], headers=get_headers(), verify=False, stream=True)) as response:
            chunk_size = 1024  # 单次请求最大值
            content_size = int(response.headers['content-length'])  # 内容体总大小
            data_count = 0
            if platform.platform().startswith('Windows'):
                dirs = r'..\qqshare' + '\\' + item[2] + '\\' + item[3]
            else:
                dirs = '../qqshare' + '/' + item[2] + '/' + item[3]
            if not os.path.exists(dirs):
                os.makedirs(dirs)
            file_path = os.path.join(dirs, item[0])
            with open(file_path, "wb") as file:
                for data in response.iter_content(chunk_size=chunk_size):
                    file.write(data)
                    data_count = data_count + len(data)
                    now_jd = (data_count / content_size) * 100
                    print("\r 文件下载进度：%d%%(%d/%d) - %s" % (now_jd, data_count, content_size, file_path), end=" ")
            obj.update('update {table} set filepath="{filepath}" where id="{id}"'.format(
                table=MYSQL_TABLE,
                filepath=file_path.replace('\\', '\\\\'),
                id=item[4]))


if __name__ == '__main__':
    main()
