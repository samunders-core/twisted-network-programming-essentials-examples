from twisted.internet import reactor, protocol


class QuoteProtocol(protocol.Protocol):

    # def __init__(self, factory):
    #     self.factory = factory
    # replaced by factory class variable in the QuoteFactory class header

    def connectionMade(self):
        self.factory.numConnections += 1

    def dataReceived(self, data):
        print("Number of active connections: %d" % (self.factory.numConnections,))
        print("> Received: ``%s''\n>  Sending: ``%s''" % (data, self.getQuote()))

        tmp_quote = self.getQuote()  # <class 'str'>
        if type(tmp_quote) is str:
            tmp_quote = tmp_quote.encode()  # utf-8 to bytes
        else:  # bytes
            pass

        # print (tmp_quote) # builtins.TypeError: Data must not be unicode
        # print (type(tmp_quote))

        # error here builtins.TypeError: Data must not be unicode
        self.transport.write(tmp_quote)
        self.updateQuote(data)

    def connectionLost(self, reason):
        self.factory.numConnections -= 1

    def getQuote(self):
        return self.factory.quote

    def updateQuote(self, quote):
        self.factory.quote = quote


class QuoteFactory(protocol.Factory):
    numConnections = 0
    protocol = QuoteProtocol

    def __init__(self, quote=None):
        self.quote = quote or "An apple a day keeps the doctor away"

    # def buildProtocol(self, addr):
    #     return QuoteProtocol(self)
    # replaced by this protocol class varibale in the class header


reactor.listenTCP(8000, QuoteFactory())
reactor.run()
