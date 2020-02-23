# 功能简介
qzone工程是用来采集QQ群的共享文件信息, python使用版本：3.6.8，python3环境下应该都没有问题

## 第三方模块
```
redis
pymysql
selenium
requests
```

## 模块介绍
```
config.py       配置文件
db.py           封装了redis部分操作
cookieqzone.py  通过扫码登陆qzone并将cookie保存到redis
qzone.py        携带redis中保存的cookie访问目标网站，采集元数据，保存到mysql（循环采集）
download        从mysql读取到下载url，执行下载操作（下载链接有效性有时间限制）
mail.py         访问目标网站时，若cookie失效，则会发送邮件到指定邮箱
```

## 执行顺序
```
python cookieqzone.py && python qzone.py && python download.py
三个模块均可独立运行
```