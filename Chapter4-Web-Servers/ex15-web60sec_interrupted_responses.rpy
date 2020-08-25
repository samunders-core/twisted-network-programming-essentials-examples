from twisted.web.resource import Resource
from twisted.web.server import NOT_DONE_YET
from twisted.internet import reactor


class DelayedResource(Resource):
    def _delayedRender(self, request):
        request.write(b"<html><body>Sorry to keep you waiting.</body></html>")
        request.finish()

    def _responseFailed(self, err, call):
        call.cancel()

    def render_GET(self, request):
        call = reactor.callLater(5, self._delayedRender, request)
        request.notifyFinish().addErrback(self._responseFailed, call)
        return NOT_DONE_YET


resource = DelayedResource()

"""Toss this into example.rpy , fire it up with twistd -n web --path . , 
and hit http://localhost:8080/example.rpy . If you wait five seconds, 
you’ll get the page content. If you interrupt the request before then, 
say by hitting escape (in Firefox, at least), then you’ll see perhaps 
the most boring demonstration ever - no page content, and nothing in 
the server logs. Success!"""
