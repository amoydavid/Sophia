# coding=utf-8
__author__ = 'liuwei'

import json
import time
import os
import uuid
from flask import Blueprint, request, redirect, url_for
from flask.ext.login import (current_user, login_required)
from models import Attachment


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
        todos = Todo.query.filter_by(list_id=list_id).filter_by(done=0).order_by('id desc').all()
    else:
        todos = Todo.query.filter_by(list_id=list_id).order_by('id desc').all()
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
        db.session.commit()
    todo_obj = json.loads(str(todo))
    todo_obj['code'] = 0
    todo_obj['message'] = u'%s 更新成功' % todo.subject
    return json.dumps(todo_obj)


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