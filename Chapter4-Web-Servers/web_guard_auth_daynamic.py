# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
This example shows how to make simple web authentication.

To run the example:
    $ python webguard.py

When you visit http://127.0.0.1:8889/, the page will ask for an username &
password. See the code in main() to get the correct username & password!
"""

import sys

from zope.interface import implementer

from twisted.python import log
from twisted.internet import reactor
from twisted.web import server, resource, guard
from twisted.web.static import File  # static resource
from twisted.cred.portal import IRealm, Portal
from twisted.cred.checkers import InMemoryUsernamePasswordDatabaseDontUse
from calendar import calendar


# web root class
class Calendar(resource.Resource):
    """
    A resource which is protected by guard and requires authentication in order
    to access.
    """

    def __init__(self, year):
        resource.Resource.__init__(self)
        self.year = year

    def render_GET(self, request):
        return "<html><body><pre>%s</pre></body></html>" % (calendar(self.year),)


class GuardedResource(resource.Resource):
    def getChild(self, name, request):
        if not name:
            name = '2020'

        return Calendar(int(name))


web_root = GuardedResource()

# GuardedResource.putChild('',File())


@implementer(IRealm)
class SimpleRealm(object):
    """
    A realm which gives out L{GuardedResource} instances for authenticated
    users.
    """

    def requestAvatar(self, avatarId, mind, *interfaces):
        root = resource.IResource
        if root in interfaces:
            return resource.IResource, web_root, lambda: None
        raise NotImplementedError()


def main():
    # log
    log.startLogging(sys.stdout)

    checkers = [InMemoryUsernamePasswordDatabaseDontUse(joe='blow')]

    portal = Portal(SimpleRealm(), checkers)

    credFactory = [guard.DigestCredentialFactory('md5', 'example.com')]

    wrapper = guard.HTTPAuthSessionWrapper(portal, credFactory)

    # guard.HTTPAuthSessionWrapper(
    #     Portal(SimpleRealm(), checkers),
    #     [guard.DigestCredentialFactory('md5', 'example.com')])

    factory = server.Site(resource=wrapper)

    reactor.listenTCP(8889, factory)

    reactor.run()


if __name__ == '__main__':
    main()
