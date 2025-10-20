from typing import Iterable

from functional.calculation_load import load_and_cache_calcs
from functional.dimension import DimensionRanges, OneValDimDict, Life, YieldCurve


ranges = OneValDimDict[Iterable]()
ranges[Life] = [1, 2, 3]
ranges[YieldCurve] = [1, 2, 3]

dr = DimensionRanges(
    t=range(0, 10),
    non_t=ranges
)

calcs = load_and_cache_calcs({'test2'}, dr, cache_size=None)
for calc in calcs:
    print(f'Calc Name: {calc.name}')
    ans = calc.function(100)
    print(calc.cache_info)