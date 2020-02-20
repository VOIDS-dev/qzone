# wpkjmtmvvnacbiei
import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr


def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))


def send_mail():
    from_addr = '290868461@qq.com'  # input('From: ')
    password = 'kommcwxdcilkbjdc'  # input('Password: ')
    to_addr = 'andrew_wf@sina.cn'  # input('To: ')
    smtp_server = 'smtp.qq.com'  # input('SMTP server: ')

    msg = MIMEText('The qzone cookie is invalid, generate new cookie please!!!', 'plain', 'utf-8')
    msg['From'] = _format_addr('QZone Cookie: <%s>' % from_addr)
    msg['To'] = _format_addr('Notification: <%s>' % to_addr)
    msg['Subject'] = Header('QZone Cookie', 'utf-8').encode()

    server = smtplib.SMTP(smtp_server, 25)
    server.set_debuglevel(1)
    server.login(from_addr, password)
    server.sendmail(from_addr, [to_addr], msg.as_string())
    server.quit()
