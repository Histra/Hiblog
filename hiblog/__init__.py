# -*- codeing = utf-8 -*-
# @Time : 2021/4/26 下午6:51
# @Author : Histranger
# @File : __init__.py.py
# @Software: PyCharm
import os

import click
from flask import Flask, render_template, request, jsonify
from flask_login import current_user
from flask_wtf.csrf import CSRFError
from markdown import Markdown

from hiblog.apis.v1 import api_v1
from hiblog.blueprints.answer import answer_bp
from hiblog.blueprints.admin import admin_bp
from hiblog.blueprints.auth import auth_bp
from hiblog.blueprints.blog import blog_bp
from hiblog.extentions import db, moment, bootstrap, login_manager, csrf, ckeditor, mail
from hiblog.models import ForTest, Admin, Category, Post, Comment
from hiblog.settings import config


# https://2dogz.cn/blog/article/4/
from dotenv import load_dotenv
load_dotenv('.env')


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    app = Flask('hiblog')
    app.config.from_object(config[config_name])

    register_jinja2_filters(app)

    register_extensions(app)  # register extensions
    register_blueprints(app)  # register blueprints
    register_shell_context(app)  # register shell context
    register_commands(app)  # register flask commands
    register_template_context(app)  # register flask template context
    register_errors(app)  # register errors

    return app


def register_jinja2_filters(app):
    @app.template_filter()
    def string2list_dict(string):
        list_dict = [{'title': title, 'url': url} for title, url in eval(string).items()]
        return list_dict


def register_extensions(app):
    db.init_app(app)
    moment.init_app(app)
    bootstrap.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    csrf.exempt(api_v1)
    ckeditor.init_app(app)
    mail.init_app(app)
    from flaskext.markdown import Markdown
    markdown = Markdown(app)


def register_blueprints(app):
    app.register_blueprint(blog_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(answer_bp, url_prefix="/answer")
    app.register_blueprint(api_v1, url_prefix="/answer/api/v1")


def register_shell_context(app):
    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db, ForTest=ForTest, Admin=Admin, Category=Category, Post=Post, Comment=Comment)


def register_commands(app):
    @app.cli.command()
    def initdb():
        """Initialize the database"""
        db.create_all()
        click.echo("Initialized database.")

    @app.cli.command()
    @click.option("--category", default=10, help="Quantity of categories, default is 10.")
    @click.option("--post", default=50, help="Quantity of posts, default is 50.")
    @click.option("--comment", default=500, help="Quantity of comments, default is 500.")
    def forge(category, post, comment):
        """Generates the faker categories, posts, comments."""
        from hiblog.fakes import fake_admin, fake_categories, fake_posts, fake_comments

        # drop special tables (not use `db.drop_all()`)
        db.engine.execute("SET FOREIGN_KEY_CHECKS = 0;")
        db.engine.execute("drop table if exists admin;")
        db.engine.execute("drop table if exists category;")
        db.engine.execute("drop table if exists post;")
        db.engine.execute("drop table if exists comment;")
        db.engine.execute("SET FOREIGN_KEY_CHECKS = 1;")

        db.create_all()

        click.echo("Generating administrator...")
        fake_admin()
        click.echo("Generating {} categories...".format(category))
        fake_categories(category)
        click.echo("Generating {} posts...".format(post))
        fake_posts(post)
        click.echo("Generating {} comments...".format(comment))
        fake_comments(comment)

        click.echo("Done.")

    @app.cli.command()
    @click.option('--username', prompt=True, help="The username used to login.")
    @click.option('--password', prompt=True, help="The password used to login.", hide_input=True,
                  confirmation_prompt=True)
    def init(username, password):
        """Create HiBlog just for you."""
        click.echo("Initializing the HiBlog.")
        db.create_all()

        admin = Admin.query.first()
        if admin:
            click.echo("The administrator already exists, updating...")
            admin.username = username
            admin.set_password(password)
        else:
            admin = Admin(
                username=username,
                blog_title="HiBlog",
                blog_subtitle="Hi, stranger",
                name="Histranger",
                about="A man who likes Haocun Liu."
            )
            admin.set_password(password)
            db.session.add(admin)
        category = Category.query.first()
        if category is None:
            click.echo("Creating the default category...")
            category = Category(name="default")
            db.session.add(category)

        db.session.commit()
        click.echo("Done.")


def register_template_context(app):
    @app.context_processor
    def make_template_context():
        admin = Admin.query.first()
        categories = Category.query.order_by(Category.name).all()

        if current_user.is_authenticated:
            unread_comments = Comment.query.filter_by(reviewed=False).count()
        else:
            unread_comments = None

        return dict(admin=admin, categories=categories,
                    unread_comments=unread_comments)


def register_errors(app):
    @app.errorhandler(404)
    def errors_404(e):
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html or request.path.startswith(
                '/answer/api'):
            response = jsonify(code=404, message="You were LOST.")
            response.status_code = 404
            return response
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def errors_500(e):
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html or request.path.startswith(
                '/answer/api'):
            response = jsonify(code=500, message="An internal server error occurred.")
            response.status_code = 500
            return response
        return render_template('errors/500.html'), 500

    @app.errorhandler(405)
    def errors_405(e):
        """method not allowed"""
        response = jsonify(code=405, message="The method is not allowed for the requested URL.")
        response.status_code = 405
        return response

    @app.errorhandler(503)
    def errors_503(e):
        """method not allowed"""
        response = jsonify(code=503, message="Service Unavailable.")
        response.status_code = 503
        return response

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return render_template('errors/400.html', description=e.description), 400
