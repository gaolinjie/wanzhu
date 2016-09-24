#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2013 mifan.tv

from lib.query import Query

class NowfeedModel(Query):
    def __init__(self, db):
        self.db = db
        self.table_name = "nowfeed"
        super(NowfeedModel, self).__init__()

    def add_new_nowfeed(self, nowfeed_info):
        return self.data(nowfeed_info).add()

    def get_nowfeed_by_id(self, nowfeed_id):
        where = "nowfeed.id = '%s'" % nowfeed_id
        return self.where(where).find()

    def update_nowfeed_by_id(self, nowfeed_id, nowfeed_info):
        where = "nowfeed.id = %s" % nowfeed_id
        return self.where(where).data(nowfeed_info).save()

    def get_all_nowfeeds(self, num = 10, current_page = 1):
        order = "nowfeed.id DESC"
        field = "nowfeed.*"
        return self.order(order).field(field).pages(current_page = current_page, list_rows = num) 

    def get_all_nowfeeds_count(self):
        return self.count()

    def delete_nowfeed_by_id(self, nowfeed_id):
        where = "nowfeed.id = %s " % nowfeed_id
        return self.where(where).delete()