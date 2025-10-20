import functools
import inspect
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import NewType, Optional

from functional.dimension import DimensionRanges, _OneValDimDict, Time, SecondaryDimension, Dimension
from functional.reference import RefData

TimeArgName = NewType('TimeArgName', str)
RefDataArgName = NewType('RefDataArgName', str)


class CalcType(Enum):
    TIME_ONLY = 1
    REF_ONLY = 2
    SECONDARY_DIMS_ONLY = 3
    TIME_AND_REF = 4
    TIME_AND_SECONDARY_DIMS = 5
    REF_AND_SECONDARY_DIMS = 6
    ALL = 7
    NO_ARGS = 8

    @staticmethod
    def from_arguments(t_name: Optional[TimeArgName],
                       data_name: Optional[RefDataArgName],
                       secondary_dims: Optional[_OneValDimDict[str]]) -> 'CalcType':
        match (t_name is not None, data_name is not None, secondary_dims is not None):
            case (False, False, False):
                return CalcType.NO_ARGS
            case (False, False, True):
                return CalcType.SECONDARY_DIMS_ONLY
            case (False, True, False):
                return CalcType.REF_ONLY
            case (False, True, True):
                return CalcType.REF_AND_SECONDARY_DIMS
            case (True, False, False):
                return CalcType.TIME_ONLY
            case (True, False, True):
                return CalcType.TIME_AND_SECONDARY_DIMS
            case (True, True, False):
                return CalcType.TIME_AND_REF
            case (True, True, True):
                return CalcType.ALL


@dataclass(frozen=True)
class Calc:
    name: str
    function: Callable
    calc_type: CalcType
    t_arg_name: Optional[TimeArgName]
    data_name: Optional[RefDataArgName]

    @property
    def t_dependent(self):
        return self.t_arg_name is not None


class CalcCreator:

    @staticmethod
    def create_calcs(function: Callable, dim_ranges: DimensionRanges) -> list[Calc]:
        non_t_dims, t_arg_name, data_arg_name = CalcCreator._find_dim_data_and_t_args(function)

        template_instance: Calc = Calc(
                name=function.__name__,
                function=function,
                calc_type=CalcType.from_arguments(t_arg_name, data_arg_name, non_t_dims),
                t_arg_name=t_arg_name,
                data_name=data_arg_name
            )

        if non_t_dims and dim_ranges.non_t:
            dim_combinations: list[tuple[Dimension, ...]] = dim_ranges.create_arg_combinations(non_t_dims.keys())
            return CalcCreator._create_partial_applied_calcs(dim_combinations, non_t_dims, template_instance)
        else:
            return [template_instance]

    @staticmethod
    def _find_dim_data_and_t_args(func: Callable) -> tuple[Optional[_OneValDimDict[str]], Optional[TimeArgName], Optional[RefDataArgName]]:
        dimension_tracker: _OneValDimDict[str] = _OneValDimDict[str]()
        ref_data_name: Optional[RefDataArgName] = None
        t_arg_name: Optional[TimeArgName] = None

        for param in inspect.signature(func).parameters.values():
            if issubclass(param.annotation, SecondaryDimension):
                dimension_tracker[param.annotation] = param.name
            elif param.annotation == Time:
                if t_arg_name is not None:
                    t_arg_name = TimeArgName(param.name)
                else:
                    raise ValueError('More than 1 Time argument in function')
            elif param.annotation == RefData:
                if ref_data_name is not None:
                    ref_data_name = RefDataArgName(param.name)
                else:
                    raise ValueError('More than 1 RefData argument in function')
        return dimension_tracker, t_arg_name, ref_data_name

    @staticmethod
    def _create_partial_applied_calcs(dim_combinations: list[tuple[Dimension, ...]],
                                      dim_arg_names: _OneValDimDict[str],
                                      template: Calc) -> list[Calc]:
        calcs: list[Calc] = []
        for combo in dim_combinations:
            kwargs = {dim_arg_names[type(dim)]: dim for dim in combo}

            partial_func = functools.partial(template.function, **kwargs)

            args_str = ", ".join(f"{dim_arg_names[type(dim)]}={repr(dim.value)}" for dim in combo)
            combo_name = f"{template.name}({args_str})"

            new_calc = Calc(
                name=combo_name,
                function=partial_func,
                calc_type=template.calc_type,
                t_arg_name=template.t_arg_name,
                data_name=template.data_name
            )

            calcs.append(new_calc)

        return calcs
