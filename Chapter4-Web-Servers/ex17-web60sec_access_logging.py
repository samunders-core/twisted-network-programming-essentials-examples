from twisted.web.http import proxiedLogFormatter
from twisted.web.server import Site
from twisted.web.static import File
from twisted.internet import reactor, endpoints

resource = File('/tmp')
factory = Site(resource, logPath=b"/tmp/access-logging-demo.log", logFormatter=proxiedLogFormatter)
endpoint = endpoints.TCP4ServerEndpoint(reactor, 8888)
endpoint.listen(factory)
reactor.run()