from twisted.internet.defer import Deferred


def addBold(result):
    return "<b>{}</b>".format(result,)


def addItalic(result):
    return "<i>{}</i>".format(result,)


def printHTML(result):
    print(result)


d = Deferred()
d.addCallback(addBold)
d.addCallback(addItalic)
d.addCallback(printHTML)
d.callback("Hello World")
