"""Shared types to avoid circular dependencies."""
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Optional, NewType


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
                       secondary_dims: Optional[dict]) -> 'CalcType':
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


class FunctionPriority(Enum):
    USER_DEFINED = 200
    PRODUCT = 100
    GENERAL = 50


@dataclass(frozen=True)
class FunctionDetails:
    """Details about a registered function."""
    name: str
    func: Callable
    module: str
    func_group: Optional[str]