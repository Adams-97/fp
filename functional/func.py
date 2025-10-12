import inspect
import types
from functools import lru_cache, partial
from types import SimpleNamespace
from pandas import read_csv, DataFrame

from functional.RefTable import RefTable
from functional.general_data import GeneralData
from model_funcs import *

def make_model(func_list, basis, data):
    funcs = {}
    ctx = SimpleNamespace(basis=basis, data=data)

    for func in func_list:
        parameters = [p for p in inspect.signature(func).parameters.keys() if not p == 'ctx']
        ctx_applied_func = partial(func, ctx=ctx)
        cached_func = lru_cache(maxsize=128)(ctx_applied_func)
        funcs[func.__name__] = (cached_func, parameters)

    return funcs


def get_funcs_from_file(module_name):
    target_functions = []
    for name, obj in globals().items():
        if isinstance(obj, types.FunctionType) and getattr(obj, "__module__") == module_name:
            target_functions.append(obj)
    return target_functions


mort_table = RefTable(read_csv('mort.csv'))
functions = get_funcs_from_file("model_funcs")
basis = {'disc_rate_pm': 0.04, 'mort_table': mort_table}
data = dict(init_age=65, sum_assured=100_000)

model_template = make_model(functions, basis=basis, data=data)
results = {}

for func_name, (func, args) in model_template.items():
    if func_name != 'age':
        continue
    else:
        func_results = []
        for t in range(0, 361):
            print(f'Running {func_name}, {t}')
            print(f"{func_name}: {func.cache_info()}")
            func_results.append(func(t))
        results[func_name] = func_results

df = DataFrame(results)
df.to_csv('res.csv', index=False)