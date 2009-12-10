from hiss import *

n = Notification()
n.title = 'Test Notification'
n.text = 'This is a test of the hiss framework.'
n.icon = 'about.png'
n.timeout = 10
n.show()

