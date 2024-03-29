# -*- codeing = utf-8 -*-
# @Time : 2021/4/26 下午9:40
# @Author : Histranger
# @File : forms.py
# @Software: PyCharm
from email.policy import default
from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField, HiddenField, \
    DateField, RadioField
from wtforms.validators import DataRequired, Length, ValidationError, Email, Optional, URL, EqualTo

from hiblog.models import Category
from hiblog.utils import is_dict


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(8, 128)])
    captcha_code = StringField('Verification Code',
                               validators=[DataRequired(), Length(4, 4, message="Input verification code.")])
    remember = BooleanField('Remember me')
    submit = SubmitField('Log in')


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(1, 60)])
    date = DateField('Date', validators=[Optional()])
    category = SelectField('Category', validators=[DataRequired()], coerce=int, default=1)
    body = CKEditorField('Body', validators=[DataRequired()])
    is_secret = BooleanField('Make Post Secret')
    submit = SubmitField()

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.category.choices = [(category.id, category.name) for category in
                                 Category.query.order_by(Category.name).all()]


class CategoryForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(1, 30)])
    submit = SubmitField()

    def validate_name(self, field):
        if Category.query.filter_by(name=field.data).first():
            raise ValidationError("Category name already in use.")


class CommentForm(FlaskForm):
    author = StringField('Name', validators=[DataRequired(), Length(1, 30)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(1, 254)])
    site = StringField('Site', validators=[Optional(), URL(), Length(0, 255)])
    body = TextAreaField('Comment', validators=[DataRequired()])
    # css_dict = {
    #     'class': 'col-8 form-group',
    # }
    # captcha_code = StringField('Verification Code', validators=[DataRequired(), Length(4, 4, message="Input verification code.")],
    #                            render_kw=css_dict)
    captcha_code = StringField('Verification Code',
                               validators=[DataRequired(), Length(4, 4, message="Input verification code.")])
    submit = SubmitField()


class AdminCommentForm(CommentForm):
    author = HiddenField()
    email = HiddenField()
    site = HiddenField()
    captcha_code = None


class SettingForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(1, 30)])
    blog_title = StringField('Blog Title', validators=[DataRequired(), Length(1, 60)])
    blog_subtitle = StringField('Blog Sub Title', validators=[DataRequired(), Length(1, 100)])
    about = CKEditorField('About Page', validators=[DataRequired()])
    submit = SubmitField()


class PasswordResetForm(FlaskForm):
    reset_password = PasswordField("New Password",
                                   validators=[DataRequired(), Length(8, 128),
                                               EqualTo('reset_password2', message="Passwords must match.")])
    reset_password2 = PasswordField("Confirm New Password", validators=[DataRequired()])
    submit = SubmitField()


class MarkdownPostForm(PostForm):
    body = TextAreaField('Body', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super(MarkdownPostForm, self).__init__(*args, **kwargs)
        self.category.choices = [(category.id, category.name) for category in
                                 Category.query.order_by(Category.name).all()]


class AnswerForm(FlaskForm):
    title = StringField('Title', validators=[Length(0, 200)])
    # content = TextAreaField('Content', validators=[DataRequired()])  # ckeditor5
    # content = CKEditorField('Content', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    author = StringField('Author', validators=[Length(0, 200)])
    links = StringField('Links', validators=[is_dict()])
    note = StringField("Note")
    submit = SubmitField()
