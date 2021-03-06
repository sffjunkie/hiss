# -*- coding: utf-8 -*-
# Copyright 2013-2014, Simon Kennedy, sffjunkie+code@gmail.com
#
# Part of 'hiss' the asynchronous notification library

import os
import sys
sys.path.insert(0,
                os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from hiss.notification import NotificationPriority

def test_NotificationPriority_VeryLow():
    p = NotificationPriority.very_low
    assert p.value == -2

def test_NotificationPriority_Moderate():
    p = NotificationPriority.moderate
    assert p.value == -1

def test_NotificationPriority_Normal():
    p = NotificationPriority.normal
    assert p.value == 0

def test_NotificationPriority_High():
    p = NotificationPriority.high
    assert p.value == 1

def test_NotificationPriority_Emergency():
    p = NotificationPriority.emergency
    assert p.value == 2
