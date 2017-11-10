#!/usr/bin/python
# coding=utf-8

import sys
reload(sys)
sys.setdefaultencoding('UTF-8')
sys.path.append('..')

import os
import re
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from scrapy.utils.project import get_project_settings

logger = logging.getLogger(__name__)


class QQ_SMTP(object):

    def __init__(self):
        # QQ SMTP 服务
        self.mail_host = ''  # 服务器
        self.mail_port = ''  # 端口
        self.mail_user = ''  # 用户名
        self.mail_pass = ''  # 口令，QQ邮箱的授权码，在QQ邮箱的设置中获取
        self.sender = ''     # 发送邮箱
        self.receivers = ''  # 接受邮箱
        self.msg = MIMEMultipart("alternative")

        self.init_settings()

    def init_settings(self):
        """
        初始化设置
        """
        settings = get_project_settings()
        self.mail_host = settings.get('MAIL_HOST', 'smtp.qq.com')
        self.mail_port = settings.get('MAIL_PORT', 465)
        self.mail_user = settings.get('MAIL_USER', 'tan-xiaoli@qq.com')
        self.mail_pass = settings.get('MAIL_PASS', 'qgufuxhoxslubhjj')
        self.set_sender(settings.get('MAIL_SENDER', 'tan-xiaoli@qq.com'))
        self.set_receivers(settings.get('MAIL_RECEIVERS', '389210522@qq.com'))

    def _check_email_address(self, email_address):
        """
        检查email_address是否合法
        """
        if re.match(r"^[0-9a-zA-Z_-]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}$", email_address):
            return True
        else:
            return False

    def set_sender(self, sender):
        if sender and self._check_email_address(sender):
            self.sender = sender

    def set_receivers(self, receivers):
        if receivers:
            if isinstance(receivers, str) and self._check_email_address(receivers):
                self.receivers = receivers
            elif isinstance(receivers, list):
                for rec in receivers:
                    if not self._check_email_address(rec):
                        return -1
                self.receivers = ",".join(receivers)

    def set_subject_info(self, subject):
        self.msg["Subject"] = Header(subject, "utf-8")
        self.msg["From"] = Header(self.sender, "utf-8")
        self.msg["To"] = Header(self.receivers, "utf-8")

    def set_text(self, text=""):
        _text = MIMEText(text, "plain", "utf-8")
        self.msg.attach(_text)

    def set_html(self, html=""):
        _html = MIMEText(html, "html", "utf-8")
        self.msg.attach(_html)

    def attach_file(self, file_path):
        attachment = MIMEText(open(file_path, "rb").read(), "base64", "utf-8")
        attachment["Content-Type"] = "application/octet-stream"
        attachment["Content-Disposition"] = "attachment; filename=\"%s\"" % os.path.basename(file_path)
        self.msg.attach(attachment)

    def m_send(self):
        try:
            smtpobj = smtplib.SMTP_SSL(self.mail_host, self.mail_port)
            smtpobj.login(self.mail_user, self.mail_pass)
            smtpobj.sendmail(self.sender, self.receivers, self.msg.as_string())
            smtpobj.quit()
            logger.debug('Send the email [%s] successfully!' % self.subject)
            return 0
        except smtplib.SMTPException as e:
            traceback.print_exc()
            logger.error('Sent the email [%s] failed!' % self.subject)
            return -1

    def send(self, subject, body):
        self.set_subject_info(subject)
        self.set_text(body)
        logger.debug('subject=%s\ncontent=%s' % (self.msg['Subject'], body))

        try:
            smtpobj = smtplib.SMTP_SSL(self.mail_host, self.mail_port)
            smtpobj.login(self.mail_user, self.mail_pass)
            smtpobj.sendmail(self.sender, self.receivers, self.msg.as_string())
            smtpobj.quit()
            logger.debug('Send the email [%s] successfully' % subject)
            return 0
        except smtplib.SMTPException as e:
            traceback.print_exc()
            logger.error('Sent the email [%s] failed!' % subject)
            return -1


def test():
    qq_email = QQ_SMTP()
    qq_email.set_sender("tan-xiaoli@qq.com")
    qq_email.set_receivers(["tan-xiaoli@qq.com", "389210522@qq.com"])
    qq_email.set_subject_info("我的新测试")
    qq_email.set_text("Hi!\nHow are you?\nHere is the link you wanted:\nhttps://www.python.org")  # text和html不能同时添加
    # qq_email.set_html("""<html><head></head><body><p>你好！<br>怎么样了?<br></body></html>""")
    qq_email.attach_file("./lib_tools.py")
    qq_email.m_send()


if __name__ == "__main__":
    test()
    print "End the script!"
