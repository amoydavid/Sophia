# -*- coding: utf-8 -*-

import os
import Image

from flask import url_for, render_template, g, send_from_directory, flash, redirect, request
from flask.ext.login import current_user, login_required

from website import app
from config import GLOBAL_SETTING, STATIC_FOLDER, DEBUG, UPLOAD_FOLDER, PIC_EXTENSIONS
from models import Topic, Project, Todolist, Todo
from forms import TopicForm, CommentForm, TodoCommentForm, TodolistForm


@app.before_request
def load_app():
    g.app = GLOBAL_SETTING


@app.route('/')
def run():
    user_id = current_user.id
    projects = []
    if user_id:
        projects = current_user.projects()
        #projects = Project.query.join(TeamUser, Project.team_user).filter(TeamUser.user_id == user_id)
    return render_template('index.html', projects=projects)


@app.route('/project/<int:project_id>/')
def project_index(project_id):
    topics = Topic.query.filter_by(project_id=project_id, is_comment=0).order_by('updated_at desc')[0:3]
    project = Project.query.get(project_id)
    team_users = project.team.users
    undone_lists = Todolist.query.filter_by(project_id=project_id, has_finished=0).order_by('created_at asc').all()
    done_lists = Todolist.query.filter_by(project_id=project_id, has_finished=1).order_by('created_at desc').all()
    return render_template('project/index.html', topics=topics, project=project, todolists=undone_lists,
                           done_lists=done_lists, todolists_json=str(undone_lists), team_users=team_users)


@login_required
@app.route('/project/<int:project_id>/todos/<string:status>/', defaults={'page': 1})
@app.route('/project/<int:project_id>/todos/<string:status>/page/<int:page>/')
def project_todo_status(project_id, status, page):
    project = Project.query.get(project_id)
    items_per_page = 40
    todos = None
    if status.lower() == 'completed':
        todos = Todo.query.filter_by(project_id=project_id, done=1).order_by('finished_at desc')\
            .paginate(page, items_per_page)
    return render_template('project/completed_todos.html', todos=todos, project=project, status=status)


@app.route('/project/<int:project_id>/todos/')
def project_todos(project_id):
    project = Project.query.get(project_id)
    team_users = project.team.users
    todolists = Todolist.query.filter_by(project_id=project_id, has_finished=0).order_by('created_at asc').all()
    title = u'所有任务'
    done_lists = Todolist.query.filter_by(project_id=project_id, has_finished=1).order_by('created_at desc').all()
    return render_template('project/todos.html', project=project, todolists=todolists,
                           todolists_json=str(todolists), team_users=team_users, title=title, done_lists=done_lists)


@login_required
@app.route('/project/<int:project_id>/topics/create/', methods=['GET', 'POST'])
def topic_create(project_id):
    project = Project.query.get(project_id)
    form = TopicForm(current_user, project, request.form.getlist('attachment'))
    if form.validate_on_submit():
        topic = form.saveTopic()
        if topic is not None:
            flash(u'保存成功')
            return redirect(url_for('topic_detail', topic_id=topic.id))
        else:
            flash(u'保存失败，请联系管理员', 'error')
    return render_template('project/topic_create.html', project=project, form=form)


@app.route('/project/<int:project_id>/topics/', defaults={'page': 1})
@app.route('/project/<int:project_id>/topics/page/<int:page>/')
def topic_list(project_id, page):
    project = Project.query.get(project_id)
    pagination = Topic.query.filter_by(project_id=project.id, is_comment=0).order_by("topic.updated_at desc").paginate(
        page, 20)
    return render_template('project/topic_list.html', project=project, pagination=pagination)


@app.route('/topic/<int:topic_id>/', methods=['GET', 'POST'], defaults={'page': 1})
@app.route('/topic/<int:topic_id>/page/<int:page>/', methods=['GET', 'POST'])
def topic_detail(topic_id, page):
    topic = Topic.query.get(topic_id)
    form = CommentForm(current_user, topic, request.form.getlist('attachment'))
    items_per_page = 20
    if form.validate_on_submit():
        comment = form.saveTopic()
        if comment is not None:
            flash(u'保存成功')
            pagination = Topic.query.filter_by(class_type='topic', is_comment=1, class_id=topic.id).order_by(
                "topic.created_at asc").paginate(page, items_per_page)
            return redirect(
                url_for('topic_detail', topic_id=topic_id, page=pagination.pages, _anchor='comment%i' % comment.id))
        else:
            flash(u'保存失败，请联系管理员', 'error')

    pagination = Topic.query.filter_by(class_type='topic', is_comment=1, class_id=topic.id).order_by(
        "topic.created_at asc").paginate(page, items_per_page)
    return render_template('project/topic_detail.html', project=topic.project, topic=topic, form=form,
                           pagination=pagination)


