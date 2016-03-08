# -*- coding: utf-8 -*-
from typing import Tuple

from pep484checker.tests._base import CheckerTestCase


class TestTuple(CheckerTestCase):
    def test_not_a_tuple(self):
        self.assertIncorrectType('22', Tuple[str])

    def test_no_parameters(self):
        self.assertCorrectType((11, 22), Tuple)

    def test_wrong_number_of_elements(self):
        self.assertIncorrectType((11, 22), Tuple[int])

    def test_correct_tuple(self):
        self.assertCorrectType((1, '2', '5'), Tuple[int, str, str])

    def test_incorrect_tuple(self):
        self.assertIncorrectType((1, 2, '5'), Tuple[int, str, str])

    def test_one_arg_plus_ellipsis(self):
        self.assertIncorrectType((1, 2, '5'), Tuple[int, ...])
        self.assertCorrectType((1, 2, 5), Tuple[int, ...])
        self.assertCorrectType(('a', 'b', 'c'), Tuple[str, ...])

