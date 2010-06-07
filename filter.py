#coding:utf-8
from datetime import timedelta
import re
import md5
import  django.template.defaultfilters as defaultfilters
from google.appengine.ext import webapp
href = re.compile(r'[a-zA-z]+://[^\s]*')
img = re.compile(r'\.(jpg|jpeg|gif|bmp|png)$')
register = webapp.template.create_template_register()
@register.filter

def timezone(value,offset):
    return value + timedelta(hours=offset)

@register.filter
def datetz(date,format='Y年m月d日, H:i '):  #datetime with timedelta
    t=timedelta(seconds=3600*8)
    return defaultfilters.date(date+t,format)

@register.filter
def textdecode(value):
    return value.replace("\n", "<br />").replace("\r\n", "<br />").replace("\t", "&nbsp;&nbsp;&nbsp;&nbsp;");

@register.filter
def filterhtml(value):
    #reg = re.compile('<[^>]+>')
    return re.sub('<[^>]+>','',value)[:300]+'......'

@register.filter
def safehtml(value):
    return value.replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br />").replace("\r\n", "<br />").replace("\t", "&nbsp;&nbsp;&nbsp;&nbsp;")

@register.filter
def ubb(value):
    rtn = safehtml(value)
    matchs = href.findall(rtn)
    if matchs:
        for match in matchs:
            rtn = rtn.replace(match,'<a href="%s" target="_blank">%s</a>' % (match,match))
    return rtn
@register.filter
def avatar(value,size=48):
    m = md5.new()
    m.update(value)
    return 'http://www.gravatar.com/avatar/%s?s=48&amp;d=&amp;r=G' %  m.hexdigest()