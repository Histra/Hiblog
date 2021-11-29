# -*- codeing = utf-8 -*-
# @Time : 2021/11/29 下午4:52
# @Author : Histranger
# @File : errors.py
# @Software: PyCharm
from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES


def api_abort(code, message=None, **kwargs):
    if message is None:
        message = HTTP_STATUS_CODES.get(code, '')

    response = jsonify(code=code, message=message, **kwargs)
    response.status_code = code
    return response  # You can also just return (response, code) tuple


def invalid_token():
    response = api_abort(401, error='invalid_token', error_description='Either the token was expired or invalid.')
    response.headers['WWW-Authenticate'] = 'Bearer'
    return response


def token_missing():
    response = api_abort(401)
    response.headers["WWW-Authenticate"] = "Bearer"
    return response