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
import sys
import stat
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
from pwd import getpwnam
from grp import getgrnam

import geetest

gt=geetest.geetest("b3def7f6a704f9649f2d907b1b661e70")

from qiniu import Auth
from qiniu import BucketManager
from qiniu import put_data

access_key = "DaQzr1UhFQD6im_kJJjZ8tQUKQW7ykiHo4ZWfC25"
secret_key = "Ge61JJtUSC5myXVrntdVOqAZ5L7WpXR_Taa9C8vb"
q = Auth(access_key, secret_key)
bucket = BucketManager(q)

DEBUG_FLAG = True

def my_chown(path, uname, gname):
    uid = getpwnam(uname).pw_uid
    gid = getgrnam(gname).gr_gid
    os.chown(path, uid, gid)

def do_login(self, user_id):
    user_info = self.user_model.get_user_by_uid(user_id)
    user_id = user_info["uid"]
    self.session["uid"] = user_id
    self.session["username"] = user_info["username"]
    self.session["mobile"] = user_info["mobile"]
    self.session["password"] = user_info["password"]
    self.session.save()
    self.set_secure_cookie("user", str(user_id))

def do_logout(self):
    # destroy sessions
    self.session["uid"] = None
    self.session["username"] = None
    self.session["mobile"] = None
    self.session["password"] = None
    self.session.save()

    # destroy cookies
    self.clear_cookie("user")

class SigninAdminHandler(BaseHandler):
    def get(self, template_variables = {}):
        do_logout(self)
        self.render("admin/login.html", **template_variables)

    def post(self, template_variables = {}):
        template_variables = {}

        # validate the fields

        form = SigninForm(self)

        user_info = self.user_model.get_user_by_mobile(form.mobile.data)
        if user_info == None:
            #self.redirect("/?s=signin&e=1")
            template_variables["errors"] = "用户名或密码错误！"
            self.render("admin/login.html", **template_variables)
            return
        
        secure_password = hashlib.sha1(form.password.data).hexdigest()
        secure_password_md5 = hashlib.md5(form.password.data).hexdigest()
        user_info = self.user_model.get_user_by_mobile_and_password(form.mobile.data, secure_password)
        user_info = user_info or self.user_model.get_user_by_mobile_and_password(form.mobile.data, secure_password_md5)
        
        if(user_info):
            do_login(self, user_info["uid"])
            # update `last_login`
            updated = self.user_model.set_user_base_info_by_uid(user_info["uid"], {"last_login": time.strftime('%Y-%m-%d %H:%M:%S')})
            self.redirect("/admin")
            return
        else:
            #self.redirect("/?s=signin&e=2")
            template_variables["errors"] = "手机或密码错误！"
            self.render("admin/login.html", **template_variables)
            return

class SignoutAdminHandler(BaseHandler):
    def get(self):
        do_logout(self)
        # redirect
        self.redirect(self.get_argument("next", "/admin/signin"))

class SignupAdminHandler(BaseHandler):
    def get(self, template_variables = {}):
        do_logout(self)
        self.redirect("/?s=signup&e=1")

    def post(self, template_variables = {}):
        template_variables = {}

        # validate the fields

        form = SignupForm(self)

        if not form.validate():
            self.get({"errors": form.errors})
            return

        # validate duplicated
        duplicated_username = self.user_model.get_user_by_username(form.username.data)

        if(duplicated_username):
                self.redirect("/?s=signup&e=4")
                return

        # validate reserved

        if(form.username.data in self.settings.get("reserved")):
            template_variables["errors"] = {}
            template_variables["errors"]["reserved_username"] = [u"用户名被保留不可用"]
            self.get(template_variables)
            return

        # continue while validate succeed

        secure_password = hashlib.sha1(form.password.data).hexdigest()
        avatar = self.avatar_model.get_rand_avatar()

        user_info = {
            "username": form.username.data,
            "password": secure_password,
            "avatar": avatar[0].avatar,
            "created": time.strftime('%Y-%m-%d %H:%M:%S')
        }

        if(self.current_user):
            return
        
        user_id = self.user_model.add_new_user(user_info)
        
        if(user_id):
            follow_info = {
                "author_id": user_id,
                "obj_id": user_id,
                "obj_type": "u",
                "created": time.strftime('%Y-%m-%d %H:%M:%S')
            }
            self.follow_model.add_new_follow(follow_info)

            do_login(self, user_id)

        self.redirect(self.get_argument("next", "/"))

class IndexAdminHandler(BaseHandler):
    def get(self, template_variables = {}):
        user_info = self.current_user
        template_variables["side_menu"] = "dashboard"
        template_variables["user_info"] = user_info
        template_variables["user_count"] = 0
        template_variables["course_count"] = 0
        if(user_info and (user_info.admin == "admin")):  
            self.render("admin/index.html", **template_variables)
        else:
            self.redirect("/admin/signin")

