# coding=utf-8
__author__ = 'liuwei'
import time
from gfm import gfm
from markdown import markdown


def datetimeformat(value, time_format='%Y-%m-%d %H:%M'):
    """
    格式化时间戳
    :type value: int
    :type time_format: str
    """
    return time.strftime(time_format, time.localtime(value))


def weekday(value):
    weekdays = [u'周天', u'周一', u'周二', u'周三', u'周四', u'周五', u'周六']
    weekindex = int(time.strftime('%w', time.localtime(value)))
    return weekdays[weekindex]


def friendly_datetime(value):
    current_time = time.time()
    if time.strftime('%Y%m%d', time.localtime(value)) == time.strftime('%Y%m%d', time.localtime(current_time)):
        return time.strftime("%H:%M", time.localtime(value))
    elif time.strftime('%Y%m', time.localtime(value)) == time.strftime('%Y%m', time.localtime(current_time)):
        date = time.localtime(value)
        return u"%s月%s日" % (date.tm_mon, date.tm_mday)
    else:
        return time.strftime("%Y-%m-%d", time.localtime(value))


def format_gfm(value):
    return markdown(gfm(value))