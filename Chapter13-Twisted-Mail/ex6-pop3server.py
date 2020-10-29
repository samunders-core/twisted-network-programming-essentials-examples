import mailbox
import os
from io import BytesIO
import sys
from zope.interface import implementer

from twisted.cred import checkers, portal
from twisted.internet import protocol, reactor
from twisted.mail import pop3, protocols
from twisted.python import log

@implementer(pop3.IMailbox)
class UserInbox(object):
    def __init__(self, userDir):
        inboxDir = os.path.join(userDir, 'Inbox')
        self.mailbox = mailbox.mbox(inboxDir)
        self.markedForDeletion = set()

    def listMessages(self, index=None):
        if index is not None:
            m = self.mailbox.get_message(index)
            return len(str(m))
        return [i not in self.markedForDeletion and len(str(m)) or 0 for i, m in self.mailbox.items()]

    def getUidl(self, index):
        return self.mailbox.get_file(index)._file.name + ":" + index

    def getMessage(self, index):
        return BytesIO(self.mailbox[index].is_multipart() and self.mailbox[index].get_payload() or self.mailbox[index].get_payload().encode("utf-8"))

    def deleteMessage(self, index):
        self.markedForDeletion.add(index)

    def undeleteMessages(self):
        self.markedForDeletion.clear()

    def sync(self):
        files = set()
        for index in self.markedForDeletion:
            self.mailbox.discard(index)
            files.add(self.mailbox.get_file(index)._file)
        self.markedForDeletion.clear()
        for f in files:
            os.unlink(f.name)

class POP3ServerProtocol(pop3.POP3):
    def authenticateUserAPOP(self, user, digest):
        self.magic = self.magic.encode("utf-8")
        return pop3.POP3.authenticateUserAPOP(self, user, digest.decode("utf-8"))

    def lineReceived(self, line):
        print("CLIENT:", line)
        pop3.POP3.lineReceived(self, line)

    def sendLine(self, line):
        print("SERVER:", line)
        pop3.POP3.sendLine(self, line)

class POP3Factory(protocol.Factory):
    def __init__(self, portal):
        self.portal = portal

    def buildProtocol(self, address):
        proto = POP3ServerProtocol()
        proto.portal = self.portal
        return proto

@implementer(portal.IRealm)
class MailUserRealm(object):

    def __init__(self, baseDir):
      self.baseDir = baseDir

    def requestAvatar(self, avatarId, mind, *interfaces):
        if pop3.IMailbox not in interfaces:
            raise NotImplementedError(
                "This realm only supports the pop3.IMailbox interface.")

        userDir = os.path.join(self.baseDir, avatarId.decode("utf-8"))
        avatar = UserInbox(userDir)
        return pop3.IMailbox, avatar, lambda: None

log.startLogging(sys.stdout)

dataDir = len(sys.argv) > 1 and sys.argv[1] or "/tmp/mail"

portal = portal.Portal(MailUserRealm(dataDir))
checker = checkers.FilePasswordDB(os.path.join(dataDir, 'passwords.txt'))
portal.registerChecker(checker)

reactor.listenTCP(1100, POP3Factory(portal))
reactor.run()
