# -*- coding: utf-8 -*-

"""
models.py

App Engine datastore models

"""

from google.appengine.ext import ndb

class News(ndb.Model):
    post_time = ndb.DateTimeProperty(auto_now_add=True)
    view = ndb.IntegerProperty()
    title = ndb.StringProperty()
    url = ndb.StringProperty()
    hot = ndb.BooleanProperty()
