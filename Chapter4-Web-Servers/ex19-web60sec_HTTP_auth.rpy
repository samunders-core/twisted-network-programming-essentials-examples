# from twisted.internet import reactor
# from twisted.web.server import Site
from twisted.web.guard import HTTPAuthSessionWrapper, DigestCredentialFactory
from twisted.web.resource import IResource
from twisted.web.static import File
from twisted.cred.checkers import FilePasswordDB
from twisted.cred.portal import IRealm, Portal
from zope.interface import implementer

# cache()


@implementer(IRealm)
class PublicHTMLRealm(object):
    def requestAvatar(self, avatarId, mind, *interfaces):
        if IResource in interfaces:
            return (IResource, File("/var/www/%s/public_html" % (avatarId,)), lambda: None)
        raise NotImplementedError()

# todo: add auth!!!


portal = Portal(PublicHTMLRealm(), [FilePasswordDB('httpd.password')])

credentialFactory = DigestCredentialFactory("md5", "localhost:8080")

resource = HTTPAuthSessionWrapper(portal, [credentialFactory])
############################


# root = File('/var/www/twisted_web1')
# root.putChild(b'doc', File("/var/www/twisted_web1/doc"))
# root.putChild(b'logs', File("/var/www/twisted_web1/log"))
# factory = Site(root)

# reactor.listenTCP(8080, factory)
# reactor.run()
