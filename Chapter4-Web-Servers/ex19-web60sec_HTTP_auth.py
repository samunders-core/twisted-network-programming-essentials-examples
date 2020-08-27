# web-server implementation
from twisted.internet import reactor, endpoints

from twisted.web.server import Site

# auth wrapper and method basic or digest
from twisted.web.guard import HTTPAuthSessionWrapper, BasicCredentialFactory

# web-page
from twisted.web.resource import IResource

# static file for web pages
from twisted.web.static import File

# password storage
from twisted.cred.checkers import FilePasswordDB

# main auth
from twisted.cred.portal import IRealm, Portal

# auth helper implements
from zope.interface import implementer

"""There’s just one last thing that needs to be done here. When rpy scripts were introduced, it was mentioned that they are evaluated in an unusual context. This is the first example that actually needs to take this into account. It so happens that DigestCredentialFactory instances are stateful. Authentication will only succeed if the same instance is used to both generate challenges and examine the responses to those challenges. However, the normal mode of operation for an rpy script is for it to be re-executed for every request. This leads to a new DigestCredentialFactory being created for every request, preventing any authentication attempt from ever succeeding.

There are two ways to deal with this. First, and the better of the two ways, we could move almost all of the code into a real Python module, including the code that instantiates the DigestCredentialFactory . This would ensure that the same instance was used for every request. Second, and the easier of the two ways, we could add a call to cache() to the beginning of the rpy script:
"""
# cache()
"""
cache is part of the globals of any rpy script, so you don’t need to import it (it’s okay to be cringing at this point). Calling cache makes Twisted re-use the result of the first evaluation of the rpy script for subsequent requests too - just what we want in this case."""


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
