from hiss import *

n = Notification()
n.Title = 'Test Notification'
n.Text = 'This is a test of the hiss framework.'
n.Icon = 'about.png'
n.Timeout = 10
n.Show()

