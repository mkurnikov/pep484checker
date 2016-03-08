# -*- coding: utf-8 -*-
import unittest
import inspect

from pep484checker.checker.func import check_type


class CheckerTestCase(unittest.TestCase):
    def assertCorrectType(self, argument, hint, error_msg=None):
        try:
            is_consistent = check_type(argument, hint)
            if is_consistent is None:
                raise TypeError('None is returned.')
        except TypeError as e:
            self.fail(e.args[0])
        #
        # if error_msg is None:
        #     if callable(argument):
        #         argument_type = str(type(argument)) + ' with signature: ' + str(inspect.signature(argument))
        #     else:
        #         argument_type = str(type(argument))
        #
        #     error_msg = 'Types aren\'t equal. \nArgument type: {0}\nGiven hint: {1}'.format(argument_type, hint)
        #
        # self.assertTrue(is_correct, error_msg)

    def assertIncorrectType(self, argument, hint, error_msg=None):
        with self.assertRaises(TypeError):
            check_type(argument, hint)
        # is_correct, _ = check_type(argument, hint)
        # if error_msg is None:
        #     error_msg = '\n Types are equal. Type: {0}'.format(hint)
        #
        # self.assertTrue(not is_correct, error_msg)
