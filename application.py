#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2016 wanzhu

# cat /etc/mime.types
# application/octet-stream    crx

import sys
reload(sys)
sys.setdefaultencoding("utf8")

import os.path
import re
import memcache
import torndb
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

import handler.index
import handler.user
import handler.admin
import handler.api

from tornado.options import define, options
from lib.loader import Loader
from lib.session import Session, SessionManager
from jinja2 import Environment, FileSystemLoader

define("port", default = 80, help = "run on the given port", type = int)
define("mysql_host", default = "localhost", help = "community database host")
define("mysql_database", default = "wanzhu", help = "community database name")
define("mysql_user", default = "wanzhu", help = "community database user")
define("mysql_password", default = "wanzhu", help = "community database password")

class Application(tornado.web.Application):
    def __init__(self):
        settings = dict(
            blog_title = u"wanzhu",
            template_path = os.path.join(os.path.dirname(__file__), "templates"),
            static_path = os.path.join(os.path.dirname(__file__), "static"),
            root_path = os.path.join(os.path.dirname(__file__), "/"),
            xsrf_cookies = False,
            cookie_secret = "cookie_secret_code",
            login_url = "/login",
            autoescape = None,
            jinja2 = Environment(loader = FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")), trim_blocks = True),
            reserved = ["user", "topic", "home", "setting", "forgot", "login", "logout", "register", "admin"],
            debug=True,
        )

        handlers = [
            (r"/(favicon\.ico)", tornado.web.StaticFileHandler, dict(path = settings["static_path"])),
            (r"/(sitemap.*$)", tornado.web.StaticFileHandler, dict(path = settings["static_path"])),
            (r"/(bdsitemap\.txt)", tornado.web.StaticFileHandler, dict(path = settings["static_path"])),
            (r"/(orca\.txt)", tornado.web.StaticFileHandler, dict(path = settings["static_path"])),

            (r"/", handler.index.IndexHandler),
            (r"/reviews", handler.index.ReviewsHandler),
            (r"/bbs", handler.index.BbsHandler),
            (r"/new", handler.index.NewHandler),
            (r"/t/(.*)", handler.index.TagHandler), 
            (r"/p/(\d+)", handler.index.PostHandler),
            (r"/reply/(\d+)", handler.index.ReplyHandler),
            (r"/upload/image", handler.index.UploadImageHandler),
            (r"/signin", handler.user.SigninHandler),
            (r"/signout", handler.user.SignoutHandler),
            (r"/signup", handler.user.SignupHandler),
            (r"/admin", handler.admin.IndexAdminHandler),
            (r"/admin/signin", handler.admin.SigninAdminHandler),
            (r"/admin/signout", handler.admin.SignoutAdminHandler),
            (r"/admin/signup", handler.admin.SignupAdminHandler),
            (r"/admin/users", handler.admin.UsersAdminHandler),
            (r"/admin/user/new", handler.admin.UserNewAdminHandler),
            (r"/admin/user/edit/(\d+)", handler.admin.UserEditAdminHandler),
            (r"/admin/user/delete/(\d+)", handler.admin.UserDeleteAdminHandler),
            (r"/admin/newsfeeds", handler.admin.NewsfeedsAdminHandler),
            (r"/admin/newsfeed/new", handler.admin.NewsfeedNewAdminHandler),
            (r"/admin/newsfeed/edit/(\d+)", handler.admin.NewsfeedEditAdminHandler),
            (r"/admin/nowfeeds", handler.admin.NowfeedsAdminHandler),
            (r"/admin/nowfeed/new", handler.admin.NowfeedNewAdminHandler),
            (r"/admin/nowfeed/edit/(\d+)", handler.admin.NowfeedEditAdminHandler),
            (r"/admin/nowfeed/delete/(\d+)", handler.admin.NowfeedDeleteAdminHandler),
            (r"/admin/tags", handler.admin.TagsAdminHandler),
            (r"/admin/tag/new", handler.admin.TagNewAdminHandler),
            (r"/admin/tag/edit/(\d+)", handler.admin.TagEditAdminHandler),
            (r"/admin/tag/delete/(\d+)", handler.admin.TagDeleteAdminHandler),
            (r"/admin/carbrands", handler.admin.CarBrandsAdminHandler),
            (r"/admin/carvenders", handler.admin.CarVendersAdminHandler),
            (r"/admin/carmodels", handler.admin.CarModelsAdminHandler),
            (r"/admin/cardata/new", handler.admin.CarDataNewAdminHandler),
            (r"/admin/cardata/edit/(\d+)", handler.admin.CarDataEditAdminHandler),
            (r"/api/signin", handler.api.SigninApiHandler),
            (r"/api/signout", handler.api.SignoutApiHandler),
            (r"/api/setting/password", handler.api.SettingPasswordApiHandler),
            (r"/api/get/user/base", handler.api.GetUserBaseInfoApiHandler),
            (r"/api/update/user/base", handler.api.UpdateUserBaseInfoApiHandler),
            (r"/get/tags", handler.index.GetTagsHandler),
        ]

        tornado.web.Application.__init__(self, handlers, **settings)

        # Have one global connection to the blog DB across all handlers
        self.db = torndb.Connection(
            host = options.mysql_host, database = options.mysql_database,
            user = options.mysql_user, password = options.mysql_password
        )

        # Have one global loader for loading models and handles
        self.loader = Loader(self.db)

        # Have one global model for db query
        self.user_model = self.loader.use("user.model")
        self.post_model = self.loader.use("post.model")
        self.nowfeed_model = self.loader.use("nowfeed.model")
        self.newsfeed_model = self.loader.use("newsfeed.model")
        self.reply_model = self.loader.use("reply.model")
        self.tag_model = self.loader.use("tag.model")
        self.post_tag_model = self.loader.use("post_tag.model")
        self.car_data_model = self.loader.use("car_data.model")

        # Have one global session controller
        self.session_manager = SessionManager(settings["cookie_secret"], ["127.0.0.1:11211"], 0)

        # Have one global memcache controller
        self.mc = memcache.Client(["127.0.0.1:11211"])

        DEBUG_FLAG = True
        if DEBUG_FLAG:
            self.debug_flag = True
            self.static_path = "/static"
            self.template_path = ""
        else:
            self.debug_flag = False
            self.static_path = "/static/dist"
            self.template_path = "dist/"

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
