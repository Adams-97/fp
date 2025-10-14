import inspect
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum

from functional.dimension import Dimension
from functional.reference import RefData


class CalcType(Enum):
    NO_DIM_OR_REF = 1
    NO_DIM_BUT_REF = 2
    DIM_AND_NO_REF = 3
    DIM_AND_REF = 4

    @staticmethod
    def from_arguments(dimension_args: list[str] | None, ref_data: str | None) -> 'CalcType':
        if dimension_args and ref_data:
            return CalcType.DIM_AND_REF
        elif dimension_args and not ref_data:
            return CalcType.DIM_AND_NO_REF
        elif not dimension_args and ref_data:
            return CalcType.NO_DIM_BUT_REF
        elif not dimension_args and not ref_data:
            return CalcType.NO_DIM_OR_REF


@dataclass(frozen=True)
class Calc:
    name: str
    cached_func: Callable
    calc_type: CalcType
    dimensions: list[str] | None = None
    data_name: str | None = None

    @staticmethod
    def create(cached_func: Callable) -> 'Calc':
        dimensions, data_name = Calc._extract_function_args(cached_func)
        calc_type = CalcType.from_arguments(dimensions, data_name)
        return Calc(name=cached_func.__name__,
                    cached_func=cached_func,
                    calc_type=calc_type,
                    dimensions=dimensions,
                    data_name=data_name)

    @staticmethod
    def _extract_function_args(func: Callable) -> tuple[list[str] | None, str | None]:
        dimension_tracker = []
        data_tracker = []
        data = None

        for p in inspect.signature(func).parameters.values():
            if p.annotation == Dimension:
                dimension_tracker.append(p.name)
            elif p.annotation == RefData:
                data_tracker.append(p.name)
            else:
                continue

        dimensions = dimension_tracker or None

        if len(data_tracker) > 1:
            raise ValueError("More than 1 ref_data argument submitted for model calc")
        elif len(data_tracker) == 1:
            data = data_tracker[0]

        return dimensions, data
