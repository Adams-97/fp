import functools
import importlib
import inspect
from collections.abc import Callable
from typing import Optional

from src.calculation import Calc, CalcCreator
from src.dimension import DimensionRanges


def _already_lru_cached(func: Callable) -> bool:
    return hasattr(func, 'cache_info')


def load_and_cache_calcs(modules: set[str], dim_ranges: DimensionRanges, cache_size: Optional[int] = 20, func_predicate: Callable[[str], bool] = None) -> list[Calc]:
    funcs = []
    predicate = func_predicate if func_predicate else lambda x: True

    for module in modules:
        mod = importlib.import_module(module)

        for name, obj in inspect.getmembers(mod, inspect.isfunction):
            if predicate(name):
                if _already_lru_cached(obj):
                    funcs.extend(CalcCreator.create_calcs(obj, dim_ranges))
                else:
                    cached_func = functools.lru_cache(maxsize=cache_size)(obj)
                    obj.__globals__[name] = cached_func
                    funcs.extend(CalcCreator.create_calcs(cached_func, dim_ranges))

    return funcs
