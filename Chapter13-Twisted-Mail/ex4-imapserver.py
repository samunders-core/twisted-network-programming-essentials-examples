import email
import mailbox
import os
import random
from io import BytesIO
import sys
from zope.interface import implementer

from twisted.cred import checkers, portal
from twisted.internet import protocol, reactor
from twisted.mail import imap4, interfaces
from twisted.python import log

@implementer(imap4.IAccount)
class IMAPUserAccount(object):

    def __init__(self, userDir):
        self.dir = userDir

    def _getMailbox(self, path):
        if path.lower() == "inbox":
            path = "Inbox"  # to match ex3-smtp_maildir.py
        fullPath = os.path.join(self.dir, path)
        if not os.path.exists(fullPath):
            raise KeyError("No such mailbox")
        return IMAPMailbox(fullPath)

    def listMailboxes(self, ref, wildcard):
        for box in os.listdir(self.dir):
            yield box, self._getMailbox(box)

    def select(self, path, rw=False):
        return self._getMailbox(path)

@implementer(imap4.IMailbox)
@implementer(interfaces.ICloseableMailboxIMAP)
class IMAPMailbox(object):

    def __init__(self, path):
        self.maildir = mailbox.mbox(path)
        self.listeners = []
        self.uniqueValidityIdentifier = random.randint(1000000, 9999999)

    def getHierarchicalDelimiter(self):
        return "."

    def getFlags(self):
        return []

    def getMessageCount(self):
        return len(self.maildir)

    def getRecentCount(self):
        return 0

    def isWriteable(self):
        return True

    def expunge(self, messageSet=imap4.MessageSet()):
        files = set()
        self.maildir.lock()
        if not messageSet.last:
            for k in self.maildir.keys():
                messageSet.add(k)
                files.add(self.maildir.get_file(k)._file)
            self.maildir.clear()
        try:
            return [messageNum for messageNum in messageSet if not self.maildir.discard(messageNum)]
        finally:
            self.maildir.unlock()
            for f in files:
                os.unlink(f.name)

    def getUIDValidity(self):
        return self.uniqueValidityIdentifier

    def _seqMessageSetToSeqDict(self, messageSet):
        if not messageSet.last:
            messageSet.last = self.getMessageCount()

        seqMap = {}
        for messageNum in messageSet:
            if messageNum >= 0 and messageNum <= self.getMessageCount():
                seqMap[messageNum] = self.maildir[messageNum - 1]
        return seqMap

    def fetch(self, messages, uid):
        if uid:
            raise NotImplementedError("This server only supports lookup by sequence number")

        messagesToFetch = self._seqMessageSetToSeqDict(messages)
        for seq, msg in messagesToFetch.items():
            yield seq, MaildirMessage(msg)

    def close():
        self.maildir.close()

    def addListener(self, listener):
        self.listeners.append(listener)

    def removeListener(self, listener):
        self.listeners.remove(listener)

@implementer(imap4.IMessage)
class MaildirMessage(object):

    def __init__(self, messageData):
        self.message = messageData

    def getFlags(self):
        return self.message.get_flags()

    def getHeaders(self, negate, *names):
        if not names:
            names = self.message.keys()

        headers = {}
        if negate:
            for header in self.message.keys():
                if header.upper() not in names:
                    headers[header.lower()] = self.message.get(header, '')
        else:
            for name in names:
                headers[name.lower()] = self.message.get(name, '')

        return headers

    def getBodyFile(self):
        return BytesIO(self.message.is_multipart() and self.message.get_payload() or self.message.get_payload().encode("utf-8"))

    def isMultipart(self):
        return self.message.is_multipart()

@implementer(portal.IRealm)
class MailUserRealm(object):

    def __init__(self, baseDir):
      self.baseDir = baseDir

    def requestAvatar(self, avatarId, mind, *interfaces):
        if imap4.IAccount not in interfaces:
            raise NotImplementedError(
                "This realm only supports the imap4.IAccount interface.")

        userDir = os.path.join(self.baseDir, avatarId.decode("utf-8"))
        avatar = IMAPUserAccount(userDir)
        return imap4.IAccount, avatar, lambda: None

class IMAPServerProtocol(imap4.IMAP4Server):
  def lineReceived(self, line):
      print("CLIENT:", line)
      imap4.IMAP4Server.lineReceived(self, line)

  def sendLine(self, line):
      imap4.IMAP4Server.sendLine(self, line)
      print("SERVER:", line)

class IMAPFactory(protocol.Factory):
    def __init__(self, portal):
        self.portal = portal

    def buildProtocol(self, addr):
        proto = IMAPServerProtocol()
        proto.portal = portal
        return proto

log.startLogging(sys.stdout)

dataDir = len(sys.argv) > 1 and sys.argv[1] or "/tmp/mail"

portal = portal.Portal(MailUserRealm(dataDir))
checker = checkers.FilePasswordDB(os.path.join(dataDir, 'passwords.txt'))
portal.registerChecker(checker)

reactor.listenTCP(1430, IMAPFactory(portal))
reactor.run()
