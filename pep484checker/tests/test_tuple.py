# -*- coding: utf-8 -*-
from typing import Tuple

from pep484checker.tests._base import CheckerTestCase


class TestTuple(CheckerTestCase):
    def test_not_a_tuple(self):
        self.assertIncorrectType('22', Tuple[str])

    def test_wrong_number_of_elements(self):
        self.assertIncorrectType((11, 22), Tuple[int])

    def test_using_ellipsis(self):
        self.assertCorrectType((11, 22, 33), Tuple[int, ...])

    def test_correct_tuple(self):
        self.assertCorrectType((1, '2', '5'), Tuple[int, str, str])

    def test_incorrect_tuple(self):
        self.assertIncorrectType((1, 2, '5'), Tuple[int, str, str])


