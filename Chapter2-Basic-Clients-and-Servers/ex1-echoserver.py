# ECHO SERVER

from twisted.internet import protocol
from twisted.internet.reactor import listenTCP, run
import datetime

counter = 0


class Echo(protocol.Protocol):

    # def makeConnection(self):
    #     pass

    def get_time_log(self):
        t = datetime.datetime.now()
        s = t.strftime('%H:%M:%S.%f')
        return s

    def connectionMade(self):
        print('Connection established!!!\n')

    def connectionLost(self, reason='Timeout'):
        print(self.get_time_log(), 'Connection lost!!!\n')

    def dataReceived(self, data):
        global counter
        print(self.get_time_log(),
              'Event: {} registered'.format(self.dataReceived))
        print('Data::{}'.format(data))
        print('Sending it back')
        if self.transport.write(data) is None:
            counter += 1
            print(self.get_time_log(),
                  'SUCCESS! {}\n\n'.format(counter))


class EchoFactory(protocol.Factory):
    def buildProtocol(self, addr):
        return Echo()


listenTCP(8000, EchoFactory())
run()
