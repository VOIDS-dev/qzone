QQ = '232742660'

#gourp list
target_group_list = ['192223812'];

# qzone代理地址
GET_QZONE_COOKIE_CMD = 'curl http://127.0.0.1:5000/qzone/random'

LOGIN_URL = 'https://qun.qq.com/'
GROUP_LIST_URL = 'https://qun.qq.com/cgi-bin/get_group_list?'
GROUP_FILE_SHARE_URL = 'https://qun.qq.com/cgi-bin/group_share_list?'
DOWNLOAD_URL = 'https://qun.qq.com/cgi-bin/group_share_get_downurl?'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}

# mysql configuration
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'password'
MYSQL_PORT = 3306
MYSQL_DATABASE = 'ica'
MYSQL_TABLE = 'qqshare'

# Redis configuration
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_PASSWORD = '*'
REDIS_DB = 2

#Onedrive configuration
redirect_uri = 'http://localhost:8080/'
client_secret = '~e.IK6pavvzc.TZ7st4Zy8LQI-wen1_k2t'
client_id='66f9a768-032a-489e-9b54-dc56672a7d6e'
api_base_url='https://api.onedrive.com/v1.0/'
graph_base_url = 'https://graph.microsoft.com/v1.0/'
scopes=['offline_access', 'files.readwrite.all']

token_base_url = 'https://login.live.com'
token_path = "/oauth20_token.srf"
grant_type = "authorization_code"

#local
base_folder = "/disk-content"

