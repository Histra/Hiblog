# -*- codeing = utf-8 -*-
# @Time : 2021/4/27 下午5:49
# @Author : Histranger
# @File : blog.py
# @Software: PyCharm
import collections

from flask import Blueprint, render_template, url_for, request, current_app, flash, redirect, abort, make_response, \
    session
from flask_login import current_user

from hiblog.extentions import db
from hiblog.forms import AdminCommentForm, CommentForm
from hiblog.models import Post, Category, Comment
from hiblog.utils import redirect_back

blog_bp = Blueprint('blog', __name__)


@blog_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['HIBLOG_POST_PER_PAGE']
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page=per_page)
    posts = pagination.items
    return render_template("blog/index.html", pagination=pagination, posts=posts)


@blog_bp.route('/post/<int:post_id>', methods=["POST", "GET"])
def show_post(post_id):
    post = Post.query.get_or_404(post_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['HIBLOG_COMMENT_PER_PAGE']
    pagination = Comment.query.with_parent(post).filter_by(reviewed=True).order_by(Comment.timestamp.asc()).paginate(
        page, per_page)
    comments = pagination.items

    if current_user.is_authenticated:
        form = AdminCommentForm()
        form.author.data = current_user.name
        form.email.data = current_app.config['HIBLOG_EMAIL']
        form.site.data = url_for('.index')
        from_admin = True
        reviewed = True
    else:
        form = CommentForm()
        from_admin = False
        reviewed = False

    reply_comment = None
    replied_id = request.args.get('reply')
    if replied_id:
        reply_comment = Comment.query.get_or_404(replied_id)

    # add session
    if not current_user.is_authenticated:
        if session.get("comment_author"):
            form.author.data = session.get("comment_author")
        if session.get("comment_email"):
            form.email.data = session.get("comment_email")
        if session.get("comment_site"):
            form.site.data = session.get("comment_site")
        if session.get("comment_body"):
            form.body.data = session.get("comment_body")
    if form.validate_on_submit():
        author = form.author.data
        email = form.email.data
        site = form.site.data
        body = form.body.data

        def insert2mysql():
            comment = Comment(
                author=author, email=email, site=site, body=body,
                from_admin=from_admin, post=post, reviewed=reviewed
            )
            if replied_id:
                comment.replied = reply_comment
                # sendMessage2TheUser
            db.session.add(comment)
            db.session.commit()

        if current_user.is_authenticated:
            insert2mysql()
            flash('Comment published.', 'success')
        else:
            session["comment_author"] = author
            session["comment_email"] = email
            session["comment_site"] = site
            session["comment_body"] = body
            captcha_code = session.get("captcha_code")
            if captcha_code == form.captcha_code.data.lower():
                insert2mysql()
                flash('Thanks, your comment will be published after reviewed.', 'info')
                for item in ["comment_author", "comment_email", "comment_site", "comment_body"]:
                    session.pop(item)
                # sendMessage2Histranger
            else:
                flash('Verification Code Error.', 'warning')
        return redirect(url_for('.show_post', post_id=post_id) + "#comments")

    return render_template('blog/post.html', post=post, pagination=pagination, comments=comments, form=form,
                           reply_comment_body=reply_comment.body if reply_comment else None)


@blog_bp.route('/category/<int:category_id>', methods=["POST", "GET"])
def show_category(category_id):
    category = Category.query.get_or_404(category_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['HIBLOG_POST_PER_PAGE']
    pagination = Post.query.with_parent(category).order_by(Post.timestamp.desc()).paginate(page, per_page=per_page)
    posts = pagination.items
    return render_template('blog/category.html', category=category, pagination=pagination, posts=posts)


@blog_bp.route("/reply/comment/<int:comment_id>")
def reply_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    return redirect(
        url_for('.show_post', post_id=comment.post_id, reply=comment_id, author=comment.author) + "#comment-form")


@blog_bp.route("/change-theme/<theme_name>")
def change_theme(theme_name):
    if theme_name not in current_app.config["HIBLOG_THEMES"].keys():
        abort(404)

    response = make_response(redirect_back())
    response.set_cookie('theme', current_app.config["HIBLOG_THEMES"][theme_name], max_age=30 * 24 * 60 * 60)
    return response


@blog_bp.route("/about")
def about():
    return render_template("blog/about.html")



