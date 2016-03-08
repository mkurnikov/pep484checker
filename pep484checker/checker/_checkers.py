# -*- coding: utf-8 -*-
import inspect
from typing import _gorg

from abc import ABCMeta, abstractmethod

from pep484checker.checker._helpers import is_consistent_types
from ._result_funcs import good_match, bad_match


class _FunctionRegistry():
    def __init__(self):
        self._registry = dict()

    def __setitem__(self, key, value):
        if not isinstance(key, str) or not isinstance(value, str):
            raise ValueError
        self._registry[key] = value

    def __getitem__(self, item):
        _check_func = self._registry[item] # is it free to raise KeyError and propagate it up
        if isinstance(_check_func, str): # still path to class
            _check_func = eval(_check_func)() # initialize, then instantiate
            self._registry[item] = _check_func

        return _check_func

_check_func_registry = _FunctionRegistry()


class _CheckTypeMeta(ABCMeta):
    def __new__(mcls, name, bases, namespace):
        cls = super().__new__(mcls, name, bases, namespace)
        if len(cls.__abstractmethods__) > 0: # in abstract class
            return cls

        if not hasattr(cls, 'type_') or getattr(cls, 'type_') is None:
            raise ValueError('type_ class variable must be filled.')

        # FIXME: why here not cls but cls.__qualname__
        _check_func_registry[cls.type_.__name__] = cls.__qualname__
        return cls


class _CheckTypeBase(metaclass=_CheckTypeMeta):
    @abstractmethod
    def __call__(self, argument, hint):
        pass


_original_check_type = None
def _check_type_func(argument, hint, covariant=True, contravariant=False):
    global _original_check_type
    if _original_check_type is None:
        from .func import check_type
        _original_check_type = check_type

    return _original_check_type(argument, hint,
                                covariant=covariant, contravariant=contravariant)


# ********************************************************
# Any, Callable, Generic, Optional, TypeVar, Union, Tuple
# ********************************************************
from typing import Any, Callable, Generic, Optional, TypeVar, Union, Tuple
from typing import AnyMeta, CallableMeta, GenericMeta, OptionalMeta, UnionMeta, TupleMeta


class CheckCallableSignatureMixin(object):
    def _check_callable_signature(self, callable_, hint):
        sign = inspect.signature(callable_)
        parameters = list(sign.parameters.items())

        if hint.__args__ != Ellipsis:
            # not Ellipsis => arguments specified, check them
            if len(parameters) != len(hint.__args__):
                return bad_match(callable_, hint, 'Wrong number of arguments of callable.')

            for i, ((_, param), hinted_type) in enumerate(zip(parameters, hint.__args__)):
                if param.annotation == param.empty:
                    # parameter unannotated in callable
                    continue
                else:
                    # check_type()
                    if not is_consistent_types(param.annotation, hinted_type):
                        return bad_match(param.annotation, hinted_type,
                                         'Argument on position {0} has incorrect type {1}. Expected {2}'
                                         .format(i, param.annotation, hinted_type))

        # check return type
        if not sign.return_annotation == sign.empty:
            if not is_consistent_types(sign.return_annotation, hint.__result__):
                return bad_match(sign.return_annotation, hint.__result__,
                                 'Type of return value has incorrect type {0}. Expected {1}'
                                 .format(sign.return_annotation, hint.__result__))

        return good_match()


class CheckIterableMixin(object):
    def _check_iterable(self, iterable_, elem_hint):
        for i, elem in enumerate(iterable_):
            try:
                _check_type_func(elem, elem_hint)
            except TypeError as e:
                return bad_match(elem, elem_hint, 'Element {0} of iterable have type {1}. '
                                                  'Expected {2}'.format(elem, type(elem), elem_hint))
        return good_match()


class CheckAny(_CheckTypeBase): # Done.
    type_ = Any

    def __call__(self, argument, hint: AnyMeta):
        return good_match()


class CheckCallable(_CheckTypeBase, CheckCallableSignatureMixin): # Done.
    type_ = Callable

    def __call__(self, argument, hint: CallableMeta):
        if not callable(argument):
            return bad_match(argument, hint, 'Argument is not callable.')
        if hint == Callable:
            return good_match()

        return self._check_callable_signature(argument, hint)


class CheckGeneric(_CheckTypeBase):
    type_ = Generic

    def __call__(self, argument, hint: GenericMeta):
        pass


class CheckOptional(_CheckTypeBase): # Done.
    type_ = Optional

    def __call__(self, argument, hint: OptionalMeta):
        raise NotImplementedError('Optional[type_name] has to be converted to '
                                  'Union[type_name, NoneType]. This class should never be called.')


class CheckTypeVar(_CheckTypeBase):
    type_ = TypeVar

    def __call__(self, argument, hint: TypeVar):
        if hint.__bound__ is not None:
            consistent = _check_type_func(argument, hint.__bound__,
                                              covariant=hint.__covariant__,
                                              contravariant=hint.__contravariant__)
            if not consistent:
                return bad_match(argument, hint, "Type {0} doesn't satisfy TypeVar's bound {1}"
                                 .format(type(argument), hint))
            else:
                return good_match()

        if len(hint.__constraints__) != 0:
            for c in hint.__constraints__:
                try:
                    _check_type_func(argument, c, covariant=hint.__covariant__,
                                        contravariant=hint.__contravariant__)
                except TypeError as e:
                    pass
                else:
                    return good_match()

            return bad_match(argument, hint, "Doesn't satisfy TypeVar's constraints {0}."
                                 .format(hint.__constraints__))

        return good_match()


