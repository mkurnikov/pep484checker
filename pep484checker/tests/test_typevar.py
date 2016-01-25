# -*- coding: utf-8 -*-
from typing import TypeVar

from pep484checker.tests._base import CheckerTestCase


class TestTypeVar(CheckerTestCase):
    def test_bound(self):
        class Foo():
            pass
        class Bar(Foo):
            pass
        class Baz(Bar):
            pass
        T = TypeVar('T', bound=Bar)
        self.assertCorrectType(Bar(), T)
        self.assertCorrectType(Baz(), T)
        self.assertIncorrectType(Foo(), T)

    def test_two_possible_types(self):
        T = TypeVar('T', int, float)
        self.assertCorrectType(22, T)
        self.assertIncorrectType('11', T)