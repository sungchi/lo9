# -*- coding: utf-8 -*-
"""
urls.py

URL dispatch route mappings and error handlers

"""

from flask import render_template

from application import app
from application import views


## URL dispatch rules
# App Engine warm up handler
# See http://code.google.com/appengine/docs/python/config/appconfig.html#Warming_Requests
app.add_url_rule('/_ah/warmup', 'warmup', view_func=views.warmup)

# News Post
app.add_url_rule('/post', 'news_post', view_func=views.news_post, methods=['GET', 'POST'])

# redirect
app.add_url_rule('/<int:post_id>', 'redirect_url', view_func=views.redirect_url, methods=['GET'])

# comment
app.add_url_rule('/<int:post_id>/c', 'comment', view_func=views.comment, methods=['GET'])

# hot switch
app.add_url_rule('/hot/<int:post_id>', 'hot', view_func=views.hot, methods=['GET'])

# bookmarklet
app.add_url_rule('/bookmarklet', 'bookmarklet', view_func=views.bookmarklet)

## Error handlers
# Handle 404 errors
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Handle 500 errors
@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

