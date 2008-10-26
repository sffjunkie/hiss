import time

from hiss import *

a = Application('Hiss', ['started', 'stoppped'])
a.Icon = 'about.png'
a.register()
time.sleep(10)
a.deregister()

