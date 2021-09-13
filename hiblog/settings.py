# -*- codeing = utf-8 -*-
# @Time : 2021/4/26 下午9:42
# @Author : Histranger
# @File : settings.py
# @Software: PyCharm
import os

# https://2dogz.cn/blog/article/4/
from dotenv import load_dotenv
load_dotenv('.env')

MYSQL_USERNAME = os.getenv('MYSQL_USERNAME', 'hiblog')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'You guess.')
MYSQL_HOST = os.getenv('MYSQL_HOST', 'You guess.')
MYSQL_DATABASE_NAME = os.getenv('MYSQL_DATABASE_NAME', 'hiblog')


class BaseConfig(object):
    SECRET_KEY = os.getenv('SECRET_KEY', 'histranger')

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    HIBLOG_POST_PER_PAGE = 5
    HIBLOG_COMMENT_PER_PAGE = 10
    HIBLOG_MANAGE_POST_PER_PAGE = 10
    HIBLOG_MANAGE_CATEGORY_PER_PAGE = 5
    HIBLOG_MANAGE_COMMENT_PER_PAGE = 20

    HIBLOG_EMAIL = "1497058369@qq.com"

    HIBLOG_THEMES = {'default': 'bootstrap.min.css',
                      'morph': 'morph_bootstrap.min.css',
                      'cyborg': 'cyborg_bootstrap.min.css'}


class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@{}/{}'. \
        format(MYSQL_USERNAME, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_DATABASE_NAME)


class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@{}/{}'. \
        format(MYSQL_USERNAME, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_DATABASE_NAME)


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
