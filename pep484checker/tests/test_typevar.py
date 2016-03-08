# -*- coding: utf-8 -*-
from typing import TypeVar, Union

from pep484checker.tests._base import CheckerTestCase


class Foo():
    pass
class Bar(Foo):
    pass
class Baz(Bar):
    pass

class TestBound(CheckerTestCase):
    def test_bound_invariant(self):
        T = TypeVar('T', bound=Bar)
        self.assertCorrectType(Bar(), T)
        self.assertIncorrectType(Foo(), T)
        self.assertIncorrectType(Baz(), T)

    def test_bound_covariant(self):
        T = TypeVar('T', bound=Bar, covariant=True)
        self.assertCorrectType(Baz(), T)


class TestConstraints(CheckerTestCase):
    def test_two_constraints_correct(self):
        T = TypeVar('T', str, int)
        self.assertCorrectType('22', T)
        self.assertCorrectType(11, T)

    def test_two_constraints_incorrect(self):
        T = TypeVar('T', str, int)
        self.assertIncorrectType(Foo(), T)

    def test_two_constraints_invariant(self):
        T = TypeVar('T', Foo, Bar)
        self.assertCorrectType(Foo(), T)
        self.assertCorrectType(Bar(), T)
        self.assertIncorrectType(Baz(), T)

    def test_two_constraints_covariant(self):
        T = TypeVar('T', Bar, Baz, covariant=True)
        self.assertIncorrectType(Foo(), T)
        self.assertCorrectType(Bar(), T)
        self.assertCorrectType(Baz(), T)

    def test_two_constraints_contravariant(self):
        T = TypeVar('T', Bar, int, contravariant=True)
        self.assertCorrectType(Foo(), T)
        self.assertCorrectType(Bar(), T)

        self.assertIncorrectType(Baz(), T)