@app.route('/project/<int:project_id>/lists/', defaults={'page': 1})
@app.route('/project/<int:project_id>/lists/page/<int:page>/')
def project_todolists(project_id, page):
    project = Project.query.get(project_id)

    return "todolist"


@app.route('/lists/<int:list_id>/', methods=['GET'])
def todolist_show(list_id):
    todolist = Todolist.query.get(list_id)
    project = todolist.project
    team_users = project.team.users
    todolists = [todolist]
    title = todolist.name
    return render_template('project/todos.html', project=project, todolists=todolists,
                           todolists_json=str(todolists), team_users=team_users, title=title, is_done=True,
                           todolist=todolist)


@login_required
@app.route('/todo/<int:todo_id>/', defaults={'page': 1}, methods=['GET', 'POST'])
@app.route('/todo/<int:todo_id>/page/<int:page>/', methods=['GET', 'POST'])
def todo_show(todo_id, page):
    todo = Todo.query.get(todo_id)
    form = TodoCommentForm(current_user, todo, request.form.getlist('attachment'))
    items_per_page = 10
    if form.validate_on_submit():
        comment = form.saveTopic()
        if comment is not None:
            flash(u'保存成功')
            pagination = Topic.query.filter_by(class_type='todo', is_comment=1, class_id=todo.id).order_by(
                "topic.created_at asc").paginate(page, items_per_page)
            return redirect(
                url_for('todo_show', todo_id=todo_id, page=pagination.pages, _anchor='comment%i' % comment.id))
        else:
            flash(u'保存失败，请联系管理员', 'error')
    team_users = todo.project.team.users
    pagination = Topic.query.filter_by(class_type='todo', is_comment=1, class_id=todo.id).order_by(
        "topic.created_at asc").paginate(page, items_per_page)
    return render_template('project/todo.html', todo=todo, form=form, pagination=pagination, team_users=team_users)


@login_required
@app.route('/project/<int:project_id>/todos/create_list/', methods=['GET', 'POST'])
def todolist_create(project_id):
    project = Project.query.get(project_id)
    form = TodolistForm(current_user, project_id)
    if form.validate_on_submit():
        flash(u'%s 创建成功' % form.todolist.name)
        return redirect(url_for("todolist_show", list_id=form.todolist.id))
    return render_template('project/todolist_create.html', form=form, project=project)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(STATIC_FOLDER, 'favicon.ico')


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    size = request.args.get('size')
    if size:
        (base_name, ext_name) = filename.rsplit('.', 1)
        if ext_name in PIC_EXTENSIONS:
            ori_file = os.path.join(UPLOAD_FOLDER, filename)
            thumb_filename = "{0:s}_{1:s}.jpg".format(base_name, size)
            thumb_dir = os.path.join(UPLOAD_FOLDER, "thumb")
            file_path = os.path.join(UPLOAD_FOLDER, "thumb/{0:s}".format(thumb_filename))
            if not os.path.exists(file_path):
                if not os.path.exists(thumb_dir):
                    os.mkdir(thumb_dir)
                im = Image.open(ori_file)
                (x, y) = im.size
                y_s = int(size)
                x_s = x * y_s / y
                out = im.resize((x_s, y_s), Image.ANTIALIAS)
                out.save(file_path, "JPEG")
            return send_from_directory(thumb_dir, thumb_filename)
        else:
            ori_file = os.path.join(STATIC_FOLDER, 'file_type/{0:s}.png'.format(ext_name))
            thumb_filename = "{0:s}_{1:s}.png".format(ext_name, size)
            thumb_dir = os.path.join(UPLOAD_FOLDER, "thumb")
            file_path = os.path.join(UPLOAD_FOLDER, "thumb/{0:s}".format(thumb_filename))
            if not os.path.exists(file_path):
                if not os.path.exists(thumb_dir):
                    os.mkdir(thumb_dir)
                im = Image.open(ori_file)
                (x, y) = im.size
                y_s = int(size)
                x_s = x * y_s / y
                out = im.resize((x_s, y_s), Image.ANTIALIAS)
                out.save(file_path, "png")
            return send_from_directory(thumb_dir, thumb_filename)

    return send_from_directory(UPLOAD_FOLDER, filename)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=DEBUG)