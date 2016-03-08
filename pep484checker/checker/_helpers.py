# -*- coding: utf-8 -*-
from typing import _type_check, _ForwardRef

from pep484checker.checker._result_funcs import bad_match


def evaluate_forward_reference(hint):
    if isinstance(hint, _ForwardRef):
        if not hint.__forward_evaluated__:
            globalns = hint.__forward_frame__.f_globals
            localns = hint.__forward_frame__.f_locals
            hint._eval_type(globalns, localns)

        hint = hint.__forward_value__
    return hint


def is_consistent_types(arg_type, hint,
                        covariant=True, contravariant=False):
    # TODO: add support for TypingMeta subclasses
    consistent = False
    hint = _type_check(hint, '`hint` argument is not an instance of `type`.')
    if hint == type(None):
        consistent = arg_type is None or arg_type is type(None)

    try:
        hint = evaluate_forward_reference(hint)
    except NameError:
        return bad_match(arg_type, hint, "Too early evaluation of {0}"
                         .format(hint))

    if not consistent:
        consistent = (arg_type == hint)

    if not consistent and covariant:
        consistent = issubclass(arg_type, hint)

    if not consistent and contravariant:
        consistent = issubclass(hint, arg_type)

    return consistent

