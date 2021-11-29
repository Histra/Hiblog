# -*- codeing = utf-8 -*-
# @Time : 2021/11/29 下午12:44
# @Author : Histranger
# @File : answer.py
# @Software: PyCharm
import random

from flask import Blueprint, render_template, request, current_app, flash, redirect, url_for
from flask_login import login_required
from sqlalchemy import func

from hiblog.extentions import db
from hiblog.forms import AnswerForm
from hiblog.models import Answer

answer_bp = Blueprint('answer', __name__)


@answer_bp.route("/")
def index():
    # https://stackoverflow.com/questions/60805/getting-random-row-through-sqlalchemy
    answer = Answer.query.filter_by(status=0).order_by(func.random()).first()
    return render_template('answer/index.html', answer=answer)


@answer_bp.route("/manage_answer")
@login_required
def manage_answer():
    page = request.args.get('page', 1, type=int)
    pagination = Answer.query.order_by(Answer.id.asc()).paginate(
        page=page,
        per_page=current_app.config["HIBLOG_ANSWER_MANAGE_PER_PAGE"]
    )
    answers = pagination.items
    return render_template('answer/manage_answer.html', answers=answers, pagination=pagination)


@answer_bp.route("/new_answer", methods=["POST", "GET"])
@login_required
def new_answer():
    form = AnswerForm()
    if form.validate_on_submit():
        print("fds")
        title = form.title.data
        content = form.content.data
        author = form.author.data
        links = form.links.data
        note = form.note.data
        answer = Answer(
            title=title,
            content=content,
            author=author,
            links=links,
            note=note
        )
        db.session.add(answer)
        db.session.commit()
        flash("Answer Created.", "success")
        return redirect(url_for('answer.show_answer', answer_id=answer.id))
    return render_template('answer/new_answer.html', form=form)


@answer_bp.route("/show_answer/<int:answer_id>", methods=["POST", "GET"])
@login_required
def show_answer(answer_id):
    answer = Answer.query.get_or_404(answer_id)
    return render_template('answer/index.html', answer=answer)


@answer_bp.route("/edit_answer/<int:answer_id>", methods=["POST", "GET"])
def edit_answer(answer_id):
    answer = Answer.query.get_or_404(answer_id)
    form = AnswerForm()
    if form.validate_on_submit():
        answer.title = form.title.data
        answer.content = form.content.data
        answer.author = form.author.data
        answer.links = form.links.data
        answer.note = form.note.data
        db.session.commit()
        flash("Answer Created.", "success")
        return redirect(url_for('answer.show_answer', answer_id=answer.id))

    form.title.data = answer.title
    form.content.data = answer.content
    form.author.data = answer.author
    form.links.data = answer.links
    form.note.data = answer.note
    return render_template('answer/new_answer.html', form=form)
