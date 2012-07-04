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
from google.appengine.api import memcache
from model import settings
import upyun
adminFlag=True #comment



class AdminControl(webapp.RequestHandler):
    def __init__(self):
        super(AdminControl,self).__init__()
    def render(self,template_file,template_value):
        path=os.path.join(os.path.dirname(__file__),template_file)
        self.response.out.write(template.render(path, template_value))
    def returnjson(self,dit):
        self.response.headers['Content-Type'] = "application/json"
        self.response.out.write(simplejson.dumps(dit))

def requires_admin(method):

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if not users.is_current_user_admin() and adminFlag:
            self.redirect(users.create_login_url(self.request.uri))
        else:
            return method(self, *args, **kwargs)
    return wrapper


class AdminSettings(AdminControl):
    @requires_admin
    def get(self):
        self.render('views/admin/setting.html',{'setting':settings})
    def post(self):
        SiteTitle = self.request.get('SiteTitle')
        SubSiteTitle = self.request.get('SubSiteTitle')
        EnableUpYun = self.request.get('EnableUpYun')
        UpYunBucket = self.request.get('UpYunBucket')
        UpYunUser   = self.request.get('UpYunUser')
        UpYunPass   = self.request.get('UpYunPass')
        model.site_init()
        config = model.settings
        config.SiteTitle = SiteTitle
        config.SubSiteTitle = SubSiteTitle
        config.EnableUpYun = EnableUpYun == "1" 
        config.UpYunBucket = UpYunBucket
        config.UpYunUser = UpYunUser
        config.UpYunPass = UpYunPass
        config.Save()
        self.redirect('/admin/settings/')


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
        yun= upyun.UpYun()
        diskUsage = 0
        try:
            diskUsage = (yun.getBucketUsage()+.0)/1024/1024
        except Exception:
            pass
        self.render('views/admin/top.html',{'username':users.get_current_user(),
            'logouturl':users.create_logout_url('http://'+os.environ['HTTP_HOST']),
            'usage':'%.2f M'%(diskUsage)
            })

class PhotoList(AdminControl):
    @requires_admin
    def get(self,id):
        album = methods.GetAlbum(id)
        photos = album.Photos(page=1,pagesize=1000)
        data = {'albums':methods.GetAllAlbums(),'photos':photos,'albumid':id,'settings':model.settings}
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
        self.render('views/admin/upload.v2.html', {'albums':methods.GetAllAlbums()})
    @requires_admin
    def post(self):
        bf=self.request.get("Filedata")
        self.response.out.write(self.request)
        return
        if not bf:
            return self.redirect('/admin/upload/')
#        name=self.request.body_file.vars['file'].filename
        mime = self.request.body_file.vars['Filedata'].headers['content-type']
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
        methods.CreateAlbum(users.get_current_user(),self.request.get('albumname'),'',self.request.get('summary'))
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
        album.Summary = self.request.get('Summary')
        album.Save()
        #self.redirect('/admin/albums/')
        self.response.out.write('<script type="text/javascript">window.parent.location.reload();</script>')


class AdminEditPhoto(AdminControl):
    @requires_admin
    def get(self,id,*avg):
        photo = methods.GetPhoto(int(id))
        self.render('views/admin/editphoto.html',{'photo':photo})
    def post(self,id,*avg):
        photo = methods.GetPhoto(int(id))
        photo.Name = self.request.get('Name')
        photo.Description = self.request.get('Description')
        photo.Update()
        memcache.delete('PHOTO_'+str(id))
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
                   [
                   ('/admin/?',AdminMain),
                   (r'/admin/upload/', Admin_Upload),
                    (r'/admin/settings/', AdminSettings),
                    (r'/admin/deleteAlbum/(?P<id>[0-9]+)/',AdminDeleteAlbum),
                    (r'/admin/albums/', Admin_CreateAlbum),
                    
                    (r'/admin/(?P<id>[0-9]+)/',PhotoList),
                    (r'/admin/left/',AdminLeft),
                    (r'/admin/top/',AdminTop),
                    (r'/admin/edit/(?P<id>[0-9]+)/(.*)',AdminEditAlbum),
                    (r'/admin/editphoto/(?P<id>[0-9]+)/(.*)',AdminEditPhoto),
                   ], debug=True)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
    main()
