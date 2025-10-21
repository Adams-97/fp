import functools
import importlib
import inspect
from collections.abc import Callable
from dataclasses import dataclass, replace, astuple
from enum import Enum
from typing import Optional, NewType, Union

from src.lib.calculation import Calc, _CalcCreator
from src.lib.dimension import DimensionRanges


class FunctionPriority(Enum):
    USER_DEFINED = 200
    PRODUCT = 100
    GENERAL = 50


@dataclass(frozen=True)
class FunctionGroup:
    name: str
    priority: FunctionPriority = FunctionPriority.GENERAL


@dataclass(frozen=True)
class _FunctionDetails:
    name: str
    func: Callable
    module: str
    func_group: Optional[FunctionGroup]


def _create_cached_function_details(cache_size: Optional[int], func_detail: _FunctionDetails) -> _FunctionDetails:
    if _already_lru_cached(func_detail.func):
        return func_detail
    else:
        cached_func = functools.lru_cache(maxsize=cache_size)(func_detail.func)
        name, func, module, group = astuple(func_detail)
        func.__globals__[name] = cached_func
        return replace(func_detail, func=cached_func)


def register_func_group(groups: Union[set[str], str]):
    saved_groups = {groups} if isinstance(groups, str) else groups

    def wrapper(func):
        func._group_name = saved_groups
        return func
    return wrapper


def _already_lru_cached(func: Callable) -> bool:
    return hasattr(func, 'cache_info')


def _is_function(obj):
    return (inspect.isfunction(obj) or
            (callable(obj) and hasattr(obj, '__wrapped__') and inspect.isfunction(obj.__wrapped__))
            )


def _load_functions(modules: list[tuple[str, FunctionPriority]]) -> list[_FunctionDetails]:
    funcs = []
    for module_name, priority in modules:
        mod = importlib.import_module(module_name)
        for name, func_obj in inspect.getmembers(mod, _is_function):
            if hasattr(func_obj, '_group_name'):
                group_name: str = getattr(func_obj, '_group_name')
                func_group = FunctionGroup(name=group_name, priority=priority)
            else:
                func_group = None
            funcs.append(_FunctionDetails(name=name, func=func_obj, module=mod.__name__, func_group=func_group))
    return funcs


_ModuleName = NewType('_ModuleName', str)


class CalcRegistry:

    def __init__(self):
        self._registry: set[_FunctionDetails] = set()
        self._function_groups: set[FunctionGroup] = set()
        self._search_modules: dict[_ModuleName, FunctionPriority] = {}

    def create_calculations(self, dim_ranges: DimensionRanges, function_cache_size: Optional[int] = 10) -> list[Calc]:
        model_calculations: list[Calc] = []
        loaded_functions: list[_FunctionDetails] = _load_functions(list(self._search_modules.items()))

        for func_detail in loaded_functions:
            cached_func_detail = _create_cached_function_details(function_cache_size, func_detail)
            if cached_func_detail.func_group in self._function_groups:
                model_calculations.extend(_CalcCreator.create_calcs(cached_func_detail, dim_ranges))


        return model_calculations

    @property
    def search_modules(self) -> set[str]:
        return {name for name, priority in self._search_modules}

    def register_modules(self, modules: set[tuple[_ModuleName, FunctionPriority]]) -> 'CalcRegistry':
        for module_name, priority in modules:
            self._search_modules[module_name] = priority
        return self

    def remove_modules(self, modules: set[str]) -> 'CalcRegistry':
        for module in modules:
            self._search_modules.pop(_ModuleName(module))
        return self

    @property
    def function_groups(self) -> set[FunctionGroup]:
        return self._function_groups

    def register_function_groups(self, function_groups: set[FunctionGroup]) -> 'CalcRegistry':
        self._function_groups = self._function_groups.union(function_groups)
        return self

    def remove_function_groups(self, function_groups: set[FunctionGroup]) -> 'CalcRegistry':
        self._function_groups = self._function_groups - function_groups
        return self
