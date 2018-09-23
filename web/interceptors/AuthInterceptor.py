import re

from app import app
from flask import request, redirect, g

from common.libs.UrlManager import UrlManager
from common.libs.user.Userservice import UserService
from common.models.user import User


@app.before_request
def before_request():
    """拦截器，登陆限制"""
    ignore_urls = app.config['IGNORE_URLS']
    ignore_check_login_urls = app.config['IGNORE_CHECK_LOGIN_URLS']
    path = request.path

    pattern = re.compile('%s' % "|".join(ignore_check_login_urls))
    if pattern.match(path):
        return

    user_info = check_login()
    g.current_user = None
    if user_info:
        g.current_user = user_info

    pattern = re.compile('%s' % "|".join(ignore_urls))
    if pattern.match(path):
        return

    if not user_info:
        return redirect(UrlManager.build_url('/user/login'))
    return


def check_login():
    """
    判断用户是否已经登陆
    :return:
    """
    cookies = request.cookies
    auth_cookie = cookies[app.config['AUTH_COOKIE_NAME']] if app.config['AUTH_COOKIE_NAME'] in cookies else None
    if auth_cookie is None:
        return False

    auth_info = auth_cookie.split("#")
    if len(auth_info) != 2:
        return False
    try:
        user_info = User.query.filter_by(uid=auth_info[1]).first()
    except Exception:
        return False
    if user_info is None:
        return False

    if auth_info[0] != UserService.gene_auth_code(user_info):
        return False

    return user_info