# -*- coding: utf-8 -*-
from typing import (Set, AbstractSet, FrozenSet, MutableSet,
                    List, Sequence, MutableSequence, Iterable,
                    MappingView, ItemsView, ValuesView, KeysView,
                    Container, Sized)

from pep484checker.tests._base import CheckerTestCase


class TestContainer(CheckerTestCase):
    def test_non_containers(self):
        class Foo():
            pass
        self.assertIncorrectType(1, Container)
        self.assertIncorrectType(1.0, Container)
        self.assertIncorrectType(Foo(), Container)

    def test_containers(self):
        self.assertCorrectType('sss', Container)
        self.assertCorrectType([1, 2], Container)
        self.assertCorrectType({'11': '22'}, Container)


class TestSized(CheckerTestCase):
    def test_non_sized(self):
        class Foo():
            pass
        self.assertIncorrectType(11, Sized)
        self.assertIncorrectType(11.0, Sized)
        self.assertIncorrectType(Foo, Sized)
        self.assertIncorrectType(Foo(), Sized)

    def test_sized(self):
        class Foo():
            def __len__(self):
                pass
        self.assertCorrectType([11, 22], Sized)
        self.assertCorrectType('1122', Sized)
        self.assertCorrectType({'11': 22}, Sized)
        self.assertCorrectType(Foo(), Sized)


class TestSimpleIterable(CheckerTestCase):
    def test_non_iterable(self):
        class Foo():
            pass
        self.assertIncorrectType(11, Iterable)
        self.assertIncorrectType(11.22, Iterable)
        self.assertIncorrectType(Foo, Iterable)
        self.assertIncorrectType(Foo(), Iterable)

    def test_unannotated_iterable(self):
        self.assertCorrectType([], Iterable)
        self.assertCorrectType([11, 22], Iterable)
        self.assertCorrectType(['11', '22'], Iterable)

    def test_annotated_incorrectly(self):
        self.assertIncorrectType([11, 22], Iterable[str])

    def test_annotated(self):
        self.assertCorrectType([11, 22], Iterable[int])


class TestSequences(CheckerTestCase):
    def test_non_sequences(self):
        class Foo():
            pass
        self.assertCorrectType('ss', Sequence)
        self.assertIncorrectType(11, Sequence)
        self.assertIncorrectType(Foo(), Sequence)
        self.assertIncorrectType(Foo(), Sequence)
        self.assertIncorrectType(Foo(), MutableSequence)

    def test_sequences_without_type(self):
        self.assertCorrectType([1, 1], MutableSequence)
        self.assertCorrectType([1, 1], Sequence)

    def test_typed_sequences(self):
        self.assertCorrectType([1, 1], MutableSequence[int])
        self.assertCorrectType([1, 1], Sequence[int])

    def test_wrongly_typed(self):
        self.assertIncorrectType([1, 1], MutableSequence[str])
        self.assertIncorrectType([1, 1], Sequence[str])

    def test_covariant(self):
        class Foo():
            pass
        class Bar(Foo):
            pass
        self.assertIncorrectType([Foo(), Bar()], MutableSequence[Foo])
        self.assertCorrectType([Foo(), Bar()], Sequence[Foo])

class TestSets(CheckerTestCase):
    def test_not_sets(self):
        self.assertIncorrectType('ss', AbstractSet)
        self.assertIncorrectType(11, AbstractSet)
        self.assertIncorrectType([], AbstractSet)
        self.assertIncorrectType({}, AbstractSet)

    def test_sets(self):
        self.assertCorrectType(set((1, 2)), AbstractSet)
        # self.assertCorrectType(set((1, 2)), Set)
        self.assertCorrectType(set((1, 2)), MutableSet)
        # self.assertCorrectType(frozenset((1, 2)), FrozenSet)

    def test_sets_specified_type(self):
        self.assertCorrectType(set((1, 2)), AbstractSet[int])
        # self.assertCorrectType(set((1, 2)), Set[int])
        self.assertCorrectType(set((1, 2)), MutableSet[int])
        # self.assertCorrectType(frozenset((1, 2)), FrozenSet[int])

    # def test_no_distinction_between_types(self): # FIXME
    #     # self.assertCorrectType(set((1, 2)), FrozenSet[int])
    #     self.assertCorrectType(frozenset((1, 2)), MutableSet[int])

    def test_covariant(self):
        class Foo():
            pass
        class Bar(Foo):
            pass
        # self.assertCorrectType({Foo(), Bar()}, Set[Foo])
        self.assertCorrectType({Foo(), Bar()}, AbstractSet[Foo])
        self.assertIncorrectType({Foo(), Bar()}, MutableSet[Foo])
        # self.assertCorrectType({Foo(), Bar()}, FrozenSet[Foo])


class TestViews(CheckerTestCase): # FIXME
    pass