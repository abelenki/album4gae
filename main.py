#coding:utf-8
import wsgiref.handlers
import os
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import users
#import model
import methods
import logging
def format_date(dt):
    return dt.strftime('%a, %d %b %Y %H:%M:%S GMT')
    

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
    def get(self,id):
        album = methods.GetAlbum(id)
        if album is None:
            self.error(404)
        else:
            photos = album.Photos()
            template_value = {'photos':photos,'album':album}
            self.render('views/album.html',template_value)
class Gallery(PublicPage):
    def get(self,id):
        album = methods.GetAlbum(id)
        if album is None:
            self.error(404)
        else:
            photos = album.Photos()
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
                                        (r'/(?P<size>image)/(?P<id>[0-9]+)/?',GetImage),
                                        (r'/(?P<size>m)/(?P<id>[0-9]+)/?',GetImage),
                                        (r'/(?P<size>s)/(?P<id>[0-9]+)/?',GetImage),
                                        (r'/(?P<size>c)/(?P<id>[0-9]+)/?',GetImage),
                                        (r'/photo/(?P<id>[0-9]+)/',ShowImage),
                                        (r'/album/(?P<id>[0-9]+)/',AlbumPage),
                                        (r'/album/(?P<id>[0-9]+)/gallery\.xml',Gallery),
                                        ('.*',Error)
                                       ], debug=True)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
    main()