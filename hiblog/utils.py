# -*- codeing = utf-8 -*-
# @Time : 2021/4/26 下午9:44
# @Author : Histranger
# @File : utils.py
# @Software: PyCharm
from wtforms import ValidationError

try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse, urljoin

from flask import request, redirect, url_for, current_app


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def redirect_back(default='blog.index', **kwargs):
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))


def is_dict(message=None):
    if message is None:
        message = "Must be Python Dict."

    def _is_dict(form, field):
        nonlocal message
        if field.data:
            try:
                dict_type = eval(field.data)
            except Exception as e:
                message = message + f" | {str(e)}"
                raise ValidationError(message)
            else:
                if not isinstance(dict_type, dict):
                    raise ValidationError(message)

    return _is_dict



