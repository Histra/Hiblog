# -*- codeing = utf-8 -*-
# @Time : 2021/4/26 下午9:39
# @Author : Histranger
# @File : extentions.py
# @Software: PyCharm
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

db = SQLAlchemy()
moment = Moment()
bootstrap = Bootstrap()
login_manager = LoginManager()
csrf = CSRFProtect()
ckeditor = CKEditor()
mail = Mail()


@login_manager.user_loader
def load_user(user_id):
    from hiblog.models import Admin
    user = Admin.query.get(int(user_id))
    return user


login_manager.login_view = "auth.login"
login_manager.login_message_category = "warning"
