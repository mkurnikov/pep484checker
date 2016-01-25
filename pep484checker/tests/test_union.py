# -*- coding: utf-8 -*-
from typing import Union

from pep484checker.tests._base import CheckerTestCase


class TestUnion(CheckerTestCase):
    def test_simple_union(self):
        self.assertCorrectType('22', Union[str, int])
        self.assertCorrectType(22, Union[str, int])

    def test_with_none(self):
        self.assertCorrectType(None, Union[str, int, None])