class PersonalAdminHandler(BaseHandler):
    def get(self, template_variables = {}):
        template_variables["side_menu"] = "personal"
        user_info = self.current_user
        template_variables["user_info"] = user_info
        
        if(user_info and (user_info.admin == "admin" or user_info.admin == "teacher")):
            self.render("admin/personal.html", **template_variables)
        else:
            self.redirect("/admin/signin")
    
    def post(self, template_variables = {}):
        template_variables = {}

        # validate the password

        user_info = self.current_user
        user_id = user_info["uid"]
        print('user info: %s' %(user_info.admin))

        if(user_info and (user_info.admin == "admin" or user_info.admin == "teacher")):
            update_info = {}
            data = json.loads(self.request.body)

            update_info = getJsonKeyValue(data, update_info, "old_pw")
            update_info = getJsonKeyValue(data, update_info, "new_pw")
            password_old = update_info["old_pw"]
            password = update_info["new_pw"]

            #print('old pw %s\n' %(password_old))
            #print('new pw %s\n' %(password))
            
            secure_password = hashlib.sha1(password_old).hexdigest()
            secure_new_password = hashlib.sha1(password).hexdigest()
            secure_ftp_new_password = hashlib.md5(password).hexdigest()

            if(not user_info["password"] == secure_password):
                success = -1
                message = "当前输入密码有误"
                self.write(lib.jsonp.print_JSON({
                    "success": success,
                    "message": message
                }))
            else:
                # continue while validate succeed
                update_result = self.user_model.set_user_password_by_uid(user_id, secure_new_password)
                if (user_info.admin == "teacher"):
                    ftpuser_name = user_info["username"]
                    #print('ftp user name: %s' % ftpuser_name)
                    self.ftpuser_model.set_ftpuser_password_by_name(ftpuser_name, secure_ftp_new_password)
                
                # update `updated`
                updated = self.user_model.set_user_base_info_by_uid(user_id, {"updated": time.strftime('%Y-%m-%d %H:%M:%S')})
                
                success = 0
                message = "密码修改成功"

                self.write(lib.jsonp.print_JSON({
                    "success": success,
                    "message": message
                }))
                #self.redirect("/admin")

class UsersAdminHandler(BaseHandler):
    def get(self, template_variables = {}):
        template_variables["side_menu"] = "users"
        user_info = self.current_user
        template_variables["user_info"] = user_info
        p = int(self.get_argument("p", "1"))

        if(user_info): 
            if(user_info.admin == "admin"): 
                template_variables["all_users"] = self.user_model.get_all_users(current_page = p)
            if(user_info.admin == "teacher"):
                template_variables["all_users"] = self.course_model.get_course_users_by_teacher(user_info.username, current_page = p)
            self.render("admin/users.html", **template_variables)
        else:
            self.redirect("/admin/signin")

class UserNewAdminHandler(BaseHandler):
    def get(self, template_variables = {}):
        template_variables["side_menu"] = "users"
        user_info = self.current_user
        template_variables["user_info"] = user_info

        if(user_info and (user_info.admin == "admin" or user_info.admin == "teacher")):  
            self.render("admin/user_new.html", **template_variables)
        else:
            self.redirect("/admin/signin")

    def post(self, template_variables = {}):
        user_info = self.current_user

        if(user_info and (user_info.admin == "admin" or user_info.admin == "teacher")):  
            update_info = {}
            data = json.loads(self.request.body)
            
            update_info = getJsonKeyValue(data, update_info, "username")
            update_info = getJsonKeyValue(data, update_info, "mobile")
            update_info = getJsonKeyValue(data, update_info, "gender")
            update_info = getJsonKeyValue(data, update_info, "admin")
            secure_password = hashlib.sha1("123456").hexdigest()
            update_info["password"] = secure_password
            update_info["created"] = time.strftime('%Y-%m-%d %H:%M:%S')

            update_result = self.user_model.add_new_user(update_info)

            if update_result > 0:
                success = 0
                message = "成功新建用户"
            else:
                success = -1
                message = "新建用户失败"

            self.write(lib.jsonp.print_JSON({
                    "success": success,
                    "message": message
            }))
        else:
            success = -1
            message = "新建用户失败"

            self.write(lib.jsonp.print_JSON({
                    "success": success,
                    "message": message
            }))     

class UserEditAdminHandler(BaseHandler):
    def get(self, user_id, template_variables = {}):
        user_info = self.current_user
        template_variables["user_info"] = user_info

        if(user_info and (user_info.admin == "admin")):  
            view_user = self.user_model.get_user_by_uid(user_id)
            template_variables["view_user"] = view_user

            self.render("admin/user_edit.html", **template_variables)
        else:
            self.redirect("/admin/signin")

