from collections import namedtuple, defaultdict

from calculation_load import load_and_cache_calcs
from functional.calculation import Calc, CalcType
from functional.reference import RefData
from functional.results import ResultHandler

module_names = set('model_funcs')
calculations = load_and_cache_calcs(module_names)

DimRange = namedtuple('DimRange', 'dimension range')


def _group_calc_types(calcs: list[Calc]) -> dict[CalcType, list[Calc]]:
    grouped = defaultdict(list)
    for calc in calcs:
        grouped[calc.calc_type].append(calc)
    return dict(grouped)


def run_calcs(calcs: list[Calc], data: RefData, result_handler: ResultHandler, dimension_projections: list[DimRange]):
    calcs_by_type: dict[CalcType, list[Calc]] = _group_calc_types(calcs)

    # Run dimensionless functions first
    for calc in calcs_by_type[CalcType.ALL] or calcs_by_type[CalcType.TIME_AND_SECONDARY_DIMS]:
        if calc.calc_type == CalcType.ALL:
            result_handler.add_result(calc.function())
        else:
            result_handler.add_result(calc.function(**{calc.data_name: data}))

