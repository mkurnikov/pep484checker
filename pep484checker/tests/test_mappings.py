# -*- coding: utf-8 -*-
from typing import Mapping, Dict, MutableMapping
from collections import defaultdict, OrderedDict, Counter

from pep484checker.tests._base import CheckerTestCase


class TestMapping(CheckerTestCase):
    def test_not_a_dict(self):
        self.assertIncorrectType('str', Mapping)
        self.assertIncorrectType(1, Mapping)
        self.assertIncorrectType(['22'], Mapping)

    def test_no_types_specified_simple_dict(self):
        self.assertCorrectType({'key': 'value'}, Mapping)
        self.assertCorrectType({'key': 'value'}, MutableMapping)
        # self.assertCorrectType({'key': 'value'}, Dict)

    def test_no_types_specified_collections_dicts(self):
        self.assertCorrectType(OrderedDict({'key': 'value'}), Mapping)
        self.assertCorrectType(defaultdict(str, **{'key': 'value'}), Mapping)

    def test_types_specified(self):
        self.assertCorrectType({'key': 'value'}, Mapping[str, str])
        self.assertCorrectType({'key': 'value'}, MutableMapping[str, str])
        # self.assertCorrectType({'key': 'value'}, Dict[str, str])

    def test_incorrect_types_exist(self):
        self.assertIncorrectType({'key': 'value', 'key2': 11}, Mapping[str, str])
        self.assertIncorrectType({'key': 'value', 'key2': 11}, MutableMapping[str, str])
        # self.assertIncorrectType({'key': 'value', 'key2': 11}, Dict[str, str])

    def test_covariant_types_fit_for_mapping(self):
        class Foo():
            pass
        class Bar(Foo):
            pass
        self.assertCorrectType({'key': Foo(), 'key2': Bar()}, Mapping[str, Foo])

    def test_covariant_types_doesnt_fit_for_mutablemapping_and_dict(self):
        class Foo():
            pass
        class Bar(Foo):
            pass
        self.assertIncorrectType({'key': Foo(), 'key2': Bar()}, MutableMapping[str, Foo])
        # self.assertIncorrectType({'key': Foo(), 'key2': Bar()}, Dict[str, Foo])


