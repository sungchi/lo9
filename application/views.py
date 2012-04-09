# -*- coding: utf-8 -*-
"""
views.py
URL route handlers
"""


from google.appengine.api import users
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

from flask import render_template, flash, url_for, redirect, request
from application import app

from models import News
from decorators import login_required, admin_required
from forms import NewsForm
from application.settings import HOST
from urlparse import urlparse
import logging
from google.appengine.ext import ndb
from datetime import datetime

PAGESIZE = 25

@app.template_filter()
def timesince(dt, default="방금"):
    now = datetime.utcnow()
    diff = now - dt 
    periods = (
        (diff.days / 365, "년"),
        (diff.days / 30, "월"),
        (diff.days / 7, "주"),
        (diff.days, "일"),
        (diff.seconds / 3600, "시간"),
        (diff.seconds / 60, "분"),
        (diff.seconds, "초"),
    )
    for period, singular in periods:
        if period:
            return "%d%s 전" % (period, singular)
    return default

@app.template_filter('date')
def date(s):
    return str(s.month)+'월 '+str(s.day)+'일 '+"%02d:%02d" % (s.hour, s.minute)

@app.template_filter('netloc')
def netloc(s):
    return urlparse(s).netloc

@ndb.toplevel
def redirect_url(post_id):
    news = News.query(News.key == ndb.Key("News",post_id)).get()
    news.view +=1
    news.put_async()
    return redirect(news.url)

def comment(post_id):
    news = News.query(News.key == ndb.Key("News",post_id)).get()
    return render_template('comment.html',article=news)

@app.route('/', defaults={'page': 1})
@app.route('/page/<int:page>')
def home(page):
    q = News.query(News.hot == True).order(-News.post_time)
    news, cursor, more =q.fetch_page(PAGESIZE,offset=PAGESIZE*(page-1))
    return render_template('index.html', news=news, page=more and page+1 or 0, host=HOST)

@app.route('/new', defaults={'page': 1})
@app.route('/new/page/<int:page>')
def new_list(page):
    q = News.query().order(-News.post_time)
    news, cursor, more =q.fetch_page(PAGESIZE,offset=PAGESIZE*(page-1))
    return render_template('new.html',news=news, page=more and page+1 or 0, host=HOST)    

def news_post():
    form = NewsForm()
    form.url.value = "test"
    if form.validate_on_submit():
        news = News(view = 0, title = form.title.data,url = form.url.data,hot = False)
        try:
            news.put()
            flash(u'저장 성공', 'success')
            return redirect(url_for('new_list'))
        except CapabilityDisabledError:
            flash(u'App Engine Datastore is currently in read-only mode.', 'failure')
            return redirect(url_for('new_list'))
    return render_template('news_post.html', form=form,title= request.args.get('title'), url= request.args.get('url'))

@app.route('/admin', defaults={'page': 1})
@app.route('/admin/page/<int:page>')
@admin_required
def admin(page):
    q = News.query().order(-News.post_time)
    news, cursor, more =q.fetch_page(PAGESIZE,offset=PAGESIZE*(page-1))
    return render_template('admin.html',news=news, page=more and page+1 or 0, host=HOST)    

def hot(post_id):
    news = News.query(News.key == ndb.Key("News",post_id)).get()
    news.hot = (news.hot and [False] or [True])[0]
    news.put()
    return ''

def bookmarklet():
    return render_template('bookmarklet.html')

def warmup():
    """App Engine warmup handler
    See http://code.google.com/appengine/docs/python/config/appconfig.html#Warming_Requests
    """
    return logging.info('Warmup Request')

