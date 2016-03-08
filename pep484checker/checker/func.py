# -*- coding: utf-8 -*-
from typing import TypingMeta, _type_check, TypeVar

from pep484checker.checker._helpers import evaluate_forward_reference, is_consistent_types
from ._checkers import _check_func_registry
from ._result_funcs import good_match, bad_match


def check_type(argument, hint, covariant=True, contravariant=False):
    # covariance/contravariance only makes sense to simple types
    hint = _type_check(hint, '`hint` argument is not an instance of `type`.')
    if hint == type(None):
        if argument is not None:
            return bad_match(argument, hint, 'Argument is not None.')
        else:
            return good_match()

    try:
        hint = evaluate_forward_reference(hint)
    except NameError:
        return bad_match(argument, hint, "Too early evaluation of {0}"
                         .format(hint))

    if isinstance(hint, TypingMeta):
        if hint.__class__ == TypeVar:
            hint_class = 'TypeVar'
        else:
            hint_class = hint.__name__ # ignores square brackers when Generic type
        _check_func = _check_func_registry[hint_class]
        return _check_func(argument, hint)

        # figure out if covariant/contravariant could be passed
        # _func_code_obj = _check_func.__call__.__code__
        # if 'covariant' in _func_code_obj.co_varnames[:_func_code_obj.co_argcount]: # func arguments
        #     return _check_func(argument, hint, covariant=covariant, contravariant=contravariant)
        # else:

    else:
        # simple type, use isinstance
        if is_consistent_types(argument.__class__, hint,
                               covariant=covariant,
                               contravariant=contravariant):
            return good_match()
        else:
            return bad_match(argument, hint)