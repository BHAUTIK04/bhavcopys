import cherrypy
import os
from redis import StrictRedis
from mako.template import Template
import json


class BhavCopy(object):
    r = StrictRedis.from_url("redis://h:p381ef8e02280716529f06c01a40c2ef52267dd19591f274b6d5112b871e25641@ec2-34-197-61-164.compute-1.amazonaws.com:46289/0")
    @cherrypy.expose
    def index(self):
        return open('html/index.html')
    index.exposed = True

    @cherrypy.expose
    def topten(self):
        data = self.r.zrangebyscore("equity", 1, 10)
        data = [json.loads(i) for i in data]
        return Template(filename='html/top10.html').render(data=data)


@cherrypy.expose
class NameSearch(object):
    r = StrictRedis.from_url("redis://h:p381ef8e02280716529f06c01a40c2ef52267dd19591f274b6d5112b871e25641@ec2-34-197-61-164.compute-1.amazonaws.com:46289/0")
    def GET(self):
        return open("html/search.html")

    def POST(self, scname=""):
        name_lis = self.r.keys()
        print(type(name_lis))
        print(len(name_lis))
        if scname in name_lis:
            print("Here")
            resp = self.r.get(scname)
        else:
            resp = "Enter correct name..."
        print(resp)
        return resp

config = {
    '/': {
        'tools.sessions.on': True,
        'tools.staticdir.root': os.path.abspath(os.getcwd())
    },
    'global': {
        'server.socket_host': '0.0.0.0',
        'server.socket_port': int(os.environ.get('PORT', 5000)),
    },
    '/static': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': os.path.abspath(os.getcwd())+'/public'
    },
    '/search': {
        'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
        'tools.response_headers.on': True,
                #'tools.response_headers.headers': [('Content-Type', 'text/plain')],
    }
}

bhavcopy = BhavCopy()
bhavcopy.search = NameSearch()
cherrypy.quickstart(bhavcopy, "/", config)
