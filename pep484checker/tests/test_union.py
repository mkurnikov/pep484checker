# -*- coding: utf-8 -*-
from typing import Union

from pep484checker.tests._base import CheckerTestCase


class TestUnion(CheckerTestCase):
    def test_simple_union(self):
        self.assertCorrectType('22', Union[str, int])
        self.assertCorrectType(22, Union[str, int])

    def test_with_none(self):
        self.assertCorrectType(None, Union[str, int, None])

    def test_covariance(self):
        class Foo():
            pass
        class Bar(Foo):
            pass
        self.assertCorrectType(Bar(), Union[Foo, str])

    def test_doesnt_support_contravariance(self):
        class Foo():
            pass
        class Bar(Foo):
            pass
        self.assertIncorrectType(Foo(), Union[Bar, str])

    def test_with_forward_reference(self):
        class Foo():
            pass

        self.assertCorrectType(Foo(), Union['Foo', str])

