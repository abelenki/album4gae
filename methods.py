#coding:utf-8
import model
from google.appengine.api import memcache
from google.appengine.api import images
from getimageinfo import getImageInfo

def cache(key="",time=3600):
    def _decorate(method):
        def _wrapper(*args, **kwargs):
            val = memcache.get(key)
            if val is None:
                val = method(*args, **kwargs)
                memcache.set(key,val,time)
            return val
        return _wrapper
    return _decorate


def CreateAlbum(user,name='',password=''):
    '''创建相册'''
    album = model.Albums(AlbumName=name,AlbumPassword=password,AlbumAuthor=user)
    album.Save()
    memcache.delete('ALLALBUMS')
    return True
@cache(key='ALLALBUMS',time=3600)
def GetAllAlbums():

    albums=model.Albums().GetAll()
    return albums

def GetAlbum(id):
    cachekey='album_'+str(id)
    data = memcache.get(cachekey)
    if not data:
        data = model.Albums().get_by_id(int(id))
        memcache.set(cachekey,data,3600)
    return data



def DeleteAlbum(id):
    album = GetAlbum(int(id))
    if album is not None:
        for a in album.Photos():
            a.delete()
        album.Delete()
    memcache.delete('ALLALBUMS')



def AddPhoto(name,description,mime,album,user,stream):
    'Add Photo'
    photo = model.Photo()
    photo.Album = album
    photo.Author = user
    photo.Description = description
    photo.Mime = mime
    photo.Name = name
    photo.PhotoStream = stream
    photo.Size=len(stream)
    photo.FileType,photo.Width,photo.Height=getImageInfo(stream)
    photo.Save()
    return photo

def DeletePhoto(id):
    photo =  model.Photo().get_by_id(int(id))
    if photo is not None:
        photo.Album.PhotoCount -=1
        photo.Album.put()
        photo.delete()


def GetPhoto(id):
    id=int(id)
    cachekey='photo_'+str(id)

    data = memcache.get(cachekey)
    if not data:
        photo = model.Photo().get_by_id(id)
        data = {'photo':None,'prev':None,'next':None}    
        if photo is not None:
            #photo.ViewCount+=1
            #photo.Update()
            data['photo'] = photo
            data['prev'] = photo.Prev()
            data['next'] = photo.Next()
            memcache.set(cachekey,data,3600)
    return data;    



def downImage(id,size="image"):
    key=id+'_CACHE_'+size
    image=memcache.get(key)
    if not image:
        image=resizeImage(id, size)
        memcache.set(key,image,1800)
    return image

def resizeImage(id,size="image"):
    image=GetPhoto(id)
    image = image['photo'];
    if not image:return None
    if size=="image":return image
    img=images.Image(image.PhotoStream)
    width = height = 200
    if size == 'thumb':
        width = 140
        height = 100
    img.resize(width,height)
    img.im_feeling_lucky()
    image.PhotoStream=img.execute_transforms(output_encoding=images.JPEG)
    return image


def Settings():
    pass