# -*- codeing = utf-8 -*-
# @Time : 2021/12/11 下午12:41
# @Author : Histranger
# @File : emails.py
# @Software: PyCharm
from threading import Thread

from flask import current_app, url_for
from flask_mail import Message

from hiblog.extentions import mail


def _send_async_email(app, message):
    with app.app_context():
        mail.send(message)


def send_email(subject, to, html):
    app = current_app._get_current_object()
    message = Message(subject, recipients=[to], html=html)
    # with app.app_context():
    #     mail.send(message)
    thr = Thread(target=_send_async_email, args=[app, message])
    thr.start()
    return thr


def send_new_comment_email2admin(comment):
    url = url_for('admin.manage_comment', _external=True)
    send_email(subject='New comment',
               to=current_app.config['HIBLOG_EMAIL'],
               html='<p>New comment [{comment_body}]</i>, click the link below to check:</p>'
                    '<p><a href="{url}">{url}</a></P>'
                    '<p><small style="color: #868e96">Do not reply this email.</small></p>'
               .format(url=url, comment_body=comment.body)
               )


def send_admin_approve2visitor(comment):
    url = url_for("blog.show_post", post_id=comment.post.id, _external=True) + "#comments"
    send_email(subject='Comment Approved.',
               to=comment.email,
               html='<p>Dear {user_name},</p>'
                    '<p><strong>Thank you for your comment.</strong> It\'s very important to me!</p>'
                    '<p>You can click the following link to check your comments.</p>'
                    '<p><a href="{url}">{url}</a></p>'
                    '<p><small style="color: #868e96">Do not reply this email. The message was sent by a '
                    'ROBOT.</small></p> '
                    '<p><small style="color: #868e96">If you have any questions, please email to 1497058369@qq.com , '
                    'thx.</small></p> '
               .format(url=url, user_name=comment.author)
               )


def send_reply_comment2someone(reply_comment, comment):
    url = url_for("blog.show_post", post_id=reply_comment.post.id, _external=True) + "#comments"
    send_email(subject='Comment Approved.',
               to=reply_comment.email,
               html='<p>Dear {user_name},</p>'
                    '<p><strong>Your comment was replied by {reply_user}. </strong>Go and see what happened!</p>'
                    '<p>You can click the following link.</p>'
                    '<p><a href="{url}">{url}</a></p>'
                    '<p><small style="color: #868e96">Do not reply this email. The message was sent by a '
                    'ROBOT.</small></p> '
                    '<p><small style="color: #868e96">If you have any questions, please email to 1497058369@qq.com , '
                    'thx.</small></p> '
               .format(url=url, user_name=reply_comment.author, reply_user=comment.author)
               )
