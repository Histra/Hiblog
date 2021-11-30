# -*- codeing = utf-8 -*-
# @Time : 2021/4/27 下午5:49
# @Author : Histranger
# @File : auth.py
# @Software: PyCharm
import base64
from io import BytesIO

from flask import Blueprint, redirect, url_for, flash, render_template, make_response, session, request, jsonify
from flask_login import current_user, login_user, login_required, logout_user

from hiblog.models import Admin
from hiblog.forms import LoginForm
from hiblog.utils import redirect_back, Captcha

auth_bp = Blueprint('auth', __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('blog.index'))

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        captcha_code = form.captcha_code.data
        if session["captcha_code"] == captcha_code.lower():
            remember = form.remember.data
            admin = Admin.query.first()
            if admin:
                if username == admin.username and admin.validate_password(password):
                    login_user(admin, remember)
                    flash("Welcome back, {} !".format(username), "success")
                    return redirect_back()
                flash('Invalid username or password.', 'warning')
            else:
                flash('No Admin account', 'warning')
        else:
            flash('Verification Code Error.', 'warning')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/captcha')
def captcha():
    captcha_type = request.args.get('type', 'image')
    if captcha_type in ["image", "base64"]:
        image, captcha_code = Captcha().generate_captcha()
        session["captcha_code"] = captcha_code
        buffer = BytesIO()
        image.save(buffer, "png")
        buffer_str = buffer.getvalue()
        if captcha_type == 'image':
            response = make_response(buffer_str)
            response.headers['Content-Type'] = 'image/gif'
            return response
        elif captcha_type == "base64":
            image_base64 = base64.b64encode(buffer_str)
            image_base64 = image_base64.decode("utf-8")
            src_format = "data:image/jpg;base64,{}"
            return jsonify({
                "base64": src_format.format(image_base64)
            })

    return render_template('errors/404.html')


@auth_bp.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("Logout success.", "info")
    return redirect_back()
