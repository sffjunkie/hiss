import time

from hiss import *

a = Application('Hiss', ['started', 'stoppped'])
a.icon = 'about.png'
a.register()
time.sleep(5)
a.deregister()

