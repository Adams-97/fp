import functools
import importlib
import inspect
from collections import namedtuple
from collections.abc import Callable

from pandas import read_csv

from functional.dimension import Dimension
from functional.reference import RefData, RefTable


FuncParams = namedtuple('FuncParams', 'dimensions data')


def extract_function_args(f: Callable) -> FuncParams:
    dimensions = []
    ref_data = []

    for p in inspect.signature(f).parameters.values():
        if p.annotation == Dimension:
            dimensions.append(p.name)
        elif p.annotation == RefData:
            ref_data.append(p.name)
        else:
            continue

    if len(ref_data) > 1:
        raise ValueError("More than 1 ref_data submitted for model")
    return FuncParams(dimensions=dimensions, data=ref_data[0])


def load_and_cache_functions(modules: set[str], cache_size: int) -> dict[str, tuple[Callable, FuncParams]]:
    funcs = {}

    for module in modules:
        mod = importlib.import_module(module)
        for name, obj in inspect.getmembers(mod, inspect.isfunction):
            function_params = extract_function_args(obj)
            cached_func = functools.lru_cache(maxsize=cache_size)(obj)
            setattr(mod, name, cached_func)
            funcs[name] = cached_func, function_params
    return funcs


mort_table = RefTable(read_csv('mort.csv'))
ref_tables = {'mort_table': mort_table}
ref_values = {'disc_rate_pm': 0.04, 'init_age': 65, 'sum_assured': 100_000}
data = RefData(tables=ref_tables, values=ref_values)

cached_funcs = load_and_cache_functions({'model_funcs'}, 2)

for t in range(0, 360):
    print(f'Calculating {t}')
    for func_name, (func, params) in cached_funcs.items():
        res = func(t, **{params.data: data})
        if t == 359:
            print(f'{func_name}: a - {res}')
            print(f'{func_name}: {func.cache_info()}')
