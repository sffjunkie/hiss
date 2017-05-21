from hiss.target import Target
from hiss.notifier import TargetList

def test_TargetList_New():
    t = TargetList()
    assert not t.targets

def testTargetList_Append():
    t = TargetList()
    t.append(Target('kodi://192.168.1.1'))
    assert len(t.targets) == 1


def testTargetList_Append():
    t = TargetList()
    kt = Target('kodi://192.168.1.1')
    t.targets.append(kt)
    t.remove(kt)
    assert len(t.targets) == 0
