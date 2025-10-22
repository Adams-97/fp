import functools
import importlib
import inspect
from collections.abc import Callable
from dataclasses import dataclass, replace, astuple
from enum import Enum
from typing import Optional

from src.lib.calculation import Calc, _CalcCreator
from src.lib.dimension import DimensionRanges
from src.lib.types import FunctionDetails, FunctionPriority


def _create_cached_function_details(cache_size: Optional[int], func_detail: FunctionDetails) -> FunctionDetails:
    if _already_lru_cached(func_detail.func):
        return func_detail
    else:
        cached_func = functools.lru_cache(maxsize=cache_size)(func_detail.func)
        name, func, module, group = astuple(func_detail)
        func.__globals__[name] = cached_func
        return replace(func_detail, func=cached_func)


def register_func_group(group: str):
    def wrapper(func):
        func._group_name = group
        return func

    return wrapper


def _already_lru_cached(func: Callable) -> bool:
    return hasattr(func, 'cache_info')


def _is_function(obj):
    return (inspect.isfunction(obj) or
            (callable(obj) and hasattr(obj, '__wrapped__') and inspect.isfunction(obj.__wrapped__))
            )


@dataclass(frozen=True)
class CalcModule:
    name: str
    priority: FunctionPriority

    @classmethod
    def from_tuple(cls, data: tuple[str, FunctionPriority]) -> 'CalcModule':
        name, priority = data
        return cls(name, priority)

    @classmethod
    def from_tuples(cls, data: list[tuple[str, FunctionPriority]]) -> set['CalcModule']:
        """Convert a list of (name, priority) tuples to a set of CalcModule instances."""
        return {cls.from_tuple(item) for item in data}


def _load_functions(modules: list[CalcModule]) -> list[FunctionDetails]:
    funcs = []
    for module in modules:
        mod = importlib.import_module(module.name)
        for name, func_obj in inspect.getmembers(mod, _is_function):
            if hasattr(func_obj, '_group_name'):
                group_name: str = getattr(func_obj, '_group_name')
                func_group = group_name
            else:
                func_group = None
            funcs.append(FunctionDetails(name=name, func=func_obj, module=mod.__name__, func_group=func_group))
    return funcs


class CalcRegistry:

    def __init__(self):
        self._registry: set[FunctionDetails] = set()
        self._function_groups: set[str] = set()
        self._search_modules: set[CalcModule] = set()

    def create_calculations(self, dim_ranges: DimensionRanges, function_cache_size: Optional[int] = 10) -> list[Calc]:
        model_calculations: list[Calc] = []
        loaded_functions: list[FunctionDetails] = _load_functions(list(self._search_modules))

        for func_detail in loaded_functions:
            cached_func_detail = _create_cached_function_details(function_cache_size, func_detail)
            if cached_func_detail.func_group in self._function_groups:
                model_calculations.extend(_CalcCreator.create_calcs(cached_func_detail, dim_ranges))

        return model_calculations

    @property
    def search_modules(self) -> set[str]:
        return {name for name, priority in self._search_modules}

    def register_modules(self, new_modules: set[CalcModule]) -> 'CalcRegistry':
        modules_by_name = {module.name: module for module in self._search_modules}
        for new_module in new_modules:
            modules_by_name[new_module.name] = new_module

        self._search_modules = set(modules_by_name.values())
        return self

    def remove_modules(self, modules: set[str]) -> 'CalcRegistry':
        self._search_modules = {
            module for module in self._search_modules if module.name not in modules
        }
        return self

    @property
    def function_groups(self) -> set[str]:
        return self._function_groups

    def register_function_groups(self, function_group_name: set[str]) -> 'CalcRegistry':
        self._function_groups = self._function_groups.union(function_group_name)
        return self

    def remove_function_groups(self, function_groups: set[str]) -> 'CalcRegistry':
        self._function_groups = self._function_groups - function_groups
        return self
