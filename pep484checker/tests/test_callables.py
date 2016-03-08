# -*- coding: utf-8 -*-
from typing import Callable

from pep484checker.tests._base import CheckerTestCase


class TestFunctionCheck(CheckerTestCase):
    """Checks for Callable type from typing.py."""
    def test_completely_unannotated(self):
        def callback(s):
            pass
        self.assertCorrectType(callback, Callable)

    def test_not_callable_argument(self):
        arg = 'Argument'
        self.assertIncorrectType(arg, Callable)

    def test_wrong_number_of_arguments(self):
        def callback(s: str, i: int) -> str:
            pass
        self.assertIncorrectType(callback, Callable[[str], str])

    def test_ellipsis_in_place_of_arguments(self):
        def callback(s: str, i: int) -> str:
            pass
        self.assertCorrectType(callback, Callable[..., str])

    def test_one_incorrect_argument(self):
        def callback(s: str, i: int) -> str:
            pass
        self.assertIncorrectType(callback, Callable[[str, str], str])

    def test_all_arguments_correct(self):
        def callback(s: str, i: int) -> str:
            pass
        self.assertCorrectType(callback, Callable[[str, int], str])

    def test_subclasses_are_also_correct(self):
        class Foo():
            pass
        class Bar(Foo):
            pass
        def callback(s: str, i: Bar) -> str:
            pass
        self.assertTrue(issubclass(Bar, Foo))
        self.assertCorrectType(callback, Callable[[str, Foo], str])

    def test_superclasses_are_incorrect(self):
        class Foo():
            pass
        class Bar(Foo):
            pass
        def callback(s: str, i: Foo) -> str:
            pass
        self.assertTrue(not issubclass(Foo, Bar))
        self.assertIncorrectType(callback, Callable[[str, Bar], str])

    def test_correct_return_type(self):
        def callback(s: str, i: int) -> str:
            pass
        self.assertCorrectType(callback, Callable[..., str])

    def test_incorrect_return_type(self):
        def callback(s: str, i: int) -> int:
            pass
        self.assertIncorrectType(callback, Callable[..., str])

    def test_none_in_arguments(self):
        def callback(s: str, i: None) -> str:
            pass
        self.assertCorrectType(callback, Callable[[str, None], str])

    def test_none_in_return_type(self):
        def callback(s: str, i: int) -> None:
            pass
        self.assertCorrectType(callback, Callable[[str, int], None])