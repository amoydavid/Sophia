#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from config import SMTP_SETTING
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText

# python 2.3.*: email.Utils email.Encoders
from email.utils import COMMASPACE, formatdate
from email import encoders

import os


def send_html_mail(to, subject, html, text=None, files=None):
    fro = SMTP_SETTING['from']
    if not files:
        files = []
    assert type(files) == list
    if isinstance(to, str):
        to = [to]

    msg = MIMEMultipart('alternatvie')
    msg['From'] = fro
    msg['Subject'] = Header(subject, charset='utf-8')
    #COMMASPACE==', '
    msg['To'] = COMMASPACE.join(to)
    msg['Date'] = formatdate(localtime=True)

    #实例化为html部分
    html_part = MIMEText(html, 'html')
    #设置编码
    html_part.set_charset('utf-8')

    if text:
        msg.attach(MIMEText(text))
    msg.attach(html_part)

    for _file in files:
        #'octet-stream': binary data
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(open(_file, 'rb'.read()))
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(_file))
        msg.attach(part)

    import smtplib

    smtp = smtplib.SMTP(SMTP_SETTING['host'])
    smtp.login(SMTP_SETTING['user'], SMTP_SETTING['password'])
    smtp.sendmail(fro, to, msg.as_string())
    smtp.close()


#server['name'], server['user'], server['passwd']
def send_mail(to, subject, text, files=None):
    fro = SMTP_SETTING['from']
    if not files:
        files = []
    assert type(files) == list
    if isinstance(to, str):
        to = [to]

    msg = MIMEMultipart()
    msg['From'] = fro
    msg['Subject'] = Header(subject, charset='utf-8')
    #COMMASPACE==', '
    msg['To'] = COMMASPACE.join(to)
    msg['Date'] = formatdate(localtime=True)
    msg.attach(MIMEText(text))

    for _file in files:
        #'octet-stream': binary data
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(open(_file, 'rb'.read()))
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(_file))
        msg.attach(part)

    import smtplib

    smtp = smtplib.SMTP(SMTP_SETTING['host'])
    smtp.login(SMTP_SETTING['user'], SMTP_SETTING['password'])
    smtp.sendmail(fro, to, msg.as_string())
    smtp.close()