class UserDeleteAdminHandler(BaseHandler):
    def get(self, user_id, template_variables = {}):
        user_info = self.current_user

        if(user_info and (user_info.admin == "admin" or user_info.admin == "teacher") and user_info.uid != long(user_id)):
            view_user = self.user_model.get_user_by_uid(user_id)
            self.user_model.delete_user_by_uid(user_id)
            
            ftpuser_name = view_user["username"]
            print('ftp username: %s' %ftpuser_name)
            self.ftpuser_model.delete_ftpuser_by_name(ftpuser_name)
            ftpuserpath = "home/vsftpd"+ftpuser_name
            #__import__('shutil').rmtree("ftpuserpath")
            success = 0
            message = "成功获取用户实名认证信息"
        else:
            success = -1
            message = "删除用户失败"

        self.write(lib.jsonp.print_JSON({
                    "success": success,
                    "message": message
            }))

class TagsAdminHandler(BaseHandler):
    def get(self, template_variables = {}):
        template_variables["side_menu"] = "tags"
        user_info = self.current_user
        template_variables["user_info"] = user_info
        p = int(self.get_argument("p", "1"))

        if(user_info):
            if(user_info.admin == "admin"):  
                template_variables["all_tags"] = self.tag_model.get_all_tags(current_page = p)
            self.render("admin/tags.html", **template_variables)
        else:
            self.redirect("/admin/signin")

class TagEditAdminHandler(BaseHandler):
    def get(self, tag_id, template_variables = {}):
        template_variables["side_menu"] = "tags"
        user_info = self.current_user
        template_variables["user_info"] = user_info

        if(user_info and user_info.admin == "admin"):  
            view_tag = self.tag_model.get_tag_by_tag_id(tag_id)
            template_variables["view_tag"] = view_tag
            if(user_info.admin == "admin"):
                self.render("admin/tag_edit.html", **template_variables)
            else:
                self.redirect("/admin/tags")  
        else:
            self.redirect("/admin/signin")

    def post(self, tag_id, template_variables = {}):
        user_info = self.current_user
        view_tag = self.tag_model.get_tag_by_id(tag_id)

        if(user_info and user_info.admin == "admin" and view_tag):  
            update_info = {}
            data = json.loads(self.request.body)
            
            update_info = getJsonKeyValue(data, update_info, "name")
            update_info = getJsonKeyValue(data, update_info, "thumb")
            update_info = getJsonKeyValue(data, update_info, "cover")
            update_info = getJsonKeyValue(data, update_info, "intro")
            update_info = getJsonKeyValue(data, update_info, "tag_type")
            
            update_result = self.tag_model.update_tag_by_id(tag_id, update_info)

            if update_result == 0:
                success = 0
                message = "成功保存标签信息"
            else:
                success = -1
                message = "保存标签信息失败"

            self.write(lib.jsonp.print_JSON({
                    "success": success,
                    "message": message
            }))
        else:
            success = -1
            message = "保存标签信息失败"

            self.write(lib.jsonp.print_JSON({
                    "success": success,
                    "message": message
            }))     

class TagNewAdminHandler(BaseHandler):
    def get(self, template_variables = {}):
        template_variables["side_menu"] = "tags"
        user_info = self.current_user
        template_variables["user_info"] = user_info

        if(user_info and user_info.admin == "admin"):  
            self.render("admin/tag_new.html", **template_variables)
        else:
            self.redirect("/admin/signin")

    def post(self, template_variables = {}):
        user_info = self.current_user

        if(user_info and user_info.admin == "admin"):  
            update_info = {}
            data = json.loads(self.request.body)
            
            update_info = getJsonKeyValue(data, update_info, "name")
            update_info = getJsonKeyValue(data, update_info, "thumb")
            update_info = getJsonKeyValue(data, update_info, "cover")
            update_info = getJsonKeyValue(data, update_info, "intro")
            update_info = getJsonKeyValue(data, update_info, "tag_type")
            update_info["created"] = time.strftime('%Y-%m-%d %H:%M:%S')

            update_result = self.tag_model.add_new_tag(update_info)

            if update_result > 0:
                success = 0
                message = "成功新建标签"
            else:
                success = -1
                message = "新建标签失败"

            self.write(lib.jsonp.print_JSON({
                    "success": success,
                    "message": message
            }))
        else:
            success = -1
            message = "新建标签失败"

            self.write(lib.jsonp.print_JSON({
                    "success": success,
                    "message": message
            }))     

class TagDeleteAdminHandler(BaseHandler):
    def get(self, tag_id, template_variables = {}):
        user_info = self.current_user

        if(user_info and (user_info.admin == "admin")):
            self.tag_model.delete_tag_by_id(tag_id)
            success = 0
            message = "成功删除标签"
        else:
            success = -1
            message = "删除标签失败"

        self.write(lib.jsonp.print_JSON({
                    "success": success,
                    "message": message
            }))