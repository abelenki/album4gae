#coding:utf-8
import wsgiref.handlers
import os
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import users
import math
import methods
import logging
import random
import model
def format_date(dt):
    return dt.strftime('%a, %d %b %Y %H:%M:%S GMT')


class SwfUpload(webapp.RequestHandler):
    def get(self):
        self.response.out.write('GET')
        return
    def post(self):
       
        bf=self.request.get("Filedata")
       
        if not bf:
            return self.redirect('/admin/upload/')
#        name=self.request.body_file.vars['file'].filename
        #mime = self.request.body_file.vars['Filedata'].headers['content-type']
        #if mime.find('image')==-1:
        #    return self.redirect('/admin/upload/')
        description=self.request.get("Description")
        name = self.request.get("Name")
        album = model.Albums().get_by_id(int(self.request.get("album")))
        image=methods.AddPhoto(name,description,'images/jpg',album,users.get_current_user(),bf)
        self.response.out.write(image.id())
        return


class PublicPage(webapp.RequestHandler):
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
    
class MainPage(PublicPage):
    def get(self,page):
        albums=methods.GetAllAlbums()
        template_value={"albums":albums[:24],"isadmin":self.is_admin()}
        self.render('views/index.html', template_value)

class AlbumPage(PublicPage):
    def get(self,id,page):
        MAX_WEIGTH = 988
        MAX_HEIGHT = 700
        album = methods.GetAlbum(id)
        pagesize = 40
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
            template_value = {'photos':_photos,'album':album}
            template_value.update(page=page)
            template_value.update(pagecount = pagecount)
            template_value.update(pages = range(1,pagecount + 1))
            template_value.update(pagesize=pagesize)
            template_value.update(url=('/album/%s/page' % id))
            self.render('views/albumV6.html',template_value)


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
        self.response.headers['Content-Type'] = str(image.Mime) 
        self.response.headers['Cache-Control']="max-age=315360000"
        self.response.headers['Last-Modified']=format_date(image.CreateTime)
        self.response.out.write(image.PhotoStream)

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
                                        ('.*',Error)
                                       ], debug=True)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
    main()