import functools
import importlib
import inspect
from collections.abc import Callable

from functional.calculation import Calc


def load_and_cache_calcs(modules: set[str], cache_size: int = 20, func_predicate: Callable[[str], bool] = None) -> list[Calc]:
    funcs = []
    predicate = func_predicate if func_predicate else lambda x: True

    for module in modules:
        mod = importlib.import_module(module)
        for name, obj in inspect.getmembers(mod, inspect.isfunction):
            if predicate(name):
                cached_func = functools.lru_cache(maxsize=cache_size)(obj)
                setattr(mod, name, cached_func)
                funcs.append(Calc.create(cached_func))

    return funcs
