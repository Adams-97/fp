from src.lib.dimension import DimensionRanges
from src.lib.registry import CalcRegistry, CalcModule, FunctionPriority
from src.model_dims import Life, YieldCurve

modules = CalcModule.from_tuples([
    ('model_funcs', FunctionPriority.GENERAL),
    ('model_funcs2', FunctionPriority.PRODUCT),
    ('model_funcs3', FunctionPriority.USER_DEFINED)
])

dr = DimensionRanges(
    t_range=range(0, 100),
    non_t_ranges={
        Life: [1, 2, 3],
        YieldCurve: ["N", "Y"]
    }
)

calcs = (
    CalcRegistry()
    .register_modules(modules)
    .register_function_groups({'a'})
).create_calculations(dr)

1