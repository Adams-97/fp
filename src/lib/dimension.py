import itertools
from abc import ABC
from dataclasses import dataclass, field
from typing import Union, TypeVar, Iterable, Type, Generic, Any, Optional


@dataclass(frozen=True)
class Dimension(ABC):
    name: str
    value: Any

    # Arithmetic operations
    def __add__(self, other: Union['Dimension', Any]):
        if isinstance(other, Dimension):
            self._check_equal_name(other)
            return Dimension(self.name, self.value + other.value)
        else:
            return Dimension(self.name, self.value + other)

    def __sub__(self, other: Union['Dimension', Any]):
        if isinstance(other, Dimension):
            self._check_equal_name(other)
            return Dimension(self.name, self.value - other.value)
        else:
            return Dimension(self.name, self.value - other)

    def __mul__(self, other: Union['Dimension', Any]):
        if isinstance(other, Dimension):
            self._check_equal_name(other)
            return Dimension(self.name, self.value * other.value)
        else:
            return Dimension(self.name, self.value * other)

    def __truediv__(self, other: Union['Dimension', Any]):
        if isinstance(other, Dimension):
            self._check_equal_name(other)
            return Dimension(self.name, self.value / other.value)
        else:
            return Dimension(self.name, self.value / other)

    # Comparison operations
    def __eq__(self, other: object) -> bool:
        if isinstance(other, Dimension):
            self._check_equal_name(other)
            return self.value == other.value
        else:
            return self.value == other

    def __lt__(self, other: Union['Dimension', Any]) -> bool:
        if isinstance(other, Dimension):
            self._check_equal_name(other)
            return self.value < other.value
        return self.value < other

    def __le__(self, other: Union['Dimension', Any]) -> bool:
        if isinstance(other, Dimension):
            self._check_equal_name(other)
            return self.value <= other.value
        return self.value <= other

    def __gt__(self, other: Union['Dimension', Any]) -> bool:
        if isinstance(other, Dimension):
            self._check_equal_name(other)
            return self.value > other.value
        return self.value > other

    def __ge__(self, other: Union['Dimension', Any]) -> bool:
        if isinstance(other, Dimension):
            self._check_equal_name(other)
            return self.value >= other.value
        return self.value >= other

    def __mod__(self, other):
        if isinstance(other, Dimension):
            self._check_equal_name(other)
            return self.value % other.value
        return self.value % other

    def _check_equal_name(self, other: 'Dimension'):
        if self.name != other.name:
            raise ValueError('Trying to perform operation on two different dimensions')


class Time(Dimension):
    def __init__(self, value: Any):
        super().__init__(name='t', value=value)


class AlternativeDimension(Dimension, ABC):

    @staticmethod
    def new_alt_dimension_type(name: str) -> Type['AlternativeDimension']:
        class _NewAlternativeDimension(AlternativeDimension):
            def __init__(self, value):
                super().__init__(name=name, value=value)

        return _NewAlternativeDimension


T = TypeVar('T')


class _DimensionDict(dict[type[Dimension], T], Generic[T]):
    def __init__(self, initial: Optional[dict[Type[Dimension], T]] = None):
        super().__init__()
        if initial:
            for k, v in initial.items():
                self[k] = v

    def __setitem__(self, key: Type[Dimension], value: T):
        if not issubclass(key, Dimension):
            raise KeyError('Key must be dim')
        elif key in self:
            raise KeyError('Key already exists')
        super().__setitem__(key, value)


class DimensionRanges:
    def __init__(self, t_range: Iterable, non_t_ranges: Optional[dict[Type[Dimension], Iterable]] = None):
        self.t_range: Iterable = t_range
        if non_t_ranges:
            self._secondary_dim_ranges: _DimensionDict[Iterable] = _DimensionDict(non_t_ranges)

    @property
    def secondary_dim_ranges(self) -> dict[Type[Dimension], Iterable]:
        if self._secondary_dim_ranges:
            return dict(self._secondary_dim_ranges)
        else:
            return {}

    def create_arg_combinations(self, dimensions: Iterable[Type[Dimension]]) -> list[tuple[Dimension, ...]]:
        if not self._secondary_dim_ranges:
            return []

        dim_types = list(dimensions)
        value_ranges = [self._secondary_dim_ranges[dim_type] for dim_type in dim_types]

        combinations = []
        for values in itertools.product(*value_ranges):
            combo = tuple(dim_type(value) for dim_type, value in zip(dim_types, values))
            combinations.append(combo)

        return combinations
