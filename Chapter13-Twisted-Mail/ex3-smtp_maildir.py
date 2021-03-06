import mailbox
import os
import sys

from email.header import Header
from zope.interface import implementer

from twisted.internet import defer, reactor
from twisted.mail import smtp
from twisted.python import log

@implementer(smtp.IMessageDelivery)
class LocalMessageDelivery(object):

    def __init__(self, protocol, baseDir):
        self.protocol = protocol
        self.baseDir = baseDir

    def receivedHeader(self, helo, origin, recipients):
        clientHostname, clientIP = helo
        myHostname = self.protocol.transport.getHost().host
        headerValue = "from %s by %s with ESMTP ; %s" % (
            clientHostname, myHostname, smtp.rfc822date())
        return ("Received: %s" % Header(headerValue)).encode("utf-8")

    def validateFrom(self, helo, origin):
        # Accept any sender.
        return origin

    def _getAddressDir(self, address):
        return os.path.join(self.baseDir, "%s" % address)

    def validateTo(self, user):
        # Accept recipients @localhost.
        if user.dest.domain.decode("utf-8") == "localhost":
            return lambda: MaildirMessage(
                self._getAddressDir(str(user.dest)))
        else:
            log.msg("Received email for invalid recipient %s" % user)
            raise smtp.SMTPBadRcpt(user)

@implementer(smtp.IMessage)
class MaildirMessage(object):

    def __init__(self, userDir):
        if not os.path.exists(userDir):
            os.makedirs(userDir, exist_ok=True)
        inboxDir = os.path.join(userDir, 'Inbox')
        self.mailbox = mailbox.mbox(inboxDir)
        self.lines = []

    def lineReceived(self, lineBytes):
        # first call with result of receivedHeader(...) above
        self.lines.append(lineBytes.decode("utf-8"))

    def eomReceived(self):
        print("New message received.")
        self.lines.append('') # Add a trailing newline.
        messageData = '\n'.join(self.lines)
        self.mailbox.add(messageData)
        return defer.succeed(None)

    def connectionLost(self):
        print("Connection lost unexpectedly!")
        # Unexpected loss of connection; don't save.
        del(self.lines)

class LocalSMTPFactory(smtp.SMTPFactory):
    def __init__(self, baseDir):
        self.baseDir = baseDir

    def buildProtocol(self, addr):
        proto = smtp.ESMTP()
        proto.delivery = LocalMessageDelivery(proto, self.baseDir)
        return proto

log.startLogging(sys.stdout)

reactor.listenTCP(2500, LocalSMTPFactory(len(sys.argv) > 1 and sys.argv[1] or "/tmp/mail"))
reactor.run()
