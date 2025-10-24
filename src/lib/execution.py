from collections import defaultdict

from src.lib.calculation import Calc, CalcType
from src.lib.reference import RefData


def _group_calc_types(calcs: list[Calc]) -> dict[CalcType, list[Calc]]:
    grouped = defaultdict(list)
    for calc in calcs:
        grouped[calc.type].append(calc)
    return dict(grouped)


def run_calcs(calcs: list[Calc], data: list[RefData], dimension_projections: list[DimRange]):
    calcs_by_type: dict[CalcType, list[Calc]] = _group_calc_types(calcs)

    # Run dimensionless functions first
    for calc in calcs_by_type[CalcType.ALL] or calcs_by_type[CalcType.TIME_AND_ALT_DIMS]:
        if calc.type == CalcType.ALL:
            result_handler.add_result(calc.function())
        else:
            result_handler.add_result(calc.function(**{calc.data_arg: data}))

