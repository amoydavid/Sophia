# coding=utf-8
__author__ = 'liuwei'

import json
import time
import os
import uuid
from flask import Blueprint, request, redirect, url_for
from flask.ext.login import (current_user, login_required)
from models import Attachment, TodoNotify


api = Blueprint('api', __name__,
                template_folder='templates')

from models import Todolist, Todo, db


@api.route("/project/<int:project_id>/lists.json")
@login_required
def project_todolists(project_id):
    todolists = Todolist.query.filter_by(project_id=project_id).order_by('id desc').all()
    return str(todolists)


@api.route("/lists/<int:list_id>/todos.json")
@login_required
def todolist_todos(list_id):
    if request.args.get('done') != 'all':
        todos = Todo.query.filter_by(list_id=list_id).filter_by(done=0, is_del=0).order_by('priority desc, id desc').all()
    else:
        todos = Todo.query.filter_by(list_id=list_id, is_del=0).order_by('priority desc, id desc').all()
    return str(todos)


@api.route("/my_todo.json")
@login_required
def my_todos():
    if request.args.get('done') != 'all':
        todos = Todo.query.filter_by(assignee_uid=current_user.id, done=0, is_del=0).order_by('priority desc, id desc').all()
    else:
        todos = Todo.query.filter_by(assignee_uid=current_user.id, is_del=0).order_by('priority desc, id desc').all()
    return str(todos)


@api.route("/lists/<int:list_id>/todos.json", methods=['POST'])
@login_required
def todolist_new_todo(list_id):
    """
    新建todo
    :param list_id:
    :return:
    """
    current_time = int(time.time())
    todolist = Todolist.query.get(list_id)
    subject = request.json.get('subject', '')
    todo = Todo()
    todo.project_id = todolist.project_id
    todo.subject = subject
    todo.point = request.json.get('point', 0)
    todo.list_id = list_id
    todo.due_date = request.json.get('due_date', '0000-00-00')
    todo.creator_id = current_user.id
    todo.created_at = current_time
    todo.updated_at = current_time
    todo.assignee_uid = request.json.get('assignee_uid', 0)
    todo.updated_user_id = current_user.id
    db.session.add(todo)
    db.session.commit()
    todo_obj = json.loads(str(todo))
    todo_obj['code'] = 0
    todo_obj['message'] = u'%s 已添加' % subject
    return json.dumps(todo_obj)


@api.route("/todo/<int:todo_id>", methods=['PUT'])
@login_required
def todo_put(todo_id):
    data = request.json
    done = data['done']
    assignee_uid = 0
    if data['assignee_uid']:
        assignee_uid = int(data['assignee_uid'])
    todo = Todo.query.get(todo_id)
    if todo is not None:
        todo.done = done
        todo.assignee_uid = assignee_uid
        if done:
            todo.finish_uid = current_user.id
        if data['due_date']:
            todo.due_date = data['due_date']
        todo.updated_user_id = current_user.id
        todo.subject = data['subject']
        db.session.commit()
    todo_obj = json.loads(str(todo))
    todo_obj['code'] = 0
    todo_obj['message'] = u'%s 更新成功' % todo.subject
    return json.dumps(todo_obj)


@api.route("/todo/<int:todo_id>", methods=['DELETE'])
@login_required
def todo_delete(todo_id):
    todo = Todo.query.get(todo_id)
    todo.is_del = 1
    db.session.add(todo)
    db.session.commit()
    json_obj = {'code': 0, 'message': '删除成功'}
    return json.dumps(json_obj)

from config import ALLOWED_EXTENSIONS, UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@api.route('/attachment/upload/', methods=['POST'])
@login_required
def upload_file():
    file = request.files['file']
    if file and allowed_file(file.filename):
        ext_name = file.filename.rsplit('.', 1)[1]
        filename = '{0:s}.{1:s}'.format(uuid.uuid1(), ext_name)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        size = os.path.getsize(os.path.join(UPLOAD_FOLDER, filename))
        attachment = Attachment()
        attachment.path = filename
        attachment.filename = file.filename
        attachment.size = size
        attachment.created_at = int(time.time())
        attachment.user_id = current_user.id
        attachment.ext_name = ext_name
        attachment.topic_id = 0
        db.session.add(attachment)
        db.session.commit()
        obj = {
            'id': attachment.id,
            'url': url_for('uploaded_file', filename=filename)
        }
        return json.dumps(obj)
    return ''


@api.route('/attachment/delete/', methods=['POST'])
@login_required
def delete_file():
    attach_id = request.form.get('id')
    attachment = Attachment.query.filter_by(id=attach_id, user_id=current_user.id).first()
    if attachment:
        attach_file = os.path.join(UPLOAD_FOLDER, attachment.path)
        if os.path.isfile(attach_file):
            os.remove(attach_file)
        db.session.delete(attachment)
        db.session.commit()
    return '1'


@api.route('/todo/link/<int:from_id>/<int:to_id>/', methods=['POST'])
@login_required
def link_todo(from_id, to_id):
    notify = TodoNotify.query.filter_by(from_id=from_id, to_id=to_id).first()
    if notify:
        return '已经链接过了亲'
    notify = TodoNotify()
    notify.from_id = from_id
    notify.to_id = to_id
    notify.created_at = int(time.time())
    notify.user_id = 0
    db.session.add(notify)
    db.session.commit()
    return '链接成功'


@api.route('/todo/move/<int:todo_id>/', methods=['POST'])
@login_required
def move_todo(todo_id):
    todolist_id = request.form.get('todolist_id')
    index = request.form.get('index')
    todo = Todo.query.get(todo_id)
    todo.move(todolist_id, index)
    return '操作成功'


