import time

from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor, endpoints
from twisted.web.static import File


class ClockPage(Resource):
    def __init__(self):
        pass

    isLeaf = True

    def render_GET(self, request):
        return (b"<!DOCTYPE html><html><head><meta charset='utf-8'>"
                b"<title></title></head><body>" + time.ctime().encode('utf-8'))


root = ClockPage()
root.putChild(b"foo", File("/var/www/twisted_web1"))
root.putChild(b"bar", File("/var/www/twisted_web1/doc"))
root.putChild(b"baz", File("/var/www/twisted_web1/log"))

factory = Site(root)
endpoint = endpoints.TCP4ServerEndpoint(reactor, 8880)
endpoint.listen(factory)
reactor.run()
