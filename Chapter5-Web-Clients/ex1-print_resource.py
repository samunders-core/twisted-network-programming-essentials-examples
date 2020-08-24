from twisted.internet import reactor
from twisted.web.client import Agent
import sys


def printPage(result):
    print(result)


def printError(failure):
    # print >>sys.stderr, failure
    print(failure, file=sys.stderr)


def stop(result):
    reactor.stop()


if len(sys.argv) != 2:
    # print >>sys.stderr, "Usage: python print_resource.py <URL>"
    print("Usage: python print_resource.py <URL>", file=sys.stderr)
    exit(1)

# d = getPage(sys.argv[1].encode()) # deprecated since Twisted 16.7.0, use Agent
# todo: fix the rest!!!
d = Agent()
d.addCallbacks(printPage, printError)
d.addBoth(stop)

reactor.run()
