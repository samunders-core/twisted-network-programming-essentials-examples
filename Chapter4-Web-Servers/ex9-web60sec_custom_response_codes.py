from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor, endpoints

class PaymentRequired(Resource):
    def render_GET(self, request):
        request.setResponseCode(402)
        return b"<html><body>Please swipe your credit card.</body></html>"

root = Resource()
root.putChild(b"buy", PaymentRequired())
factory = Site(root)
endpoint = endpoints.TCP4ServerEndpoint(reactor, 8880)
endpoint.listen(factory)
reactor.run()