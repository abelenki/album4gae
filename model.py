#coding:utf-8
import os,logging
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.api import mail
from google.appengine.api import urlfetch
import datetime

settings = None

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
        memcache.delete('ALLALBUMS')
    def Delete(self):
        self.delete()
        memcache.delete('ALLALBUMS')
    def Cover(self):
        '''封面'''
        if self.CoverId > 0:
            return 'http://%s/thumb/%s.jpeg' % (os.environ['HTTP_HOST'],self.CoverId)
        return '/static/images/cover.jpg' 
    def AlbumUrl(self):
        return 'http://%s/alubm/%s' % (os.environ['HTTP_HOST'],self.key().id())
    def GetAll(self):
        return Albums.all().order('DisplayOrder').fetch(1000)
    def Photos(self,page=1,pagesize=20):
        cachekey = "PHOTOLIST_%s_%d_%d" % (self.id(),page,pagesize)
        data = memcache.get(cachekey)
        if not data:
            limit = (page - 1) * pagesize
            data = db.GqlQuery("SELECT * FROM Photo where Album = :1 ORDER BY CreateTime DESC LIMIT "+str(limit)+","+str(pagesize) , self)
            memcache.set(cachekey,data,3600)            
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
    imgurl = db.StringProperty()
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
    EnableUpYun = db.BooleanProperty(default=True)
    UpYunBucket = db.StringProperty(default='')
    UpYunUser   = db.StringProperty(default='')
    UpYunPass   = db.StringProperty(default='')

    def __str__(self):
        return   self.SubSiteTitle+'&'+str(self.EnableUpYun)+'&'+self.UpYunBucket+'&'+self.UpYunUser+'&'+self.UpYunPass+'&'
    def id (self):
        return str(self.key().id())
    def Save(self):
        
        self.put()
        val = memcache.delete('SITE_CONFIG')
        logging.info('Delete cache SITE_CONFIG is %s,new data is %s' % (str(val),str(self)))
        global settings
        settings = None
    def get(self):
        return Settings.get_by_key_name('default')
    


def InitData():
    settings = Settings(key_name = 'default')
    settings.save()
    return settings

def site_init():
    settings = memcache.get('SITE_CONFIG')
    
    if  settings is None:
        settings = Settings.get_by_key_name('default')
    
        if settings is None:
            settings = InitData()
    
        val = memcache.set('SITE_CONFIG',settings,3600)
    
    return settings



settings =  site_init()