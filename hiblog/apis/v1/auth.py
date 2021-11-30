# -*- codeing = utf-8 -*-
# @Time : 2021/11/29 下午4:52
# @Author : Histranger
# @File : auth.py
# @Software: PyCharm
from flask import current_app, request, g
from functools import wraps
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired

from hiblog.models import Admin
from hiblog.apis.v1.errors import api_abort, token_missing, invalid_token


def generate_token(user):
    expiration = 3600
    s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
    token = s.dumps({'id': user.id}).decode('ascii')
    return token, expiration


def get_token():
    if 'Authorization' in request.headers:
        try:
            token_type, token = request.headers['Authorization'].split(None, 1)
        except ValueError:
            token_type = token = None
    else:
        token_type = token = None
    return token_type, token


def validate_token(token):
    s = Serializer(current_app.config["SECRET_KEY"])
    try:
        data = s.loads(token)
    except (BadSignature, SignatureExpired):
        return False
    admin_user = Admin.query.get(data['id'])
    if admin_user is None:
        return False
    g.current_user = admin_user
    return True


def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token_type, token = get_token()
        print(token, "\n", token_type)
        if request.method != 'OPTIONS':
            if token_type is None or token_type.lower() != 'bearer':
                return api_abort(400, 'The token type must be bearer.')
            if token is None:
                return token_missing()
            if not validate_token(token):
                return invalid_token()
        return f(*args, **kwargs)
    return decorated
