import inspect
import types
from functools import lru_cache, partial
from collections import namedtuple
from typing import Callable

from pandas import read_csv, DataFrame

from functional.RefTable import RefTable
from model_funcs import *

FuncInfo = namedtuple('FuncInfo', 'dimensions general_name individual_name')

def make_model(func_list, general: GeneralData):

    funcs: dict[str, tuple[Callable, FuncInfo]] = {}

    for func in func_list:
        general_param = ""
        individual_param = ""
        dimensions = []
        for p in inspect.signature(func).parameters.values():
            if p.annotation == Dimension:
                dimensions.append(p.name)
            elif p.annotation == GeneralData:
                general_param = p.name
            elif p.annotation == IndividualData:
                individual_param = p.name

        func_info = FuncInfo(dimensions=dimensions, general_name=general_param, individual_name=individual_param)
        stored_func = func
        if func_info.general_name != '':
            stored_func = partial(func, **{func_info.general_name: general})

        funcs[func.__name__] = (stored_func, func_info)

    return funcs


def apply_and_cache(funcs: dict[str, tuple[Callable, FuncInfo]], individual: IndividualData):
    output_funcs = {}

    for func_name, (func, func_info) in funcs.items():
        stored_func = func
        if func_info.individual_name != '':
            stored_func = partial(func, **{func_info.individual_name: individual})

        cached_func = lru_cache()(stored_func)
        output_funcs[func_name] = (cached_func, func_info.dimensions)

    return output_funcs


def get_funcs_from_file(module_name):
    target_functions = []
    for name, obj in globals().items():
        if isinstance(obj, types.FunctionType) and getattr(obj, "__module__") == module_name:
            target_functions.append(obj)
    return target_functions


mort_table = RefTable(read_csv('mort.csv'))
functions = get_funcs_from_file("model_funcs")
basis_tables = {'mort_table': mort_table}
basis_values = {'disc_rate_pm': 0.04}

individual_data = dict(init_age=65, sum_assured=100_000)

general_data = GeneralData(
    tables=basis_tables, values=basis_values
)
individual = IndividualData(
    tables=None, values=individual_data
)

model_template = make_model(functions, general_data)
model_instance = apply_and_cache(model_template, individual)

initial_dimension = Dimension('t', 0)
output_results = {}

for func_name, (func, dimensions) in model_instance:
    func_res = []
for t in range(0, 361):
    print(f'Running {t}')
    result.append(age_func[0](t))