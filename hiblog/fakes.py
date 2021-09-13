# -*- codeing = utf-8 -*-
# @Time : 2021/4/26 下午9:39
# @Author : Histranger
# @File : fakes.py
# @Software: PyCharm
import random

from faker import Faker

from hiblog.extentions import db
from hiblog.models import Admin, Category, Post, Comment

faker = Faker()


def fake_admin():
    admin = Admin(
        username="admin",
        blog_title="HiBlog",
        blog_subtitle="Hi, stranger",
        name="Histranger",
        about="A man who likes Haocun Liu."
    )
    admin.set_password("admin12345")

    db.session.add(admin)
    db.session.commit()


def fake_categories(count=10):
    category = Category(name="Default")
    db.session.add(category)
    db.session.commit()

    for i in range(count):
        category = Category(name=faker.word())
        db.session.add(category)
        try:
            db.session.commit()
        except Exception as e:
            print(str(e))
            db.session.rollback()


def fake_posts(count=50):
    for i in range(count):
        post = Post(
            title=faker.sentence(),
            body=faker.text(2000),
            category=Category.query.get(random.randint(1, Category.query.count())),
            timestamp=faker.date_time_this_year()
        )
        db.session.add(post)

    db.session.commit()


def fake_comments(count=500):
    for i in range(count):
        comment = Comment(
            author=faker.name(),
            email=faker.email(),
            site=faker.url(),
            body=faker.sentence(),
            timestamp=faker.date_time_this_year(),
            reviewed=True,
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)

    salt = int(count * 0.1)
    for i in range(salt):
        # un-reviewed comments
        comment = Comment(
            author=faker.name(),
            email=faker.email(),
            site=faker.url(),
            body=faker.sentence(),
            timestamp=faker.date_time_this_year(),
            reviewed=False,
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)

        # admin comments
        comment = Comment(
            author="Histanger",
            email="1497058369@qq.com",
            site="histranger.com",
            body=faker.sentence(),
            timestamp=faker.date_time_this_year(),
            from_admin=True,
            reviewed=True,
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)

    db.session.commit()

    # relies
    for i in range(salt):
        comment = Comment(
            author=faker.name(),
            email=faker.email(),
            site=faker.url(),
            body=faker.sentence(),
            timestamp=faker.date_time_this_year(),
            reviewed=True,
            replied=Comment.query.get(random.randint(1, Comment.query.count())),
            post=Post.query.get(random.randint(1, Post.query.count())),
        )
        db.session.add(comment)

    db.session.commit()
