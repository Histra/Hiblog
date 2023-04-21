# -*- codeing = utf-8 -*-
# @Time : 2021/4/27 下午5:48
# @Author : Histranger
# @File : admin.py
# @Software: PyCharm
import markdown
from flask import Blueprint, render_template, request, current_app, flash, redirect, url_for
from flask_login import login_required, current_user

from hiblog.emails import send_admin_approve2visitor, send_reply_comment2someone
from hiblog.extentions import db
from hiblog.forms import PostForm, CategoryForm, SettingForm, MarkdownPostForm, PasswordResetForm
from hiblog.models import Post, Category, Comment, Admin
from hiblog.utils import redirect_back

admin_bp = Blueprint('admin', __name__)


@admin_bp.route("/post/new", methods=['POST', 'GET'])
@login_required
def new_post():
    # markdown
    post_type = request.args.get('post_type')

    if post_type == 'markdown':
        form = MarkdownPostForm()
        if form.validate_on_submit():
            title = form.title.data
            body = form.body.data
            category = Category.query.get(form.category.data)
            post = Post(
                title=title,
                body=body,
                category=category,
                type=post_type,
            )
            db.session.add(post)
            db.session.commit()
            flash("Markdown Post Created.", "success")
            return redirect(url_for('blog.show_post', post_id=post.id))
        return render_template('admin/new_markdown_post.html', form=form)
    else:
        form = PostForm()
        if form.validate_on_submit():
            title = form.title.data
            body = form.body.data
            category = Category.query.get(form.category.data)
            timestamp = form.date.data
            is_secret = form.is_secret.data
            # print(timestamp)
            post = Post(
                title=title,
                body=body,
                category=category,
                timestamp=timestamp,
                is_secret=is_secret,
            )
            db.session.add(post)
            db.session.commit()
            flash("Post Created.", "success")
            return redirect(url_for('blog.show_post', post_id=post.id))
        return render_template('admin/new_post.html', form=form)


@admin_bp.route("/post/<int:post_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    # markdown
    if post.type == 'markdown':
        form = MarkdownPostForm()
        if form.validate_on_submit():
            post.title = form.title.data
            post.body = form.body.data
            post.category = Category.query.get(form.category.data)
            db.session.commit()
            flash('Post updated.', 'success')
            return redirect(url_for('blog.show_post', post_id=post.id))

        form.title.data = post.title
        form.body.data = post.body
        form.category.data = post.category_id

        return render_template('admin/edit_markdown_post.html', form=form)
    else:
        form = PostForm()
        if form.validate_on_submit():
            post.title = form.title.data
            post.body = form.body.data
            post.category = Category.query.get(form.category.data)
            post.timestamp = form.date.data
            post.is_secret = form.is_secret.data
            print(post.is_secret, form.is_secret.data)
            db.session.commit()
            flash('Post updated.', 'success')
            return redirect(url_for('blog.show_post', post_id=post.id))

        form.title.data = post.title
        form.body.data = post.body
        form.category.data = post.category_id
        form.date.data = post.timestamp
        form.is_secret.data = post.is_secret
        
        return render_template('admin/edit_post.html', form=form)


@admin_bp.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash("Post deleted.", 'success')
    return redirect_back()


@admin_bp.route("/post/<int:post_id>/set-comment", methods=['POST'])
@login_required
def set_comment(post_id):
    post = Post.query.get_or_404(post_id)
    if post.can_comment:
        post.can_comment = False
        flash("Comment disabled.", 'info')
    else:
        post.can_comment = True
        flash("Comment enabled.", 'info')
    db.session.commit()
    return redirect(url_for('blog.show_post', post_id=post.id))


@admin_bp.route("/post/manage")
@login_required
def manage_post():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page=page,
        per_page=current_app.config["HIBLOG_MANAGE_POST_PER_PAGE"]
    )
    posts = pagination.items
    return render_template('admin/manage_post.html', pagination=pagination, posts=posts)


@admin_bp.route("/category/new", methods=["POST", "GET"])
@login_required
def new_category():
    form = CategoryForm()

    if form.validate_on_submit():
        name = form.name.data
        category = Category(
            name=name
        )
        db.session.add(category)
        db.session.commit()
        flash('Category created.', 'success')
        return redirect(url_for(".manage_category", category_id=category.id))

    return render_template('admin/new_category.html', form=form)


