# -*- coding: utf-8 -*-

import unittest
from pep484checker.checker._helpers import is_consistent_types


class Foo():
    pass
class Bar(Foo):
    pass
class Baz(Bar):
    pass

class TestConsistentHelper(unittest.TestCase):
    def test_invariant_correct(self):
        self.assertTrue(is_consistent_types(Foo, Foo))

    def test_invariant_incorrect(self):
        self.assertFalse(is_consistent_types(Foo, Bar, covariant=False, contravariant=False))
        self.assertFalse(is_consistent_types(Bar, Foo, covariant=False, contravariant=False))

    def test_covariant_correct(self):
        self.assertTrue(is_consistent_types(Bar, Foo, covariant=True))

    def test_contravariant_correct(self):
        self.assertTrue(is_consistent_types(Foo, Bar, contravariant=True))