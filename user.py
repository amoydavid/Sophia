# coding=utf-8
__author__ = 'liuwei'

from flask import Blueprint, render_template, abort,request,flash,redirect,url_for
from jinja2 import TemplateNotFound
from flask.ext.login import (LoginManager, current_user, login_required,
                             login_user, logout_user, AnonymousUser,
                             confirm_login, fresh_login_required)
from forms import LoginForm

user = Blueprint('user', __name__,
    template_folder='templates')

@user.route('/login/',methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash(u'欢迎回来，%s' % form.user.name)
        remember = request.form.get("remember", "no") == "yes"
        login_user(form.user, remember=remember)
        return redirect(form.next.data or url_for("run"))
    return render_template("login.html", form=form)

@user.route("/logout/")
@login_required
def logout():
    logout_user()
    flash(u"已注销")
    return redirect(url_for("run"))

@user.route('/')
def show_index():
    password = 'miiyue.com'
    pw_hash = password
    return "user show"+pw_hash

@user.route('/<int:user_id>/')
def show(user_id):
    return 'user index'