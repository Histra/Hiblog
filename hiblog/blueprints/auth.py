# -*- codeing = utf-8 -*-
# @Time : 2021/4/27 下午5:49
# @Author : Histranger
# @File : auth.py
# @Software: PyCharm
from flask import Blueprint, redirect, url_for, flash, render_template
from flask_login import current_user, login_user, login_required, logout_user

from hiblog.models import Admin
from hiblog.forms import LoginForm
from hiblog.utils import redirect_back

auth_bp = Blueprint('auth', __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('blog.index'))

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data
        admin = Admin.query.first()
        if admin:
            if username == admin.username and admin.validate_password(password):
                login_user(admin, remember)
                flash("Welcome back, {} !".format(username), "success")
                return redirect_back()
            flash('Invalid username or password.', 'warning')
        else:
            flash('No Admin account', 'waring')

    return render_template('auth/login.html', form=form)


@auth_bp.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    print("Fda")
    flash("Logout success.", "info")
    return redirect_back()

