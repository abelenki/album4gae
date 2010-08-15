#coding:utf-8
import os,logging
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.api import mail
from google.appengine.api import urlfetch

class Comment(db.Model):
    Author = db.StringProperty()
    Ip = db.StringProperty()
    CommentDate = db.DateTimeProperty()
    CommentBody = db.StringProperty()
    #Photo = db.ReferenceProperty(Photo)
    @property
    def Id(self):
        return str(self.key().id())
    def Post(self):
        self.put()
    
class Albums(db.Model):
    '''相册数据模型'''
    AlbumName = db.StringProperty()
    PhotoCount = db.IntegerProperty(default=0)
    AlbumPassword = db.StringProperty()
    AlbumCreateDate = db.DateTimeProperty(auto_now_add = True)
    AlbumAuthor = db.UserProperty()
    LastUpdate = db.DateTimeProperty(auto_now=True)
    CreateDate = db.DateTimeProperty(auto_now_add = True)
    DisplayOrder = db.IntegerProperty(default = 0)
    CoverId = db.IntegerProperty(default = 0)
    def id(self):
        return str(self.key().id())
    def Save(self):
        self.put()
    def Delete(self):
        self.delete()
    def Cover(self):
        '''封面'''
        if self.CoverId > 0:
            return 'http://%s/thumb/%s.jpeg' % (os.environ['HTTP_HOST'],self.CoverId)
        return '/static/images/cover.jpg' 
    def AlbumUrl(self):
        return 'http://%s/alubm/%s' % (os.environ['HTTP_HOST'],self.key().id())
    def GetAll(self):
        return Albums.all().order('DisplayOrder').order('-LastUpdate').fetch(1000)
    def Photos(self,page=1,pagesize=20):
        limit = (page - 1) * pagesize
        data = db.GqlQuery("SELECT * FROM Photo where Album = :1 ORDER BY CreateTime DESC LIMIT "+str(limit)+","+str(pagesize) , self)
        return data
        #return Photo.all().filter('Album =',self).order('-CreateTime').fetch(limit,offset)

class Photo(db.Model):
    '''照片数据模型'''
    Name = db.StringProperty()
    Description = db.StringProperty()
    Mime = db.StringProperty()
    Size = db.IntegerProperty()
    CreateTime = db.DateTimeProperty(auto_now_add = True)
    FileType = db.StringProperty()
    ViewCount = db.IntegerProperty(default = 0)
    Width = db.IntegerProperty()
    Height = db.IntegerProperty()
    EXIF = db.StringProperty()
    Author = db.UserProperty()
    State = db.IntegerProperty(default = 1)
    PhotoStream = db.BlobProperty()
    Album = db.ReferenceProperty(Albums) 
    Comments = db.ReferenceProperty(Comment)
    #left    = db.IntegerProperty(default=0)
    #top     = db.IntegerProperty(default=0)
    #rot     = db.IntegerProperty(default=0)
    def id(self):
        return str(self.key().id())
    def Save(self):
        '''添加或修改'''
        self.put()
        self.Album.PhotoCount +=1
        
        self.Album.Save()
    def PhotoUrl(self):
        return "http://%s/photo/%s.jpeg" %(os.environ['HTTP_HOST'],self.key().id())
    def Update(self):
        self.put()
    def Prev(self):
        prev =  Photo.all().filter('Album',self.Album).filter('CreateTime < ',self.CreateTime).order('-CreateTime').fetch(1)
        if len(prev) == 1:
            return prev[0]
        return None
    def Next(self):
        next =  Photo.all().filter('Album',self.Album).filter('CreateTime > ',self.CreateTime).order('CreateTime').fetch(1)
        if len(next) == 1:
            return next[0]
        return None
        
class Settings(db.Model):
    SiteTitle = db.StringProperty(default=u'我的相册')
    SubSiteTitle = db.StringProperty(default='')
    Version = 1.0
    Timedelta = db.FloatProperty(default = 8.0)
    def id (self):
        return str(self.key().id())
    def Save(self,key,value):
        self.put()
    def initSettings(self):
        pass

