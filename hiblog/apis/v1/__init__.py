# -*- codeing = utf-8 -*-
# @Time : 2021/11/29 下午4:42
# @Author : Histranger
# @File : __init__.py.py
# @Software: PyCharm

from flask import Blueprint
from flask_cors import CORS

api_v1 = Blueprint('api_v1', __name__)

CORS(api_v1)

from hiblog.apis.v1 import resources
