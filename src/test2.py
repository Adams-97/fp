import pandas as pd
from dask.distributed import Client
import dask.dataframe as dd
import dask
from distributed import get_worker

from src.lib.dimension import DimProjection
from src.lib.reference import CsvTable, RefData, RefTable
from src.lib.registry import CalcRegistry, CalcModule, FunctionPriority


def run_model(policy_rows: pd.DataFrame, mort_table: RefTable):
    modules = CalcModule.from_tuples([
        ('model_funcs', FunctionPriority.GENERAL)
    ])

    dr = DimProjection(range(0, 100))

    calcs = (
        CalcRegistry()
        .register_modules(modules)
        .register_function_groups({'a'})
    ).create_calculations(dr, function_cache_size=2)

    disc_rate_pa = 0.04

    data = RefData(policy_values=dict(init_age=65, sum_assured=100_000),
                   tables={'mort_table': mort_table},
                   global_values={'disc_rate_pm': (1 + disc_rate_pa) ** (1 / 12) - 1})

    worker = get_worker()
    flattened_res = {}
    for calc in calcs:
        flattened_res[calc.name] = []

    for index, policy in policy_rows.iterrows():
        for t in dr.t_range:
            for calc in calcs:
                res = calc.function(t, **{str(calc.data_arg): data})
                flattened_res[calc.name].append(res)
    print(f"Worker {worker.address} processed policy partition")
    return pd.DataFrame(flattened_res)


if __name__ == "__main__":
    client = Client(processes=True)
    print(client.dashboard_link)

    tables = CsvTable(csv='mort.csv', index_cols=['age'])
    send_data = client.scatter(tables, broadcast=True)

    df: dask.dataframe.DataFrame = dd.read_csv('policy.csv')
    meta = pd.DataFrame(
        columns=['age', 'expected_claim', 'num_alive', 'num_deaths', 'pv_claim', 'q_x', 'q_x_m', 't', 'v']
    )
    repartitioned_df = df.repartition(npartitions=100)
    res: dask.dataframe.DataFrame = repartitioned_df.map_partitions(run_model, mort_table=send_data, meta=meta)
    res2 = res.shape[0].compute()
    print(res2)
    1
    # 100_000_000