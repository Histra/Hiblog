# -*- codeing = utf-8 -*-
# @Time : 2021/11/29 下午7:19
# @Author : Histranger
# @File : schemas.py
# @Software: PyCharm
from flask import url_for


def answer_item_schema(answer_item):
    return {
        'id': answer_item.id,
        'self': url_for('.answer_item', answer_id=answer_item.id, _external=True),
        'kind': 'Answer Item',
        'title': answer_item.title,
        'content': answer_item.content,
        'author': answer_item.author,
        'link': [{'title': title, 'url': url} for title, url in eval(answer_item.links).items()] if answer_item.links else [],
        'status': answer_item.status
    }


def answer_items_schema(answer_items, current_url, prev_url, next_url, pagination):
    return {
        'self': current_url,
        'kind': 'Answer Items',
        'items': [answer_item_schema(answer_item) for answer_item in answer_items],
        'prev': prev_url,
        'next': next_url,
        'total': pagination.total
    }
