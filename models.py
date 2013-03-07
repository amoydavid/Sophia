# -*- coding: utf-8 -*-

__author__ = 'liuwei'

from website import db
import json, hashlib, time
from util import friendly_datetime


class Attachment(db.Model):
    __tablename__ = 'attachment'
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.Integer)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'))
    path = db.Column(db.String(128))
    ext_name = db.Column(db.String(20))
    root_class = db.Column(db.String(32))
    root_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship("User", uselist=False)
    project = db.relationship("Project", uselist=False)


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    name = db.Column(db.String(64))
    subject = db.Column(db.String(512))
    user = db.relationship("User", uselist=False)
    topic_count = db.Column(db.Integer)
    todo_count = db.Column(db.Integer)
    file_count = db.Column(db.Integer)
    status = db.Column(db.Integer)
    team = db.relationship("Team")
    created_at = db.Column(db.Integer)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256), unique=True)
    password = db.Column(db.String(64))
    name = db.Column(db.String(256))
    site = db.Column(db.Integer)
    created_at = db.Column(db.Integer)
    updated_at = db.Column(db.Integer)
    avatar = db.Column(db.String(256))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<User %r>' % self.name

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def hash_password(self, password):
        return hashlib.md5(password).hexdigest()

    def check_password(self, password):
        if self.password == self.hash_password(password):
            return True
        else:
            return False

    def projects(self):
        team_ids = []
        for team in self.teams:
            team_ids.append(team.id)
        return Project.query.filter(Project.team_id.in_(team_ids)).filter(Project.status == 0).all()

    def __repr__(self):
        obj = {
            'id': self.id,
            'name': self.name,
            'avatar': self.avatar
        }
        return json.dumps(obj)


TeamUser = db.Table('team_user',
                    db.Column('team_id', db.Integer, db.ForeignKey('team.id')),
                    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)


class Team(db.Model):
    __tablename__ = 'team'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    users = db.relationship('User', secondary=TeamUser, backref=db.backref('teams', lazy='dynamic'))


class Topic(db.Model):
    __tablename__ = 'topic'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    class_type = db.Column(db.String(32))
    class_id = db.Column(db.Integer)
    user = db.relationship("User", uselist=False)
    project = db.relationship("Project", uselist=False)
    subject = db.Column(db.String(512))
    content = db.Column(db.Text)
    created_at = db.Column(db.Integer)
    updated_at = db.Column(db.Integer)
    reply_count = db.Column(db.Integer, default=0)
    is_comment = db.Column(db.SmallInteger, default=0)
    attachments = db.relationship("Attachment", backref="topic")

    def _get_attachments(self):
        return db.object_session(self).query(Attachment).filter(Attachment.root_id == self.id,
                                                                Attachment.root_class == 'topic').all()

    all_attachments = property(_get_attachments)


