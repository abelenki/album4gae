#coding:utf-8
from datetime import timedelta
from google.appengine.ext import webapp
register = webapp.template.create_template_register()
@register.filter

def timezone(value,offset):
    return value + timedelta(hours=offset)