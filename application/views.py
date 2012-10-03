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
from forms import NewsForm, SearchForm
from application.settings import HOST
from urlparse import urlparse
import logging
from google.appengine.ext import ndb
from datetime import datetime
from urllib import quote

from google.appengine.api import search

PAGESIZE = 25
_INDEX_NAME = 'news'

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

@app.template_filter('url')
def url(s): 
    return quote(s.encode('utf8'))

@ndb.toplevel
def redirect_url(post_id):
    news = ndb.Key("News",post_id).get()
    news.view +=1
    news.put_async()
    return redirect(news.url.encode('utf-8'))

def comment(post_id):
    news = ndb.Key("News",post_id).get()
    return render_template('comment.html',article=news,host=HOST)

@app.route('/', defaults={'page': 1})
@app.route('/page/<int:page>')
def home(page):
    search_form = SearchForm()
    q = News.query(News.hot == True).order(-News.post_time)
    news, cursor, more =q.fetch_page(PAGESIZE,offset=PAGESIZE*(page-1))
    return render_template('index.html', search_form=search_form, news=news, page=more and page+1 or 0, host=HOST)

@app.route('/new', defaults={'page': 1})
@app.route('/new/page/<int:page>')
def new_list(page):
    q = News.query().order(-News.post_time)
    news, cursor, more =q.fetch_page(PAGESIZE,offset=PAGESIZE*(page-1))
    return render_template('new.html',news=news, page=more and page+1 or 0, host=HOST)    

def create_doc(id, title, url, post_time):
    return search.Document(
        fields=[search.TextField(name='id',value=str(id)),
        search.TextField(name='title',value=title),
        search.TextField(name='url',value=url),
        search.DateField(name='post_time',value=post_time)
        ])

def news_post():
    form = NewsForm()
    if form.validate_on_submit():
        news = News(view = 0, title = form.title.data,url = form.url.data,hot = False)
        try:
            news.put()
            search.Index(name=_INDEX_NAME).add(create_doc(news.key.id(),news.title,news.url,news.post_time))
            flash(u'저장 성공', 'success')
            return redirect(url_for('new_list'))
        except CapabilityDisabledError:
            flash(u'App Engine Datastore is currently in read-only mode.', 'failure')
            return redirect(url_for('new_list'))
    return render_template('news_post.html', form=form,title= request.args.get('title'), url= request.args.get('url'))

def search_keyword():
    logging.info(request.args.get('keyword'))
    results = search.Index(name=_INDEX_NAME).search("\""+request.args.get('keyword')+"\"")
    return render_template('search.html',results=results, host=HOST)

@app.route('/admin', defaults={'page': 1})
@app.route('/admin/page/<int:page>')
@admin_required
def admin(page):
    q = News.query().order(-News.post_time)
    news, cursor, more =q.fetch_page(PAGESIZE,offset=PAGESIZE*(page-1))
    return render_template('admin.html',news=news, page=more and page+1 or 0, host=HOST)    

@app.route('/admin/indexing/<int:page>')
@admin_required
def admin_index(page):
    news, cursor, more = News.query().fetch_page(250,offset=250*(page-1))
    for new in news:
        search.Index(name=_INDEX_NAME).add(create_doc(new.key.id(),new.title,new.url,new.post_time))
        logging.info("indexing: "+str(new.key.id()))
    return redirect(url_for('home'))

@app.route('/admin/index/<int:id>')
@admin_required
def admin_index(id):
    new = ndb.Key("News",id).get()
    search.Index(name=_INDEX_NAME).add(create_doc(new.key.id(),new.title,new.url,new.post_time))
    logging.info("indexing: "+str(new.key.id()))
    return redirect(url_for('home'))

#all search index data delete
@app.route('/admin/delete')
@admin_required
def index_delete():
    doc_index = search.Index(name=_INDEX_NAME)
    while True:
        document_ids = [document.doc_id for document in doc_index.list_documents(ids_only=True)]
        if not document_ids:
            break
        doc_index.remove(document_ids)

def hot(post_id):
    news = ndb.Key("News",post_id).get()
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

