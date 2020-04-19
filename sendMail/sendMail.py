# メール送信
from email.utils import formatdate
from email.mime.text import MIMEText
import smtplib

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587


def create_message(from_addr, to_addr, cc_addr, bcc_addr, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Cc'] = cc_addr
    msg['Bcc'] = bcc_addr
    msg['Date'] = formatdate()
    return msg

# def send( loginAdr, loginPW, from_addr, to_addrs, msg):


def send(loginAdr, loginPW, msg):
    smtpobj = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    smtpobj.set_debuglevel(False)
    smtpobj.ehlo()
    smtpobj.starttls()
    smtpobj.ehlo()
    smtpobj.login(loginAdr, loginPW)
    smtpobj.send_message(msg)
    # smtpobj.sendmail(from_addr, to_addrs, msg.as_string())
    smtpobj.quit()
