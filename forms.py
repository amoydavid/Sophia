# coding=utf-8
__author__ = 'liuwei'

from flask.ext.wtf import Form, TextField, Required, PasswordField, HiddenField, TextAreaField, SelectField, SelectMultipleField, widgets
from models import User, Topic, db, Todolist, Attachment
import time


class LoginForm(Form):
    email = TextField(u'邮箱', validators=[Required(u'请填写邮箱')])
    password = PasswordField(u'密码', validators=[Required(u'请填写密码')])
    next = HiddenField()

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.user = None

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False
        user = User.query.filter_by(email=self.email.data).first()
        if user is None:
            self.email.errors.append(u'用户不存在')
            return False
        if not user.check_password(self.password.data):
            self.password.errors.append(u"密码不正确")
            return False
        self.user = user
        return True


class RegisterForm(Form):
    email = TextField(u'邮箱', validators=[Required(u'请填写邮箱')])
    name = TextField(u'名字', validators=[Required(u'请填写名字')])
    password = PasswordField(u'密码', validators=[Required(u'请填写密码')])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.user = None

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False
        user = User.query.filter_by(email=self.email.data).first()
        if user is not None:
            self.email.errors.append(u'Email已被注册')
            return False
        user = User(self.name.data)
        created_time = int(time.time())
        user.email = self.email.data
        user.password = user.hash_password(self.password.data)
        user.created_at = created_time
        user.site = 0
        user.updated_at = created_time
        user.avatar = 'img/default_avatar.jpg'
        db.session.add(user)
        db.session.commit()
        self.user = user
        return True


class TopicForm(Form):
    class_type = HiddenField(default='topic')
    class_id = HiddenField(default='0')
    subject = TextField(u'主题', validators=[Required(u'请填写主题')])
    content = TextAreaField(u'内容')

    def __init__(self, user, project, attachments=None, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.user = user
        self.project = project
        if not attachments:
            attachments = []
        self.attachments = attachments

    def saveTopic(self):
        topic = Topic()
        topic.class_type = self.class_type.data
        topic.class_id = int(self.class_id.data)
        topic.subject = self.subject.data
        topic.content = self.content.data
        topic.project_id = self.project.id
        topic.user_id = self.user.id
        current_time = int(time.time())
        topic.created_at = current_time
        topic.updated_at = current_time
        db.session.add(topic)
        db.session.commit()
        project = topic.project
        for atta_id in self.attachments:
            atta = Attachment.query.get(atta_id)
            atta.topic_id = topic.id
            atta.project_id = topic.project_id
            atta.root_class = topic.class_type
            if topic.class_id == 0:
                atta.root_id = topic.id
            else:
                atta.root_id = topic.class_id
            db.session.commit()
            project.file_count += 1
        db.session.commit()
        return topic


class CommentForm(Form):
    content = TextAreaField(u'内容')

    def __init__(self, user, topic, attachments=None, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.user = user
        self.topic = topic
        if not attachments:
            attachments = []
        self.attachments = attachments

    def saveTopic(self):
        topic = Topic()
        topic.class_type = 'topic'
        topic.class_id = self.topic.id
        topic.content = self.content.data
        topic.project_id = self.topic.project.id
        topic.user_id = self.user.id
        current_time = int(time.time())
        topic.created_at = current_time
        topic.updated_at = current_time
        topic.is_comment = 1
        db.session.add(topic)
        db.session.commit()
        project = topic.project
        for atta_id in self.attachments:
            atta = Attachment.query.get(atta_id)
            atta.topic_id = topic.id
            atta.project_id = topic.project_id
            atta.root_class = topic.class_type
            atta.root_id = topic.class_id
            db.session.commit()
            project.file_count += 1
        db.session.commit()
        return topic


class TodoCommentForm(Form):
    content = TextAreaField(u'内容')

    def __init__(self, user, todo, attachments=None, *args, **kwargs):
        """
        class init
        :param user:
        :param todo:
        :param attachment:
        :param args:
        :param kwargs:
        """
        if not attachments:
            attachments = []
        Form.__init__(self, *args, **kwargs)
        self.user = user
        self.todo = todo
        self.attachments = attachments

    def saveTopic(self):
        topic = Topic()
        topic.class_type = 'todo'
        topic.class_id = self.todo.id
        topic.content = self.content.data
        topic.project_id = self.todo.project.id
        topic.user_id = self.user.id
        current_time = int(time.time())
        topic.created_at = current_time
        topic.updated_at = current_time
        topic.is_comment = 1
        db.session.add(topic)
        db.session.commit()
        project = topic.project
        for atta_id in self.attachments:
            atta = Attachment.query.get(atta_id)
            atta.topic_id = topic.id
            atta.project_id = topic.project_id
            atta.root_class = topic.class_type
            atta.root_id = topic.class_id
            db.session.commit()
            project.file_count += 1
        db.session.commit()
        return topic


class TodolistForm(Form):
    name = TextField(u'列表名称', validators=[Required(u'请填写列表名称')])

    def __init__(self, user, project_id, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.project_id = int(project_id)
        self.todolist = None
        self.user = user

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False
        current_time = int(time.time())
        todolist = Todolist()
        todolist.name = self.name.data
        todolist.project_id = self.project_id
        todolist.created_at = current_time
        todolist.updated_at = current_time
        todolist.creator_id = self.user.id
        todolist.todo_count = 0
        todolist.has_finished = 0
        todolist.finish_count = 0
        db.session.add(todolist)
        db.session.commit()
        self.todolist = todolist
        return True