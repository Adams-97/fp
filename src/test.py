from typing import Iterable

import lib

modules = {'model_funcs'}
Life = lib.AlternativeDimension.new_alt_dimension_type('life')
YieldCurve = lib.AlternativeDimension.new_alt_dimension_type('yc')


dim_range = lib.DimensionRanges(
    range(0, 10),
    {
        Life: [1, 2, 3],
        YieldCurve: [1, 2, 3]
    }
)

lib.load_and_cache_calcs(modules, dim_range)
1
