from pandas import read_csv

from calculation_load import load_and_cache_calcs
from functional.reference import RefTable, RefData

mort_table = RefTable(read_csv('mort.csv'))
ref_tables = {'mort_table': mort_table}
ref_values = {'disc_rate_pm': 0.04, 'init_age': 65, 'sum_assured': 100_000}
data = RefData(tables=ref_tables, values=ref_values)


modules = {"model_funcs"}
calcs = load_and_cache_calcs(modules)


for t in range(0, 361):
    print(f'Running {t}')
    for calc in calcs:
        calc.cached_func(t, **{calc.data_name: data})
