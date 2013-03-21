# -*- coding: utf-8 -*-
__author__ = 'liuwei'

import os

# 设置开始
DEBUG = True
GLOBAL_SETTING = {'name': u'Sophia', 'debug': DEBUG}
SECRET_KEY = 'testkey'
SQLALCHEMY_DATABASE_URI = 'mysql://root@127.0.0.1:3306/basecamp'
SMTP_SETTING = {
    'host': '',
    'from': '',
    'user': '',
    'password': ''
}
# 设置结束

# 以下部分请慎重修改
_basedir = os.path.abspath(os.path.dirname(__file__))
DATABASE_CONNECT_OPTIONS = {}
THREADS_PER_PAGE = 15
TEMPLATE_FOLDER = os.path.join(_basedir, 'templates')
STATIC_FOLDER = os.path.join(_basedir, 'static')
SESSION_PATH = WHOOSH_INDEX = os.path.join(_basedir, 'appsession')
PERMANENT_SESSION_LIFETIME = 2 * 24 * 60 * 60
UPLOAD_FOLDER = os.path.join(_basedir, 'upload')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'rar', 'doc', 'docx', 'zip', '7z'}
PIC_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
AVATAR_FOLDER = os.path.join(UPLOAD_FOLDER, 'avatar')
BASE_DIR = _basedir

local_config_file = os.path.join(_basedir, 'local_config.py')
if os.path.exists(local_config_file):
    from local_config import *
del os