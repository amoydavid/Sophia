# -*- coding: utf-8 -*-
__author__ = 'liuwei'

import os

_basedir = os.path.abspath(os.path.dirname(__file__))
SECRET_KEY = 'testkey'

DEBUG = True

SECRET_KEY = 'testkey'
if DEBUG:
    SQLALCHEMY_DATABASE_URI = 'mysql://root@127.0.0.1:3306/basecamp'
else:
    SQLALCHEMY_DATABASE_URI = 'mysql://root@127.0.0.1:3306/basecamp'

DATABASE_CONNECT_OPTIONS = {}
THREADS_PER_PAGE = 15
TEMPLATE_FOLDER = os.path.join(_basedir, 'templates')
STATIC_FOLDER = os.path.join(_basedir, 'static')

SESSION_PATH = WHOOSH_INDEX = os.path.join(_basedir, 'appsession')

PERMANENT_SESSION_LIFETIME = 2 * 24 * 60 * 60

GLOBAL_SETTING = {'name': u'Sophia', 'debug': DEBUG}

UPLOAD_FOLDER = os.path.join(_basedir, 'upload')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'rar', 'doc', 'docx', 'zip', '7z'}
PIC_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
del os