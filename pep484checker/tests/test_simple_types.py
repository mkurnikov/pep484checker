# -*- coding: utf-8 -*-
from pep484checker.tests._base import CheckerTestCase


class TestBuiltins(CheckerTestCase):
    def test_none(self):
        self.assertCorrectType(None, None)

    def test_primitive_types(self):
        self.assertCorrectType(22, int)
        self.assertCorrectType(22.2, float)
        self.assertCorrectType('foo', str)
        self.assertCorrectType(True, bool)

    def test_userdefined_type(self):
        class Foo():
            pass
        self.assertCorrectType(Foo(), Foo)

    def test_subclass_of_userdefined_type(self):
        class Foo():
            pass
        class Bar(Foo):
            pass
        self.assertTrue(issubclass(Bar, Foo))
        self.assertCorrectType(Bar(), Foo)

    def test_superclass_incorrect(self):
        class Foo():
            pass
        class Bar(Foo):
            pass
        self.assertTrue(issubclass(Bar, Foo))
        self.assertIncorrectType(Foo(), Bar)