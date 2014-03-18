# Copyright 2013-2014, Simon Kennedy, code@sffjunkie.co.uk
#
# Part of 'hiss' the asynchronous notification library

__all__ = ['HissError', 'ValidationError', 'NotifierError', 'TargetError']

class HissError(Exception):
    pass


class marshalError(HissError):
    """An error which occurred when marshaling/unmarshaling of messages"""


class ValidationError(HissError):
    """An error which occurred when validating hashing/encryption"""


class NotifierError(HissError):
    """An error whilst calling notifier methods."""


class TargetError(HissError):
    """An error whilst processing a target specification."""

