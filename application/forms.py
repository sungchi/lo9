# -*- coding: utf-8 -*-
"""
forms.py

Web forms based on Flask-WTForms

See: http://flask.pocoo.org/docs/patterns/wtforms/
     http://wtforms.simplecodes.com/

"""

from flaskext import wtf
from flaskext.wtf import validators
from flaskext.wtf.html5 import URLField

class NewsForm(wtf.Form):
    url = URLField('주소',validators=[validators.Required()])
    title = wtf.TextField('제목', validators=[validators.Required()])
