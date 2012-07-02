#coding:utf-8
import wsgiref.handlers
import os
from google.appengine.api import memcache

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import users
import math
import methods
import logging
import random
import model
import time

import datetime

from upyun import UpYun,md5,md5file
yun = None

def format_date(dt):
    return dt.strftime('%a, %d %b %Y %H:%M:%S GMT')




class PublicPage(webapp.RequestHandler):
    def __init__(self):
        super(PublicPage,self).__init__()
        setting = model.settings
        global yun
        yun= UpYun(username = setting.UpYunUser,password=setting.UpYunPass,bucket=setting.UpYunBucket)
        diskUsage = 0
        try:
            diskUsage = (yun.getBucketUsage()+.0)/1024/1024
        except Exception:
            pass
        self.usage = '%.2f M'%(diskUsage)
        #setting.initSettings()
        
    def render(self, template_file, template_value):

        path = os.path.join(os.path.dirname(__file__), template_file)
        self.response.out.write(template.render(path, template_value))
    def error(self,code):
        if code==400:
            self.response.set_status(code)
        else:
            self.response.set_status(code)
    def is_admin(self):
        return users.is_current_user_admin()
    
    def head(self, *args):
        return self.get(*args) 
    


class SwfUpload(PublicPage):
    def get(self):
        self.response.out.write('GET')
        return
    def post(self):
       
        bf=self.request.get("Filedata")
        if not bf:
            return self.redirect('/admin/upload/')
        path = '/album/'+ datetime.datetime.now().strftime('%m')+ '/'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'.jpg'
        a = yun.writeFile(path,bf,True)
        logging.info('upload result:'+str(a))
        if a == True:
            description=self.request.get("Description")
            name = self.request.get("Name")
            album = model.Albums().get_by_id(int(self.request.get("album")))
            imageurl = 'http://imgstore.b0.upaiyun.com'+path
            image = methods.AddPhoto(name,description,'images/jpg',album,users.get_current_user(),bf,imageurl)
            self.response.out.write(imageurl+"!thumb")
        else:
            logging.info('upload image to upyun error:'+str(a))
            self.response.out.write(0)
        return

class MainPage(PublicPage):
    def get(self,page):
        
        if self.request.get('flush') is not None:
            memcache.flush_all()
        albums=methods.GetAllAlbums()
        template_value={"albums":albums[:24],"isadmin":self.is_admin(),"config":model.settings,
        'usage':self.usage
        }
        self.render('views/index.js.html', template_value)


class CrossDomain(PublicPage):
    def get(self):
        self.response.headers['Content-Type'] = 'text/xml' 
        
        self.render('views/crossdomain.xml',{})

class AlbumPage(PublicPage):
    def get(self,id,page):
        MAX_WEIGTH = 988
        MAX_HEIGHT = 700
        album = methods.GetAlbum(id)
        pagesize = 1000
        pagecount = 1
        if page is None:page = 1
        page = int(page)
        if album is None:
            self.error(404)
        else:
            pagecount = int(math.ceil(float(album.PhotoCount)/pagesize))
            offset = (page-1)*pagesize
            limit = offset + pagesize
            #_photos = album.Photos(offset,pagesize)
            #_photos = _photos[offset:limit]
            _photos = album.Photos(page,pagesize)
            #for a in _photos:
            #    a.left = random.randint(0,MAX_WEIGTH)
            #    a.top=random.randint(0,400)
            #    a.rot = random.randint(-40,40)
            #    if a.top>MAX_HEIGHT-130 and a.left > MAX_WEIGTH-230 :
            #        a.top-=120+130
            #        a.left-=230
            template_value = {'photos':_photos,'album':album,'config':model.settings,'usage':self.usage}
            template_value.update(page=page)
            template_value.update(pagecount = pagecount)
            template_value.update(pages = range(1,pagecount + 1))
            template_value.update(pagesize=pagesize)
            template_value.update(url=('/album/%s/page' % id))
            self.render('views/album.js.html',template_value)


class Gallery(PublicPage):
    def get(self,id):
        album = methods.GetAlbum(id)
        if album is None:
            self.error(404)
        else:
            photos = album.Photos
            template_value = {'photos':photos,'album':album}
            self.response.headers['Content-Type'] = 'application/xml'
            self.render('views/gallery.html',template_value)
class ShowImage(PublicPage):
    def get(self,id):
        data=methods.GetPhoto(id)        
        if not data['photo']:return self.error(404)
        template_value={"image":data,"admin":self.is_admin()}
        
        self.render('views/show.html', template_value)
    
    
class GetImage(PublicPage):
    def get(self,size,id):
        dic=self.request.headers
        key=dic.get("If-None-Match")
        self.response.headers['ETag']=size+id
        if key and key==size+id:
            return self.error(304)
        image=methods.downImage(id, size)
        if not image:
            return self.error(404)
        self.redirect(image) 
        #self.response.headers['Content-Type'] = str(image.Mime) 
        #self.response.headers['Cache-Control']="max-age=315360000"
        #self.response.headers['Last-Modified']=format_date(image.CreateTime)
        #self.response.out.write(image.PhotoStream)

class Error(PublicPage):
    def get(self):
        return self.error(404)

def main():
    webapp.template.register_template_library('filter')
    application = webapp.WSGIApplication(
                                       [('/(?P<page>[0-9]*)/?', MainPage),
                                        (r'/(?P<size>image)/(?P<id>[0-9]+)\.jpeg',GetImage),
                                        (r'/(?P<size>thumb)/(?P<id>[0-9]+)\.jpeg',GetImage),
                                        (r'/photo/(?P<id>[0-9]+)\.jpeg',ShowImage),
                                        (r'(?:/album/(?P<id>[0-9]+))?(?:/page/?(?P<page>[0-9]+))?/?',AlbumPage),
                                        (r'/album/(?P<id>[0-9]+)/gallery\.xml',Gallery),
                                        (r'/SwfUpload/',SwfUpload),
                                        (r'/crossdomain\.xml',CrossDomain),
                                        ('.*',Error)
                                       ], debug=True)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
    main()