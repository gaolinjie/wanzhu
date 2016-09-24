#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2013 meiritugua.com

import uuid
import uuid
import hashlib
from PIL import Image
import StringIO
import time
import json
import re
import urllib2
import tornado.web
import lib.jsonp
import pprint
import math
import datetime 
import os
import requests

from base import *
from lib.variables import *
from form.user import *
from lib.variables import gen_random
from lib.xss import XssCleaner
from lib.utils import find_mentions
from lib.utils import getJsonKeyValue
from lib.reddit import hot
from lib.utils import pretty_date
from lib.dateencoder import DateEncoder

from lib.mobile import is_mobile_browser

import geetest

gt=geetest.geetest("b3def7f6a704f9649f2d907b1b661e70")

from qiniu import Auth
from qiniu import BucketManager
from qiniu import put_data

access_key = "TFvjvqgoQZi8ec-C0HB3cbYO_fE7_kbUYd6DDko6"
secret_key = "_YH9QO_rTUrm4q82vH9ifQyTaQknj5xrtaQJ5iGI"
q = Auth(access_key, secret_key)
bucket = BucketManager(q)
bucket_domain = '7xko01.com1.z0.glb.clouddn.com'

DEBUG_FLAG = True

def do_api_login(self, user_id):
    user_info = self.user_model.get_user_by_uid(user_id)
    user_id = user_info["uid"]
    self.session["uid"] = user_id
    self.session["username"] = user_info["username"]
    self.session["password"] = user_info["password"]
    self.session.save()
    self.set_secure_cookie("user", str(user_id))

def do_api_logout(self):
    # destroy sessions
    self.session["uid"] = None
    self.session["username"] = None
    self.session["password"] = None
    self.session.save()

    # destroy cookies
    self.clear_cookie("user")

class SigninApiHandler(BaseHandler):
    def post(self, template_variables = {}):
        template_variables = {}

        data = json.loads(self.request.body)
        username = data["username"]
        password = data["password"]

        success = 0
        message = ""
        user_info = None

        if data or username or password:
            success = 0
            user_info = self.user_model.get_user_by_username(username)
        else:
            success = -1
            message = "请求参数错误，请重试"

        if user_info == None:
            success = -1
            message = "该用户不存在"

        user_info = None
        if success == 0:
            secure_password = hashlib.sha1(password).hexdigest()
            secure_password_md5 = hashlib.md5(password).hexdigest()
            user_info = self.user_model.get_user_by_username_and_password(username, secure_password)
            user_info = user_info or self.user_model.get_user_by_username_and_password(username, secure_password_md5)

        if(user_info):
            do_api_login(self, user_info["uid"])
            updated = self.user_model.set_user_base_info_by_uid(user_info["uid"], {"last_login": time.strftime('%Y-%m-%d %H:%M:%S')})
            success = 0
            message = "登录成功"
        else:
            success = -1
            message = "登录失败，请重试"

        self.write(lib.jsonp.print_JSON({
                    "success": success,
                    "message": message
            }))

class SignoutApiHandler(BaseHandler):
    def get(self):
        do_api_logout(self)
        self.write(lib.jsonp.print_JSON({
                    "success": 0,
                    "message": "退出登录成功"
            }))

class SettingPasswordApiHandler(BaseHandler):
    def post(self, template_variables = {}):
        template_variables = {}

        data = json.loads(self.request.body)
        password_old = data["password_old"]
        password_new = data["password_new"]

        if data and password_old and password_new:
            success = 0
        else:
            success = -1
            message = "请求参数错误，请重试"

        if success == 0:
            user_info = self.current_user
            if(user_info):
                user_id = user_info["uid"]
                secure_old_password = hashlib.sha1(password_old).hexdigest()
                secure_new_password = hashlib.sha1(password_new).hexdigest()

                if(not user_info["password"] == secure_old_password):
                    success = -1
                    message = "当前密码输入不正确，请重试"
                else:
                    self.user_model.set_user_password_by_uid(user_id, secure_new_password)
                    success = 0
                    message = "您的用户密码已更新"
                    self.user_model.set_user_base_info_by_uid(user_id, {"updated": time.strftime('%Y-%m-%d %H:%M:%S')})
            else:
                success = -1
                message = "登录失败，请重试"

        self.write(lib.jsonp.print_JSON({
                    "success": success,
                    "message": message
            }))

class GetUserBaseInfoApiHandler(BaseHandler):
    def get(self, template_variables = {}):
        user_info = self.current_user

        if(user_info):  
            success = 0
            message = "成功获取用户基本信息"

            self.write(lib.jsonp.print_JSON({
                    "success": success,
                    "message": message,
                    "uid": user_info.uid,
                    "mobile": user_info.mobile,
                    "username": user_info.username,
            }))
        else:
            success = -1
            message = "用户未登录，请先登录"

            self.write(lib.jsonp.print_JSON({
                    "success": success,
                    "message": message
            }))

class UpdateUserBaseInfoApiHandler(BaseHandler):
    def post(self, template_variables = {}):
        user_info = self.current_user
        user_id = int(self.get_argument("uid", "-1"))

        if(user_info):  
            if(user_id==-1):
                user_id = user_info.uid
            else:
                if(user_id!=user_info.uid and user_info.admin!="admin" and user_info.admin!="teacher"):
                    self.write(lib.jsonp.print_JSON({
                        "success": -1,
                        "message": "不是管理员，无法更新别人的信息"
                    }))
                    return

            update_info = {}
            data = json.loads(self.request.body)

            update_info = getJsonKeyValue(data, update_info, "username")
            update_info = getJsonKeyValue(data, update_info, "mobile")
            update_info = getJsonKeyValue(data, update_info, "gender")
            update_info = getJsonKeyValue(data, update_info, "admin")
            update_info["updated"] = time.strftime('%Y-%m-%d %H:%M:%S')

            update_result = self.user_model.set_user_base_info_by_uid(user_id, update_info)


            if update_result == 0:
                success = 0
                message = "成功保存用户基本信息"
            else:
                success = -1
                message = "保存用户基本信息失败"

            self.write(lib.jsonp.print_JSON({
                    "success": success,
                    "message": message
            }))
        else:
            success = -1
            message = "用户未登录，请先登录"

            self.write(lib.jsonp.print_JSON({
                    "success": success,
                    "message": message
            }))     

class GetCourseApiHandler(BaseHandler):
    def get(self, course_id, template_variables = {}):
        course = self.course_model.get_course_by_id(course_id)
        course_json = json.dumps(course, cls=DateEncoder)
        self.write(course_json)

class GetAllCoursesApiHandler(BaseHandler):
    def get(self, template_variables = {}):
        all_courses = self.course_model.get_all_courses()
        course_json = json.dumps(all_courses, cls=DateEncoder)
        self.write(course_json)

class TraceApiHandler(BaseHandler):
    def post(self, template_variables = {}):
        user_info = self.current_user

        if(user_info):  
            update_info = {}
            data = json.loads(self.request.body)

            chapter_id = data["chapter_id"]
            video_url = self.chapter_model.get_chapter_by_id(chapter_id).video_link
            update_info["video_url"] = video_url
            update_info["created"] = time.strftime('%Y-%m-%d %H:%M:%S')
            update_info["userid"] = user_info.uid
            update_info["username"] = user_info.username 
            update_info = getJsonKeyValue(data, update_info, "event_str")   
            self.trace_model.add_new_trace(update_info)
