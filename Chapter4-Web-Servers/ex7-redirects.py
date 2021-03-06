from twisted.web.util import redirectTo
from twisted.internet import reactor
from twisted.web.resource import Resource, NoResource
from twisted.web.server import Site

from calendar import calendar
from datetime import datetime


class YearPage(Resource):
    isLeaf = True  # render any URL with  yeaar/something ex: 2015/something

    def __init__(self, year):
        Resource.__init__(self)
        self.year = year

    def render_GET(self, request):
        # fix bytes
        return ("<html><body><pre>%s</pre></body></html>" % (calendar(self.year),)).encode()


class CalendarHome(Resource):
    def getChild(self, name, request):
        if name == b'':  # fix bytes
            return self
        if name.isdigit():
            return YearPage(int(name))
        else:
            return NoResource()

    # def render_GET(self, request):
    #     return "<html><body>Welcome to the calendar server!</body></html>".encode()  # fix bytes

    def render_GET(self, request):
        return redirectTo(str(datetime.now().year).encode(), request) # fix bytes object


root = CalendarHome()
factory = Site(root)
reactor.listenTCP(8000, factory)
reactor.run()
