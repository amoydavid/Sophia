# coding=utf-8
__author__ = 'liuwei'

from flask.ext.wtf import Form, TextField, Required, PasswordField, HiddenField, TextAreaField, \
    FileField, SelectField, BooleanField
from models import User, Topic, db, Todolist, Attachment, Team, Project, TeamUser, InviteCode
import time
import os
import uuid
from config import PIC_EXTENSIONS, AVATAR_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in PIC_EXTENSIONS


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


class ProjectForm(Form):
    name = TextField(u'名称', validators=[Required(u'请填写项目名')])
    subject = TextAreaField(u'说明')
    team_id = SelectField(u'团队', coerce=int)

    def __init__(self, user=None, team=None, project=None, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.user = user
        self._team = team
        self.project = project

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False
        if not self.project:
            self.project = Project()
        if not self.user:
            self.name.errors.append(u'没有指定用户')
            return False
        if not self.team_id.data and self._team:
            team_id = self._team.id
        else:
            team_id = self.team_id.data
        self.project.name = self.name.data
        self.project.subject = self.subject.data
        self.project.creator_id = self.user.id
        self.project.created_at = int(time.time())
        self.project.team_id = team_id
        self.project.todo_count = 0
        self.project.file_count = 0
        self.project.topic_count = 0
        self.project.status = 0
        db.session.add(self.project)
        db.session.commit()
        return True


class RegisterForm(Form):
    email = TextField(u'邮箱', validators=[Required(u'请填写邮箱')])
    name = TextField(u'昵称', validators=[Required(u'请填写昵称')])
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
        user = User.query.filter_by(name=self.name.data).first()
        if user is not None:
            self.name.errors.append(u'昵称已被使用')
            return False
        user = User(self.name.data)
        created_time = int(time.time())
        user.email = self.email.data
        user.password = user.hash_password(self.password.data)
        user.created_at = created_time
        user.site = 0
        user.updated_at = created_time
        user.avatar = 'default_avatar.jpg'
        db.session.add(user)
        db.session.commit()
        self.user = user
        return True


class ProfileForm(Form):
    email = TextField(u'邮箱', validators=[Required(u'请填写邮箱')])
    name = TextField(u'昵称', validators=[Required(u'请填写昵称')])
    current_password = PasswordField(u'现有密码')
    new_password = PasswordField(u'新密码')
    avatar = FileField(u'头像')

    def __init__(self, user, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.user = user

    def validate_email(form, field):
        if field.data:
            email_user = User.query.filter(User.email == field.data).filter(db.not_(User.id == form.user.id)).first()
            if email_user:
                field.errors.append(u'Email被占用')
            return False
        return True

    def validate_avatar(form, field):
        if field.data:
            ext_name = field.data.filename.rsplit('.', 1)[1]
            if not allowed_file(field.data.filename):
                field.errors.append(u'只能上传图片')
                return False
            field.data.filename = u"%s.%s" % (uuid.uuid1(), ext_name)
        return True

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False
        if self.new_password.data:
            if not self.current_password.data:
                self.current_password.errors.append(u'请填写现有密码')
                return False
            if not self.user.check_password(self.current_password.data):
                self.current_password.errors.append(u'密码填错了亲')
                return False
            self.user.password = self.user.hash_password(self.new_password.data)
        self.user.email = self.email.data
        self.user.name = self.name.data
        self.user.updated_at = int(time.time())
        old_file = None
        if self.avatar.data:
            old_file = self.user.avatar
            self.user.avatar = u"%s" % self.avatar.data.filename
        db.session.add(self.user)
        db.session.commit()
        if old_file and old_file != 'default_avatar.jpg':
            old_file = os.path.join(AVATAR_FOLDER, old_file)
            if os.path.exists(old_file):
                os.remove(old_file)
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


class TeamForm(Form):
    name = TextField(u'团队名称', validators=[Required(u'请填写团队名称')])
    status = BooleanField(u'删除项目')
    team_id = HiddenField()

    def __init__(self, user, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.admin_user = user

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False
        current_time = int(time.time())
        if self.team_id.data:
            team = Team.query.get(self.team_id.data)
        else:
            team = Team()
        team.admin_id = self.admin_user.id
        team.name = self.name.data
        team.created_at = current_time
        if self.status.data:
            team.status = 1
        else:
            team.status = 0
        db.session.add(team)
        db.session.commit()
        if not self.team_id.data:
            team_user = TeamUser()
            team_user.team_id = team.id
            team_user.user_id = self.admin_user.id
            db.session.add(team_user)
            db.session.commit()
        if self.status.data:
            team_user = TeamUser.query.filter(db.and_(TeamUser.team_id == team.id and
                                                      TeamUser.user_id == self.admin_user.id)).first()
            if team_user:
                db.session.delete(team_user)
                db.session.commit()
            db.session.query(Project).filter(Project.team_id == team.id).update({Project.status: 1})
            db.session.commit()
        self.team = team
        return True


class JoinTeam(Form):
    code = TextField(u'团队邀请码', validators=[Required(u'请填写邀请码')])

    def __init__(self, user, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.user = user

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False
        invite_code = InviteCode.query.filter_by(code=self.code.data, used=0).first()
        if not invite_code:
            self.code.errors.append(u'邀请码不正确')
            return False
        invite_code.email = self.user.email
        invite_code.user_id = self.user.id
        invite_code.used = 1
        db.session.add(invite_code)
        db.session.commit()
        team_user = TeamUser()
        team_user.team_id = invite_code.team_id
        team_user.user_id = self.user.id
        db.session.add(team_user)
        db.session.commit()
        self.team_id = invite_code.team_id
        return True