class CheckUnion(_CheckTypeBase): # Done.
    type_ = Union

    def __call__(self, argument, hint: UnionMeta):
        for possible_type in hint.__union_set_params__:
            try:
                _check_type_func(argument, possible_type)
            except TypeError:
                pass
            else: # match
                return good_match()

        return bad_match(argument, hint)


class CheckTuple(_CheckTypeBase, CheckIterableMixin): # Done.
    type_ = Tuple

    def __call__(self, argument, hint: TupleMeta):
        if type(argument) != tuple:
            return bad_match(argument, hint)

        if hint.__tuple_params__ is None or len(hint.__tuple_params__) == 0:
            return good_match()

        if not hint.__tuple_use_ellipsis__:
            if len(argument) != len(hint.__tuple_params__):
                return bad_match(argument, hint, 'Wrong number of elements in tuple.')

            for i, (elem, elem_hint) in enumerate(zip(argument, hint.__tuple_params__)):
                try:
                    _check_type_func(elem, elem_hint)
                except TypeError as e:
                    return bad_match(argument, hint, 'At position {0} in tuple: '.format(i) + e.args[0])

            return good_match()

        else:
            return self._check_iterable(argument, hint.__tuple_params__[0])

# ********************************************************
# ABCs (from collections.abc)
# ********************************************************
class CheckABCTypeMixin(object):
    def _is_consistent_with_abc(self, argument, hint):
        abc_class = hint.__extra__
        return isinstance(argument, abc_class)


class CheckMappingMixin(object):
    def _check_mapping(self, mapping_, k_type, v_type):
        for k, v in mapping_.items():
            try:
                _check_type_func(k, k_type)
            except TypeError as e:
                return bad_match(k, k_type, 'Type of key {0} for mapping is incorrect. Expected {1}'
                                 .format(k, k_type))
            else:
                try:
                    _check_type_func(v, v_type)
                except TypeVar as e:
                    return bad_match(v, v_type, 'Type of value {0} for key {1} for mapping '
                                                'is incorrect. Expected {2}'.format(v, k, v_type))
        return good_match()

from typing import Container, Sized, Iterable, Sequence, MutableSequence
from typing import AbstractSet, MutableSet
from typing import Mapping, MutableMapping
from typing import ByteString, Iterator
from typing import AsyncIterable, AsyncIterator, Awaitable


class _CheckABCBase(_CheckTypeBase, CheckABCTypeMixin):
    class DummyType(object):
        pass

    type_ = DummyType

    def __call__(self, argument, hint):
        if not self._is_consistent_with_abc(argument, hint):
            return bad_match(argument, hint)

        return good_match()


class CheckContainer(_CheckABCBase):
    type_ = Container


class CheckSized(_CheckABCBase):
    type_ = Sized


class BoundTypeVarsMixin(object):
    def _is_unannotated(self, hint):
        if not hasattr(self, 'origin_typevars'):
            self.origin_typevars = _gorg(hint).__parameters__

        return hint.__parameters__ == self.origin_typevars

    def _get_bounded_typevars(self, hint):
        if not hasattr(self, 'origin_typevars'):
            self.origin_typevars = _gorg(hint).__parameters__

        for origin_typevar, param in zip(self.origin_typevars, hint.__parameters__):
            origin_typevar.__bound__ = param
        return self.origin_typevars


class CheckIterable(_CheckTypeBase, CheckABCTypeMixin, BoundTypeVarsMixin, CheckIterableMixin):
    type_ = Iterable

    def __call__(self, argument, hint: GenericMeta):
        if not self._is_consistent_with_abc(argument, hint):
            return bad_match(argument, hint)

        if self._is_unannotated(hint):
            # unannotated iterable
            return good_match()

        bounded_typevars = self._get_bounded_typevars(hint)
        return self._check_iterable(argument, bounded_typevars[0])


class CheckSequence(CheckIterable):
    type_ = Sequence


class CheckMutableSequence(CheckIterable):
    type_ = MutableSequence


class CheckAbstractSet(CheckIterable):
    type_ = AbstractSet


class CheckMutableSet(CheckIterable):
    type_ = MutableSet


class CheckMapping(_CheckTypeBase, CheckABCTypeMixin, BoundTypeVarsMixin, CheckMappingMixin):
    type_ = Mapping

    def __call__(self, argument, hint: GenericMeta):
        if not self._is_consistent_with_abc(argument, hint):
            return bad_match(argument, hint)

        if self._is_unannotated(hint):
            # unannotated iterable
            return good_match()

        bounded_typevars = self._get_bounded_typevars(hint)
        return self._check_mapping(argument, bounded_typevars[0], bounded_typevars[1])


class CheckMutableMapping(CheckMapping):
    type_ = MutableMapping


class CheckByteString(_CheckABCBase):
    type_ = ByteString


class CheckIterator(_CheckABCBase):
    type_ = Iterator


class CheckAwaitable(_CheckABCBase):
    type_ = Awaitable


class CheckAsyncIterable(_CheckABCBase):
    type_ = AsyncIterable


class CheckAsyncIterator(_CheckABCBase):
    type_ = AsyncIterator


# ********************************************************
# Python data structures (Dict, List, Set, FrozenSet, Generator)
# ********************************************************

from typing import Dict, Set, List, FrozenSet, Generator


