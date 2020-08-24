from twisted.internet import reactor
# from twisted.web.client import downloadPage
from twisted.web.client import Agent
import sys


def printError(failure):
    print >>sys.stderr, failure


def stop(result):
    reactor.stop()


if len(sys.argv) != 3:
    # print >>sys.stderr, "Usage: python download_resource.py <URL> <output file>"
    print("Usage: python download_resource.py <URL> <output file>", file=sys.stderr)
    exit(1)

# d = downloadPage(sys.argv[1].encode(), sys.argv[2].encode()) # deprecated method
# DeprecationWarning: twisted.web.client.downloadPage was deprecated in Twisted 16.7.0;
# please use https://pypi.org/project/treq/ or twisted.web.client.Agent instead
d.addErrback(printError)
d.addBoth(stop)

reactor.run()
