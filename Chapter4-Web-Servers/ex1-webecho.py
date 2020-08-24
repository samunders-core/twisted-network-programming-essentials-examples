from twisted.protocols import basic
from twisted.internet import protocol, reactor

class HTTPEchoProtocol(basic.LineReceiver):
    def __init__(self):
        self.lines = []

    def lineReceived(self, line):
        self.lines.append(line.decode()) # decode from bytes to utf-8 string
        if not line:
            self.sendResponse()

    def sendResponse(self):
        self.sendLine(b'HTTP/1.1 200 OK')
        self.sendLine(b'')
        responseBody = ("You said:\r\n\r\n" + "\r\n".join(self.lines)).encode()
        self.transport.write(responseBody)
        self.transport.loseConnection()

class HTTPEchoFactory(protocol.ServerFactory):
    def buildProtocol(self, addr):
        return HTTPEchoProtocol()

reactor.listenTCP(8000, HTTPEchoFactory())
reactor.run()