@admin_bp.route("/category/manage")
@login_required
def manage_category():
    page = request.args.get('page', 1, type=int)

    tmp_dict = {'id': Category.id, 'name': Category.name}
    order_by = tmp_dict[request.args.get('order_by', 'id')]

    pagination = Category.query.order_by(order_by).paginate(
        page=page,
        per_page=current_app.config["HIBLOG_MANAGE_CATEGORY_PER_PAGE"]
    )
    categories = pagination.items
    return render_template('admin/manage_category.html', pagination=pagination, categories=categories)


@admin_bp.route("/category/<int:category_id>/edit", methods=["POST", "GET"])
@login_required
def edit_category(category_id):
    category = Category.query.get_or_404(category_id)
    form = CategoryForm()
    if category_id == 1:
        flash('You can not edit the Default category.', 'warning')
        return redirect(url_for('.manage_category'))

    if form.validate_on_submit():
        old_category_name = category.name
        category.name = form.name.data
        db.session.commit()
        flash("Update Category : {} -> {} .".format(old_category_name, category.name), 'success')
        return redirect(url_for(".manage_category"))

    form.name.data = category.name
    return render_template("admin/edit_category.html", form=form)


@admin_bp.route("/category/<int:category_id>/delete", methods=['POST'])
@login_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    if category.id == 1:
        flash("You can not delete the Default category.", "warning")
        return redirect(url_for('.manage_category'))

    def move_and_delete():
        default_category = Category.query.get(1)
        posts = category.posts[
                :]  # attention : must use this to convert  <class 'sqlalchemy.orm.collections.InstrumentedList'> to <class 'list'>
        for post in posts:
            post.category = default_category
        db.session.delete(category)
        db.session.commit()

    # category.delete()
    move_and_delete()

    flash("Category {} deleted.".format(category.name), 'success')
    return redirect(url_for('.manage_category'))


@admin_bp.route("/comment/manage")
@login_required
def manage_comment():
    filter_rule = request.args.get('filter', 'all')
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config["HIBLOG_MANAGE_COMMENT_PER_PAGE"]
    if filter_rule == 'unread':
        filter_comments = Comment.query.filter_by(reviewed=False)
    elif filter_rule == "admin":
        filter_comments = Comment.query.filter_by(from_admin=True)
    else:
        filter_comments = Comment.query

    pagination = filter_comments.order_by(Comment.timestamp.desc()).paginate(
        page=page,
        per_page=per_page
    )
    comments = pagination.items

    disable_all = Post.query.filter(Post.can_comment == 1).first()
    if disable_all is None:
        disable_all = False
    else:
        disable_all = True
    return render_template("admin/manage_comment.html", pagination=pagination, comments=comments, disable_all=disable_all)


@admin_bp.route("/comment/manage/disable_all_comments/<int:disable_all>", methods=["POST"])
@login_required
def disable_all_comments(disable_all):
    disable_all = bool(disable_all)
    for post in Post.query.all():
        if disable_all:
            post.can_comment = 0
        else:
            post.can_comment = 1
    db.session.commit()

    return redirect(url_for('.manage_comment'))

@admin_bp.route("/comment/<int:comment_id>/delete", methods=["POST"])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted.', 'success')
    return redirect_back()


@admin_bp.route("/comment/<int:comment_id>/approve", methods=["POST"])
@login_required
def approve_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    comment.reviewed = True
    db.session.commit()
    send_admin_approve2visitor(comment)
    reply_comment = comment.replied
    if reply_comment and not reply_comment.from_admin:
        send_reply_comment2someone(reply_comment, comment)

    flash('Comment published.', 'success')
    return redirect_back()


@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    setting_form = SettingForm()
    password_reset_form = PasswordResetForm()
    if setting_form.submit.data and setting_form.validate_on_submit():
        current_user.name = setting_form.name.data
        current_user.blog_title = setting_form.blog_title.data
        current_user.blog_subtitle = setting_form.blog_subtitle.data
        current_user.about = setting_form.about.data
        db.session.commit()
        flash('Setting updated.', 'success')
        return redirect(url_for('blog.index'))
    if password_reset_form.submit.data:
        if password_reset_form.validate_on_submit():
            admin = Admin.query.get_or_404(current_user.id)
            new_password = password_reset_form.reset_password.data
            admin.set_password(new_password)
            db.session.commit()
            flash('Password resettled.', 'success')
            return redirect(url_for('blog.index'))
        else:
            flash('Passwords must equal.', 'warning')
            return redirect(url_for('admin.settings'))

    setting_form.name.data = current_user.name
    setting_form.blog_title.data = current_user.blog_title
    setting_form.blog_subtitle.data = current_user.blog_subtitle
    setting_form.about.data = current_user.about
    return render_template('admin/settings.html', setting_form=setting_form, password_reset_form=password_reset_form)
