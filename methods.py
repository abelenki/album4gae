#coding:utf-8
import model
from google.appengine.api import memcache
from google.appengine.api import images
from getimageinfo import getImageInfo
from utility import cacheV2

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


@cacheV2('ALBUM_{id}')
def GetAlbum(id):
    data = model.Albums().get_by_id(int(id))
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
    memcache.delete('ALLALBUMS')
    return photo

def DeletePhoto(id):
    photo =  model.Photo().get_by_id(int(id))
    if photo is not None:
        photo.Album.PhotoCount -=1
        photo.Album.put()
        photo.delete()
        memcache.delete('ALLALBUMS')






@cacheV2('PHOTO_{id}')
def GetPhoto(id):
    '''根据ID获取单张相片'''
    id=int(id)
    photo = model.Photo().get_by_id(id)
    return photo 

    
    if photo is not None:
        #photo.ViewCount+=1
        #photo.Update()
        data['photo'] = photo
        data['prev'] = photo.Prev()
        data['next'] = photo.Next()
    return data;    


@cacheV2('PREV_PHOTO_{id}')
def PrevPhoto(id):
    photo = GetPhoto(id)
    if photo is not None:
        return photo.Prev()
    return None

@cacheV2('NEXT_PHOTO_{id}')
def NextPhoto(id):
    photo = GetPhoto(id)
    if photo is not None:
        return Photo.Next()
    return None


def downImage(id,size="image"):
    image = resizeImage(id,size)
    return image

def resizeImage(id,size="image"):
    image=GetPhoto(id)
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