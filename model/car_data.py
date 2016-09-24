#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2013 meiritugua.com

import time
from lib.query import Query

class Car_dataModel(Query):
    def __init__(self, db):
        self.db = db
        self.table_name = "car_data"
        super(Car_dataModel, self).__init__()

    def add_new_car_data(self, car_data_info):
        return self.data(car_data_info).add()

    def update_car_data_by_id(self, car_data_id, car_data_info):
        where = "car_data.id = %s" % car_data_id
        return self.where(where).data(car_data_info).save()

    def delete_car_data_by_id(self, car_data_id):
        where = "car_data.id = %s " % car_data_id
        return self.where(where).delete()

    def get_car_data_by_id(self, car_data_id):
        where = "car_data.id = %s " % car_data_id
        return self.where(where).find()

    def get_all_car_brands(self, num = 10, current_page = 1):
    	where = "car_data.data_type = 'car_brand'"
        order = "car_data.id DESC"
        field = "car_data.*"
        return self.where(where).order(order).field(field).pages(current_page = current_page, list_rows = num) 

    def get_all_car_venders(self, num = 10, current_page = 1):
    	where = "car_data.data_type = 'car_vender'"
        order = "car_data.id DESC"
        field = "car_data.*"
        return self.where(where).order(order).field(field).pages(current_page = current_page, list_rows = num) 

    def get_all_car_models(self, num = 10, current_page = 1):
    	where = "car_data.data_type = 'car_model'"
        order = "car_data.id DESC"
        field = "car_data.*"
        return self.where(where).order(order).field(field).pages(current_page = current_page, list_rows = num) 

    def get_car_models_by_sort(self, car_sort, num = 4, current_page = 1):
        where = "car_data.data_type = 'car_model' AND car_data.car_sort = '%s'" % car_sort
        order = "car_data.id DESC"
        field = "car_data.*"
        return self.where(where).order(order).field(field).pages(current_page = current_page, list_rows = num) 

        
