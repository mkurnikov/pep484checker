# -*- coding: utf-8 -*-
class IsValidType(object):
    def __init__(self, val: bool, errors=None):
        self.val = val
        if errors:
            self.errors = errors

    def __bool__(self):
        return self.val
    # TODO: add tuple unpacking


def good_match():
    return True


def bad_match(argument, hint, message=None):
    if message is None:
        message = 'Argument type {0} is not consistent with hint {1}'.format(type(argument), hint)

    raise TypeError(message)
