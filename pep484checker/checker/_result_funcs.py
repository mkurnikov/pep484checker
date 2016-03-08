# -*- coding: utf-8 -*-
def good_match():
    return True


def bad_match(argument, hint, message=None):
    if message is None:
        message = 'Argument type {0} is not consistent with hint {1}'.format(type(argument), hint)

    raise TypeError(message)
