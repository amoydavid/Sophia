# coding=utf-8
__author__ = 'liuwei'

import os
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask.ext.login import (login_required,
                             login_user, logout_user)
from forms import LoginForm, RegisterForm, ProfileForm
from models import User
from config import AVATAR_FOLDER
import Image

user = Blueprint('user', __name__,
                 template_folder='templates')


@user.route('/login/', methods=["GET", "POST"])
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
    return "user show" + pw_hash


@login_required
@user.route('/<int:user_id>/')
def show(user_id):
    return render_template('user/show.html')


@login_required
@user.route('/<int:user_id>/setting/', methods=['GET', 'POST'])
def setting(user_id):
    user = User.query.get(user_id)
    form = ProfileForm(user, email=user.email, name=user.name)
    if form.validate_on_submit():
        size = 128, 128
        if form.avatar.data:
            image_data = request.files[form.avatar.name].read()
            if not os.path.exists(AVATAR_FOLDER):
                os.mkdir(AVATAR_FOLDER)
            open(os.path.join(AVATAR_FOLDER, form.avatar.data.filename), 'w').write(image_data)
            im = Image.open(os.path.join(AVATAR_FOLDER, form.avatar.data.filename))
            if im.size[0] >= im.size[1]:
                im = im.resize((size[0] * im.size[0]/im.size[1], size[0]))
                im = im.crop(((im.size[0] - size[0])/2, 0, (im.size[0] + size[0])/2, size[0]))
            else:
                im = im.resize((size[0], size[0] * im.size[1]/im.size[0]))
                im = im.crop((0, (im.size[1] - size[0])/2, size[0], (im.size[1] + size[0])/2))
            im.save(os.path.join(AVATAR_FOLDER, form.avatar.data.filename))
        flash(u'保存成功')
        return redirect(url_for("user.setting", user_id=user_id))
    return render_template('user/setting.html', form=form)


@user.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        flash(u'欢迎，%s' % form.user.name)
        remember = request.form.get("remember", "no") == "yes"
        login_user(form.user, remember=remember)
        return redirect(url_for("run"))
    return render_template('user/register.html', form = form)