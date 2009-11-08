#coding=utf-8
import wsgiref.handlers
import os
from functools import wraps
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import users
import methods,logging
import model
from django.utils import simplejson


adminFlag=True


class AdminControl(webapp.RequestHandler):
    def render(self,template_file,template_value):
        path=os.path.join(os.path.dirname(__file__),template_file)
        self.response.out.write(template.render(path, template_value))
    def returnjson(self,dit):
        self.response.headers['Content-Type'] = "application/json"
        self.response.out.write(simplejson.dumps(dit))

def requires_admin(method):
    @wraps(method)
    '''用户权限验证包装器'''
    def wrapper(self, *args, **kwargs):
        if not users.is_current_user_admin() and adminFlag:
            self.redirect(users.create_login_url(self.request.uri))
        else:
            return method(self, *args, **kwargs)
    return wrapper

class AdminMain(AdminControl):
    @requires_admin
    def get(self):
        self.render('views/admin/index.html',{'albums':methods.GetAllAlbums()})
class AdminLeft(AdminControl):
    @requires_admin
    def get(self):
        self.render('views/admin/left.html',{})
class AdminTop(AdminControl):
    @requires_admin
    def get (self):
        self.render('views/admin/top.html',{'username':users.get_current_user(),'logouturl':users.create_logout_url('http://'+os.environ['HTTP_HOST'])})

class PhotoList(AdminControl):
    @requires_admin
    def get(self,id):
        album = methods.GetAlbum(id)
        photos = album.Photos()
        data = {'albums':methods.GetAllAlbums(),'photos':photos,'albumid':id}
        self.render('views/admin/photos.html',data)
    def post(self,id):
        alid = int(self.request.get('alid'))
        if len(self.request.get('setcover')) > 0:
            pid = self.request.get('deleteid')
            album = methods.GetAlbum(alid)
            album.CoverId = int(pid)
            album.Save()
        else:
            ids =  self.request.get_all('deleteid')
            for i in ids:
                methods.DeletePhoto(int(i))
        self.redirect('/admin/'+str(alid)+'/')

class Admin_Upload(AdminControl):
    @requires_admin
    def get(self):
        self.render('views/admin/upload.html', {'albums':methods.GetAllAlbums()})
    @requires_admin
    def post(self):
        bf=self.request.get("file")
        if not bf:
            return self.redirect('/admin/upload/')
            #name=self.request.body_file.vars['file'].filename
        mime = self.request.body_file.vars['file'].headers['content-type']
        if mime.find('image')==-1:
            return self.redirect('/admin/upload/')
        description=self.request.get("Description")
        name = self.request.get("Name")
        album = model.Albums().get_by_id(int(self.request.get("album")))
        image=methods.AddPhoto(name,description,mime,album,users.get_current_user(),bf)
        self.redirect('/admin/upload/')

class Admin_CreateAlbum(AdminControl):
    def get(self):
        self.render('views/admin/album.html',{'albums':methods.GetAllAlbums()})
    def post(self):
        methods.CreateAlbum(users.get_current_user(),self.request.get('albumname'),'')
        self.redirect('/admin/albums/',{})

class AdminEditAlbum(AdminControl):
    @requires_admin
    def get (self,id,*avg):
        album = methods.GetAlbum(int(id))
        self.render('views/admin/editalbum.html',{'album':album})
    @requires_admin
    def post(self,id,*avg):
        album = methods.GetAlbum(int(self.request.get('albumid')))
        album.AlbumName = self.request.get('AlbumName')
        album.DisplayOrder = int(self.request.get('DisplayOrder'))
        album.Save()
        #self.redirect('/admin/albums/')
        self.response.out.write('<script type="text/javascript">window.parent.location.reload();</script>')

class AdminDeleteAlbum(AdminControl):
    @requires_admin
    def get(self,id):
        methods.DeleteAlbum(int(id))
        self.redirect('/admin/albums/')
    


class Admin_Login(AdminControl):
    @requires_admin
    def get(self):
        self.redirect('/')
        
def main():
    webapp.template.register_template_library('filter')
    application = webapp.WSGIApplication(
                   [(r'/admin/upload/', Admin_Upload),
                    (r'/admin/deleteAlbum/(?P<id>[0-9]+)/',AdminDeleteAlbum),
                    (r'/admin/albums/', Admin_CreateAlbum),
                    (r'/admin/',AdminMain),
                    (r'/admin/(?P<id>[0-9]+)/',PhotoList),
                    (r'/admin/left/',AdminLeft),
                    (r'/admin/top/',AdminTop),
                    (r'/admin/edit/(?P<id>[0-9]+)/(.*)',AdminEditAlbum),
                   ], debug=True)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
    main()