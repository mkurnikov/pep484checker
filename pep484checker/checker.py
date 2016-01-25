# -*- coding: utf-8 -*-
from typing import (AnyMeta, CallableMeta, UnionMeta,
                    OptionalMeta, TupleMeta, TypingMeta)
from typing import (Any, Tuple, Optional, Callable, Union, TypeVar, Mapping,
                    Container, _ProtocolMeta, MutableMapping, Dict)
from typing import T, KT, VT_co, VT
import inspect

from collections import Mapping as ABCMapping


def check_type(argument: Any, hint: Union[type, None]) -> Tuple[bool, Optional[str]]:
    if hint is None:
        hint = type(None)

    if not isinstance(hint, type): # user error
        raise ValueError("Provided hint has to be instance of 'type'. Given {}".format(hint))

    if isinstance(hint, CallableMeta):
        return check_callable(argument, hint)

    if isinstance(hint, TupleMeta):
        return check_tuple(argument, hint)

    if issubclass(hint, Mapping): # Mapping, MutableMapping, Dict
        return check_mapping(argument, hint)

    # if issubclass(hint, Container): # AbstractSet, MutableSet, Set, FrozenSet. Sequence, MutableSequence, List.
    #                                 # KeysView
    #     return check_container(argument, hint) # FIXME: ItemsView inherits from Set
    #
    # if isinstance(hint, _ProtocolMeta): # SupportsInt/Float/Round...
    #     return check_protocol(argument, hint)

    if hint == type(None) \
        or hint.__class__ in [AnyMeta, UnionMeta, OptionalMeta, TypeVar] \
            or not isinstance(hint, TypingMeta):
        # catches Any, None, Union, Optional, TypeVar, all classes and built-ins
        if not issubclass(type(argument), hint):
            return False, 'Incorrect type {0}. Expected {1}'.format(type(argument), hint)
        else:
            return True, None


def check_tuple(argument: Any, hint: TupleMeta) -> Tuple[bool, Optional[str]]:
    if type(argument) != tuple:
        return False, 'Argument is not a tuple.'

    # Tuple[int, ...]
    if hint.__tuple_use_ellipsis__:
        return check_type(argument[0], hint.__tuple_params__[0])

    if len(argument) != len(hint.__tuple_params__):
        return False, 'Wrong number of elements in tuple.'

    for i, (elem, elem_hint) in enumerate(zip(argument, hint.__tuple_params__)):
        is_correct, errors = check_type(elem, elem_hint)
        if not is_correct:
            return False, 'For {0} element of tuple: {1}'.format(i, errors)

    return True, None


def check_callable(argument: Any, hint: CallableMeta) -> Tuple[bool, Optional[str]]:
    # TODO: add documentation
    # TODO: add doctest
    if not callable(argument): # TODO: check if correct "is callable"
        return False, 'Argument is not callable.'

    # unspecified args list and return value (just Callable) and argument is callable.
    if hint == Callable:
        return True, None

    sign = inspect.signature(argument)
    parameters = list(sign.parameters.items())

    # if inspect.ismethod(argument): #bounded # TODO: find out what is the right way to write annotation
    #                                          (with or without self type)
    #     parameters.insert(0, ('self', Parameter('self', Parameter.POSITIONAL_ONLY,
    #                                             annotation=type(argument.__self__))))

    if hint.__args__ != Ellipsis:
        # not Ellipsis => arguments specified, check them
        if len(parameters) != len(hint.__args__):
            return False, 'Wrong number of arguments of callable.'

        for i, ((_, param), hinted_type) in enumerate(zip(parameters, hint.__args__)):
            if param.annotation == param.empty:
                # parameter unannotated in argument
                continue
            else:
                if not _is_subclass(param.annotation, hinted_type):
                    return False, 'Argument on position {0} has incorrect type {1}. Expected {2}'\
                        .format(i, param.annotation, hinted_type) # TODO: should I start from 0 or from 1?

    # check return type
    if not sign.return_annotation == sign.empty:
        if not _is_subclass(sign.return_annotation, hint.__result__):
            return False, 'Type of return value has incorrect type {0}. Expected {1}'\
                .format(sign.return_annotation, hint.__result__)

    return True, None


def _is_subclass(arg_type: Union[type, None], hinted_type: Union[type, None]) -> bool:
    if hinted_type is None:
        hinted_type = type(None)
    if arg_type is None:
        arg_type = type(None)

    return issubclass(arg_type, hinted_type)

# from typing import Generic

def check_mapping(argument: ABCMapping, hint: Mapping):
    if not isinstance(argument, ABCMapping):
        return False, 'Argument is not an instance of collections.abc.Mapping.'

    # without parameters, or using standard TypeVar's
    if hint in [Mapping, MutableMapping, Dict]:
        return True, None

    # Mapping VT is covariant, MutableMapping and Dict VT is invariant
    if issubclass(hint, MutableMapping): # MutableMapping or Dict, invariant
        ktype, vtype = hint.__parameters__
        return _check_mapping_types(argument, ktype, vtype, covariant_vtype=False)

    if issubclass(hint, Mapping): # Mapping, covariant
        ktype, vtype = hint.__parameters__
        return _check_mapping_types(argument, ktype, vtype, covariant_vtype=True)


def _check_mapping_types(mapping, ktype, vtype, covariant_vtype=False):
    for k, v in mapping.items():
        if type(k) != ktype: # exact match
            return False, 'Key type for pair {0} in mapping is not consistent with typing {1}'\
                .format((k, v), (ktype, vtype))

        if covariant_vtype: # all subclasses are ok
            if not issubclass(v.__class__, vtype):
                return False, 'Value type for pair {0} in mapping is not consistent with typing {1}'\
                    .format((k, v), (ktype, vtype))

        else: # exact match
            if type(v) != vtype:
                return False, 'Value type for pair {0} in mapping is not consistent with typing {1}'\
                    .format((k, v), (ktype, vtype))

    return True, None

