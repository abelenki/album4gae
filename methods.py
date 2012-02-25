#coding:utf-8
import model
from google.appengine.api import memcache
from google.appengine.api import images
from getimageinfo import getImageInfo

def CreateAlbum(user,name='',password=''):
    '''创建相册'''
    album = model.Albums(AlbumName=name,AlbumPassword=password,AlbumAuthor=user)
    album.Save()
    return True
def GetAllAlbums():
    albums=model.Albums().GetAll()
    return albums

def GetAlbum(id):
    return model.Albums().get_by_id(int(id))



def DeleteAlbum(id):
    album = GetAlbum(int(id))
    if album is not None:
        for a in album.Photos():
            a.delete()
        album.Delete()



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
    photo = model.Photo().get_by_id(id)
    data = {'photo':None,'prev':None,'next':None}    
    if photo is not None:
        photo.ViewCount+=1
        photo.Update()
        data['photo'] = photo
        data['prev'] = photo.Prev()
        
        data['next'] = photo.Next() #model.Photo.all().filter("Album=",photo.Album).filter(" CreateTime >",photo.CreateTime).order("CreateTime").fetch(1)
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