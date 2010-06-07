#coding:utf-8
import wsgiref.handlers
import os
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import users
import model
import math
import methods
import logging
import datetime
import md5
def format_date(dt):
    return dt.strftime('%a, %d %b %Y %H:%M:%S GMT')


def pager(totalcount = 0,page = 1,pagesize = 10,param="{p}"):

    if (totalcount <= 0):
        return ''
    
    pagestr = ''
    count = totalcount
    perpage = pagesize
    currentpage = page
    pagecount = int(math.ceil(float(totalcount) / pagesize))
    if pagecount==1:
        return ''
    #return 'totalcount:%d,pagesize:%d,page:%d' % (totalcount,pagesize,page)
    pagestr = ""
    breakpage = 3
    currentposition = 3
    breakspace = 2
    maxspace = 3
    prevnum = currentpage - currentposition
    nextnum = currentpage + currentposition
    if prevnum < 1:
        prevnum = 1

    if nextnum > pagecount:
        nextnum = pagecount
    if currentpage==1:
        pass
        #pagestr +='<span class=\"current\">&laquo;</span>'
    else:
        pagestr +='<a href="%s">&laquo;</a>' % (param.replace('{p}',str(currentpage - 1)))
    if (prevnum - breakspace > maxspace):
        for i in range(1,breakspace+1):
            pagestr +='<a href="%s">%s</a>' % ( param.replace('{p}',str(i)),i)
        pagestr += '<span class="break">...</span>'
        
        for i in range(pagecount - breakpage + 1,prevnum):
            pagestr +='<a href="%s">%s</a>' % ( param.replace('{p}',str(i)),i)
    else:
        for i in range(1,prevnum):
            pagestr +='<a href="%s">%s</a>' % ( param.replace('{p}',str(i)),i)
    
    for i in range(prevnum,nextnum+1):
        if currentpage == i:
            pagestr +='<span class="current">%d</span>' % i
        else:
            pagestr +='<a href="%s">%s</a>' % ( param.replace('{p}',str(i)),i)
    if pagecount - breakspace - nextnum + 1 > maxspace:
        for i in range(nextnum + 1,breakpage+1):
            pagestr +='<a href="%s">%s</a>' % ( param.replace('{p}',str(i)),i)
        pagestr += '<span class="extend">...</span>';
        for i in range(pagecount - breakspace + 1,pagecount+1) :
            pagestr +='<a href="%s">%s</a>' % ( param.replace('{p}',str(i)),i)
    else:
        for i in range(nextnum + 1,pagecount+1):
            pagestr +='<a href="%s">%s</a>' % ( param.replace('{p}',str(i)),i)
    if currentpage == pagecount:
        pass
        #pagestr += '<span class=\"current\">&raquo;</span>'
    else:
        pagestr +='<a href="%s">&raquo;</a>' % param.replace('{p}', str(currentpage + 1))
    
    pagestr += '<span class="pages"> page %d of total %d pages,%d record(s) </span>'% (currentpage, pagecount,totalcount)
    return pagestr

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
    def render(self, template_file, template_value):
        path = os.path.join(os.path.dirname(__file__), template_file)
        self.response.out.write(template.render(path, template_value))
    def error(self,code):

        if code==400:
            self.response.set_status(code)
            self.render("views/404.html",self.template_value)
        else:
            self.response.set_status(code)
    def is_admin(self):
        return users.is_current_user_admin()
    def write(self,val):
        self.response.out.write(val)
    def initialize(self, request, response):
        webapp.RequestHandler.initialize(self, request, response)
        self.login_user = users.get_current_user()
        self.is_login = (self.login_user != None)
        self.loginurl=users.create_login_url(self.request.uri)
        self.logouturl=users.create_logout_url(self.request.uri)
        self.is_admin = users.is_current_user_admin()
        self.template_value = {'self':self,}
        self.pathinfo = request.environ['PATH_INFO']
        self.req = request
        self.res = response
     
class MainPage(PublicPage):
    def get(self,page):
        
        albums=methods.GetAllAlbums()
        self.template_value["albums"]=albums[:24]
        self.render('views/index.html', self.template_value)

class AlbumPage(PublicPage):
    def get(self,id,page=1):
        
        pagesize = 16
        album = methods.GetAlbum(id)
        if album is None:
            self.error(404)
        else:
            try:
                page = int(page)
            except:
                page = 1
            photos = album.Photos(page,pagesize)
            recordcount =  album.PhotoCount
            pagecount = int(math.ceil(float(recordcount)/pagesize))
            pagecount = max(1,pagecount)
            param = "/album/"+str(id)+"/page/{p}/"
            self.template_value["page"] = pager(totalcount = recordcount,page = page,pagesize = pagesize,param=param)
            self.template_value['photos'] = photos
            self.template_value['album'] = album
            self.template_value['recordcount'] = recordcount

            self.render('views/album.html',self.template_value)
class Gallery(PublicPage):
    def get(self,id):
        album = methods.GetAlbum(id)
        if album is None:
            self.error(404)
        else:
            photos = album.Photos()
            self.template_value['photos'] = photos
            self.template_value['album']  = album
            self.response.headers['Content-Type'] = 'application/xml'
            self.render('views/gallery.html',self.template_value)
class ShowImage(PublicPage):
    def get(self,id):
        import EXIF
        data=methods.GetPhoto(id)
        if not data['photo']:return self.error(404)
        comments = model.Comment().GetCommentByPhoto(id)
        self.template_value["image"] = data
        self.template_value["comments"] = comments
        
        self.render('views/photo.html', self.template_value)
    
    
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

class PostComment(PublicPage):
    def post(self):
        if self.is_login:
            pid = int(self.request.get('pid'))
            comment = model.Comment()
            comment.Author = self.login_user
            comment.CommentDate = datetime.datetime.now()
            comment.CommentBody = self.request.get('comment')
            comment.Photo = model.Photo().Get(pid)
            comment.Save()
        self.redirect('/photo/'+str(pid)+'/')
class DeleteComment(PublicPage):
    def get(self,id):
        if self.is_admin:
            model.Comment().Delete(id)
            self.write('0')
        else:
            self.write('1')
        return
def main():
    webapp.template.register_template_library('filter')
    application = webapp.WSGIApplication(
                                       [('/(?P<page>[0-9]*)/?', MainPage),
                                        (r'/(?P<size>image)/(?P<id>[0-9]+)/?',GetImage),
                                        (r'/(?P<size>m)/(?P<id>[0-9]+)/?',GetImage),
                                        (r'/(?P<size>s)/(?P<id>[0-9]+)/?',GetImage),
                                        (r'/(?P<size>c)/(?P<id>[0-9]+)/?',GetImage),
                                        (r'/photo/(?P<id>[0-9]+)/?',ShowImage),
                                        (r'(?:/album/(?P<id>[0-9]+))?(?:/page/?(?P<page>[0-9]+))?/?',AlbumPage),
                                        #(r'/album/(?P<id>[0-9]+)/?',AlbumPage),
                                        (r'/gallery/(?P<id>[0-9]+)/?',Gallery),
                                        (r'/SwfUpload/?',SwfUpload),
                                        (r'/postcomment/?',PostComment),
                                        (r'/deletecomment/(?P<id>[0-9]+)/?',DeleteComment),
                                        ('.*',Error)
                                       ], debug=True)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
    main()