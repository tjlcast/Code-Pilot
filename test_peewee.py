#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# @Time 2023/11/7 S{TIME} 
# @Name test. Py
# @Author：jialtang


from peewee import *

db = SqliteDatabase('mydatabase.db')


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    username = CharField(unique=True)
    email = CharField()


class BlogPost(BaseModel):
    title = CharField()
    content = TextField()
    author = ForeignKeyField(User, backref='blog_posts')


def get_start():
    db.create_tables([User, BlogPost])

    # 添加新用户
    user = User(username='john', email='john@example.com')
    user.save()

    # 查询用户
    for user in User.select():
        print(user.username, user.email)

    # 更新用户
    user = User.get(username='john')
    user.email = 'newemail@example.com'
    user.save()

    # 删除用户
    user = User.get(username='john')
    user.delete_instance()

    print("Finish started.")


if __name__ == "__main__":
    get_start()
