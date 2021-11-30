# -*- codeing = utf-8 -*-
# @Time : 2021/4/26 下午9:44
# @Author : Histranger
# @File : utils.py
# @Software: PyCharm
import os
import random
import string

from PIL import Image, ImageFont, ImageDraw, ImageFilter
from wtforms import ValidationError

from hiblog.settings import StaticConfig

try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse, urljoin

from flask import request, redirect, url_for


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


class Captcha:
    # https://www.weiney.com/2108.html
    # https://www.liaoxuefeng.com/wiki/1016959663602400/1017785454949568
    random_letters = string.ascii_letters + string.digits
    block_size = 36
    captcha_len = 4
    offset = 3
    RGB_start, RGB_end = 50, 250
    line_num = 4
    line_width = 2

    width = block_size * captcha_len
    height = block_size
    font_size = block_size - offset * 2

    def generate_captcha(self):
        """Return (image, captcha_code.lower)"""
        # create an image, and set width, height and background-color
        img = Image.new('RGB', (self.width, self.height), '#f1f0f0')
        font = ImageFont.truetype(os.path.join(StaticConfig.hiblog_PATH, "static/fonts/FiraCode-Regular.ttf"), self.font_size)
        draw = ImageDraw.Draw(img)
        captcha_code = ""

        # generate a random captcha code and save it to image
        for i in range(self.captcha_len):
            code = random.choice(self.random_letters)
            captcha_code += code
            draw.text((self.block_size * i + self.offset, self.offset), text=code, font=font, fill=self.random_RGB())

        # Draw lines to strengthen verification
        for _ in range(self.line_num):
            x1 = random.randint(0, self.width // 2)
            y1 = random.randint(0, self.height // 2)
            x2 = random.randint(0, self.width)
            y2 = random.randint(self.height // 2, self.height)
            draw.line(((x1, y1), (x2, y2)), fill=self.random_RGB(), width=self.line_width)

        # Add filter
        img = img.filter(ImageFilter.EDGE_ENHANCE)

        return img, captcha_code.lower()

    def random_RGB(self):
        """Return RGB(_, _, _)"""
        return tuple(random.randint(self.RGB_start, self.RGB_end) for _ in range(3))
