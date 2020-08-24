from twisted.internet import reactor
from twisted.web.resource import Resource
from twisted.web.server import Site

import time


class BusyPage(Resource):
    isLeaf = True

    def render_GET(self, request):
        print('start time: {}'.format(time.asctime()))
        time.sleep(5)
        return ("Finally done, at %s" % (time.asctime(),)).encode()


factory = Site(BusyPage())
reactor.listenTCP(8000, factory)
reactor.run()
