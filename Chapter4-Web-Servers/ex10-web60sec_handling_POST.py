from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor, endpoints

import html

class FormPage(Resource):
    def render_GET(self, request):
        return (b"<!DOCTYPE html><html><head><meta charset='utf-8'>"
                b"<title></title></head><body>"
                b"<form method='POST'><input name='the-field'></form>")

    def render_POST(self, request):
        args = request.args[b"the-field"][0].decode("utf-8")
        escapedArgs = html.escape(args)
        return (b"<!DOCTYPE html><html><head><meta charset='utf-8'>"
                b"<title></title></head><body>"
                b"You submitted: " + escapedArgs.encode('utf-8'))

root = Resource()
root.putChild(b"form", FormPage())
factory = Site(root)
endpoint = endpoints.TCP4ServerEndpoint(reactor, 8880)
endpoint.listen(factory)
reactor.run()