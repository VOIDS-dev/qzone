QQ = '2337956208'

# qzone代理地址
GET_QZONE_COOKIE_CMD = 'curl http://127.0.0.1:5000/qzone/random'

LOGIN_URL = 'http://qun.qzone.qq.com/'
GROUP_LIST_URL = 'http://qun.qzone.qq.com/cgi-bin/get_group_list?'
GROUP_FILE_SHARE_URL = 'http://qun.qzone.qq.com/cgi-bin/group_share_list?'
DOWNLOAD_URL = 'http://qun.qzone.qq.com/cgi-bin/group_share_get_downurl?'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}

# mysql configuration
MYSQL_HOST = '*'
MYSQL_USER = 'root'
MYSQL_PASSWORD = '*'
MYSQL_PORT = 3306
MYSQL_DATABASE = 'ica'
MYSQL_TABLE = 'qqshare'

# Redis configuration
REDIS_HOST = '*'
REDIS_PORT = 6379
REDIS_PASSWORD = '*'
REDIS_DB = 2