class Todolist(db.Model):
    __tablename__ = 'todo_list'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), db.ForeignKey('user.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    created_at = db.Column(db.Integer)
    updated_at = db.Column(db.Integer)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    todo_count = db.Column(db.Integer)
    finish_count = db.Column(db.Integer)
    has_finished = db.Column(db.SmallInteger)
    project = db.relationship('Project')

    def __repr__(self):
        obj = {
            'id': self.id,
            'name': self.name,
            'project_id': self.project_id,
            'todo_count': self.todo_count,
            'finish_count': self.finish_count,
            'has_finished': self.has_finished
        }
        return json.dumps(obj)

    def todos(self, done=0, limit=None):
        if not limit:
            todos = Todo.query.filter_by(list_id=self.id, done=done).order_by('priority desc')[0:limit]
        else:
            todos = Todo.query.filter_by(list_id=self.id, done=done).order_by('priority desc')
        return todos


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    created_at = db.Column(db.Integer)
    updated_at = db.Column(db.Integer)
    finished_at = db.Column(db.Integer, nullable=True)
    creator_id = db.Column(db.Integer)
    list_id = db.Column(db.Integer)
    priority = db.Column(db.Integer, default=0)
    point = db.Column(db.Integer, default=0)
    subject = db.Column(db.String(256), nullable=False)
    done = db.Column(db.SmallInteger, default=0)
    due_date = db.Column(db.Date, default=0)
    finish_uid = db.Column(db.Integer, default=0)
    assignee_uid = db.Column(db.Integer, default=0)
    reply_count = db.Column(db.Integer, default=0)
    creator = db.relationship('User', uselist=False, foreign_keys=creator_id, primaryjoin=creator_id == User.id)
    finish_user = db.relationship('User', uselist=False, foreign_keys=finish_uid, primaryjoin=finish_uid == User.id)
    assignee = db.relationship('User', uselist=False, foreign_keys=assignee_uid, primaryjoin=assignee_uid == User.id)
    _old_done = 0
    project = db.relationship('Project')
    todolist = db.relationship('Todolist', uselist=False, foreign_keys=list_id, primaryjoin=list_id == Todolist.id)

    def _get_attachments(self):
        return db.object_session(self).query(Attachment).filter(Attachment.root_id == self.id,
                                                                                  Attachment.root_class == 'todo').all()

    attachments = property(_get_attachments)

    def __repr__(self):
        due_date = ''
        if self.due_date:
            due_date = str(self.due_date)
        assignee = None
        if self.assignee:
            assignee = {
                'id': self.assignee.id,
                'name': self.assignee.name,
                'avatar': self.assignee.avatar
            }
        finish_user = None
        if self.finish_user:
            finish_user = {
                'id': self.finish_user.id,
                'name': self.finish_user.name,
                'avatar': self.finish_user.avatar
            }
        obj = {
            'id': self.id,
            'subject': self.subject,
            'project_id': self.project_id,
            'done': self.done,
            'due_date': due_date,
            'finished_at': friendly_datetime(self.finished_at),
            'assignee_uid': self.assignee_uid,
            'reply_count': self.reply_count,
            'point': self.point,
            'creator': {
                'id': self.creator.id,
                'name': self.creator.name,
                'avatar': self.creator.avatar
            },
            'finish_user': finish_user,
            'assignee': assignee
        }
        return json.dumps(obj)


from sqlalchemy import event


def after_insert_topic(mapper, connection, target):
    if target.is_comment != 1:
        connection.execute('update project set topic_count = topic_count+1 where id = %i' % int(target.project_id))
    else:
        connection.execute('update %s set reply_count = reply_count+1,updated_at = %i where id = %i' % (
            target.class_type, int(time.time()), int(target.class_id)))


def after_insert_todo(mapper, connection, target):
    connection.execute(
        'update todo_list set todo_count = todo_count+1,has_finished=0 where id = %i' % int(target.list_id))
    connection.execute('update project set todo_count = todo_count+1 where id = %i' % int(target.project_id))


def before_update_todo(mapper, connection, target):
    target._old_done = connection.scalar(
        "select done from todo where id = %d"
        % target.id)
    if target._old_done == 0 and target.done == 1:
        target.finished_at = int(time.time())
        #connection.execute('update todo set finished_at = %d where id = %i' % (int(time.time()), int(target.id)))


def after_update_todo(mapper, connection, target):
    if target._old_done == 0 and target.done == 1:
        list_id = int(target.list_id)
        connection.execute('update todo_list set finish_count = finish_count+1 where id = %i' % list_id)
        result = connection.execute(
            "select todo_count,finish_count from todo_list where id = %i" % list_id
        )
        for row in result:
            if row['todo_count'] == row['finish_count']:
                connection.execute('update todo_list set has_finished = 1 where id = %i' % list_id)
            break
        result.close()
    elif target._old_done == 1 and target.done == 0:
        connection.execute(
            'update todo_list set finish_count = finish_count-1,has_finished=0 where id = %i' % int(target.list_id))


event.listen(Topic, 'after_insert', after_insert_topic)
event.listen(Todo, 'after_insert', after_insert_todo)
event.listen(Todo, 'before_update', before_update_todo)
event.listen(Todo, 'after_update', after_update_todo)
