from twisted.internet import reactor
from twisted.internet.defer import Deferred, inlineCallbacks

def go():
	def callback(r):
		print('callback')

	d = Deferred()
	#d.addCallback(callback)
	reactor.callLater(5, d.callback, True)
	return d

@inlineCallbacks
def r():
	_d1 = yield go()
	print('yield 1')
	_d2 = yield go()
	print('yield 2')

print('running')
reactor.callWhenRunning(r)
reactor.callLater(15, reactor.stop)
reactor.run()
print('done')

