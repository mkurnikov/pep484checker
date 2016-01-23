# -*- coding: utf-8 -*-
from typing import Any, TypingMeta, Tuple, Optional, CallableMeta, Callable, Union
import inspect
from inspect import Parameter


def check_type(argument: Any, hint: Union[type, None]) -> Tuple[bool, Optional[str]]:
    if hint is None:
        hint = type(None)

    if not isinstance(hint, type): # user error
        raise ValueError("Provided hint has to be instance of 'type'. Given {}".format(hint))

    if isinstance(hint, CallableMeta):
        return check_callable(argument, hint)

    if not issubclass(type(argument), hint):
        return False, 'Incorrect type {0}. Expected {1}'.format(type(argument), hint)

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





