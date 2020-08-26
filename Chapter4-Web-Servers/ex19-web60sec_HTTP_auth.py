from twisted.internet import reactor, endpoints
from twisted.web.server import Site
from twisted.web.guard import HTTPAuthSessionWrapper, BasicCredentialFactory
from twisted.web.resource import IResource
from twisted.web.static import File
from twisted.cred.checkers import FilePasswordDB
from twisted.cred.portal import IRealm, Portal
from zope.interface import implementer

# ???
# cache()


@implementer(IRealm)
class PublicHTMLRealm(object):
    def requestAvatar(self, avatarId, mind, *interfaces):
        if IResource in interfaces:
            print("/var/www/{}/public_html".format(avatarId.decode()))
            return (IResource, File("/var/www/{}/public_html".format(avatarId.decode())), lambda: None)
        print('Unauthorized')
        raise NotImplementedError()


portal = Portal(PublicHTMLRealm(), [FilePasswordDB('./httpd.password')])

# print([FilePasswordDB('./httpd.password')])

credentialFactory = BasicCredentialFactory("localhost:8080")
# print(credentialFactory.__repr__())

resource = HTTPAuthSessionWrapper(portal, [credentialFactory])
# print(resource.__repr__())

# remove below if use rpy script for twistd
factory = Site(resource)
endpoint = endpoints.TCP4ServerEndpoint(reactor, 8080)
endpoint.listen(factory)
reactor.run()
