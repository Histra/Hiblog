# -*- codeing = utf-8 -*-
# @Time : 2021/11/29 下午4:47
# @Author : Histranger
# @File : resources.py
# @Software: PyCharm
from flask import request, jsonify, g, current_app, url_for
from flask.views import MethodView
from sqlalchemy import func

from hiblog.apis.v1.auth import generate_token, auth_required
from hiblog.apis.v1.schemas import answer_item_schema, answer_items_schema
from hiblog.models import Admin, Answer
from hiblog.apis.v1 import api_v1
from hiblog.apis.v1.errors import api_abort


class AnswerIndexAPI(MethodView):

    def get(self):
        return jsonify({
            "api_version": "1.0",
            "api_base_url": url_for(".index", _external=True),
            "authentication_url": url_for(".token", _external=True),
            "answer_item_url": str(url_for(".answer_item", answer_id=1, _external=True)).rsplit('/', 1)[0].strip()
                               + "/{answer_id}",
            "answer_items_url": url_for(".answer_items", _external=True) + "{?page}",
            "answer_random_item": url_for(".answer_random_item", _external=True)
        })


class AuthTokenAPI(MethodView):

    def post(self):
        grant_type = request.form.get('grant_type')
        username = request.form.get('username')
        password = request.form.get('password')

        if grant_type is None or grant_type.lower() != 'password':
            return api_abort(400, message="The grant type must be password.")

        admin_user = Admin.query.filter_by(username=username).first()

        if admin_user is None or not admin_user.validate_password(password):
            return api_abort(400, message="Either the username or password was invalid.")

        token, expiration = generate_token(admin_user)

        response = jsonify({
            'access_token': token,
            'token_type': 'Bearer',
            'expires_in': expiration
        })
        response.headers['Cache-Control'] = 'no-store'
        response.headers['Pragma'] = 'no-cache'
        return response


class AnswerItemAPI(MethodView):
    decorators = [auth_required]

    def get(self, answer_id):
        """Get answer by answer.id"""
        answer_item = Answer.query.get_or_404(answer_id)
        admin_user = Admin.query.order_by(Admin.id).first()  # here maybe change.
        if g.current_user != admin_user:
            return api_abort(403)
        return jsonify(answer_item_schema(answer_item))


class AnswerRandomItemAPI(MethodView):
    decorators = [auth_required]

    def get(self):
        """Get answer by random"""
        answer_item = Answer.query.filter_by(status=0).order_by(func.random()).first()
        admin_user = Admin.query.order_by(Admin.id).first()  # here maybe change.
        if g.current_user != admin_user:
            return api_abort(403)
        return jsonify(answer_item_schema(answer_item))


class AnswerItemsAPI(MethodView):
    decorators = [auth_required]

    def get(self):
        """Get answers by page"""
        page = request.args.get('page', 1, type=int)
        pagination = Answer.query.order_by(Answer.id).paginate(
            page=page,
            per_page=current_app.config["HIBLOG_ANSWER_API_V1_PER_PAGE"]
        )
        answer_items = pagination.items
        current_url = url_for('.answer_items', page=page, _external=True)
        prev_url = url_for('.answer_items', page=page - 1, _external=True) if pagination.has_prev else None
        next_url = url_for('.answer_items', page=page + 1, _external=True) if pagination.has_next else None
        return jsonify(answer_items_schema(answer_items, current_url, prev_url, next_url, pagination))


api_v1.add_url_rule('/oauth', view_func=AnswerIndexAPI.as_view('index'), methods=["GET"])
api_v1.add_url_rule('/oauth/token', view_func=AuthTokenAPI.as_view('token'), methods=["POST"])
api_v1.add_url_rule('/oauth/answer_item/<int:answer_id>', view_func=AnswerItemAPI.as_view('answer_item'),
                    methods=["GET"])
api_v1.add_url_rule('/oauth/answer_items', view_func=AnswerItemsAPI.as_view('answer_items'), methods=["GET"])
api_v1.add_url_rule('/oauth/answer_random_item', view_func=AnswerRandomItemAPI.as_view('answer_random_item'), methods=["GET"])
