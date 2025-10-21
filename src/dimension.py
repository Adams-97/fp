import itertools
from abc import ABC
from dataclasses import dataclass, field
from typing import Union, TypeVar, Iterable, Type, Generic, Optional

number = TypeVar('number', int, float)


@dataclass(frozen=True)
class Dimension(ABC):
    name: str
    value: number

    # Arithmetic operations
    def __add__(self, other: Union['Dimension', number]):
        if isinstance(other, Dimension):
            self._check_equal_name(other)
            return Dimension(self.name, self.value + other.value)
        else:
            return Dimension(self.name, self.value + other)

    def __sub__(self, other: Union['Dimension', number]):
        if isinstance(other, Dimension):
            self._check_equal_name(other)
            return Dimension(self.name, self.value - other.value)
        else:
            return Dimension(self.name, self.value - other)

    def __mul__(self, other: Union['Dimension', number]):
        if isinstance(other, Dimension):
            self._check_equal_name(other)
            return Dimension(self.name, self.value * other.value)
        else:
            return Dimension(self.name, self.value * other)

    def __truediv__(self, other: Union['Dimension', number]):
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

    def __lt__(self, other: Union['Dimension', number]) -> bool:
        if isinstance(other, Dimension):
            self._check_equal_name(other)
            return self.value < other.value
        return self.value < other

    def __le__(self, other: Union['Dimension', number]) -> bool:
        if isinstance(other, Dimension):
            self._check_equal_name(other)
            return self.value <= other.value
        return self.value <= other

    def __gt__(self, other: Union['Dimension', number]) -> bool:
        if isinstance(other, Dimension):
            self._check_equal_name(other)
            return self.value > other.value
        return self.value > other

    def __ge__(self, other: Union['Dimension', number]) -> bool:
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
    def __init__(self, value: number):
        super().__init__(name='t', value=value)


class SecondaryDimension(Dimension):
    pass


class Life(SecondaryDimension):
    def __init__(self, value: number):
        super().__init__(name='life', value=value)


class YieldCurve(SecondaryDimension):
    def __init__(self, value: number):
        super().__init__(name='yc', value=value)


T = TypeVar('T')


class OneValDimDict(dict[type[Dimension], T], Generic[T]):
    def __setitem__(self, key: Type[Dimension], value: T):
        if not issubclass(key, Dimension):
            raise KeyError('Key must be dim')
        elif key in self:
            raise KeyError('Key already exists')
        super().__setitem__(key, value)


@dataclass(frozen=True)
class DimensionRanges:
    t: Iterable
    non_t: OneValDimDict[Iterable] = field(default_factory=OneValDimDict[Iterable])

    def create_arg_combinations(self, dimensions: Iterable[Type[Dimension]]) -> list[tuple[Dimension, ...]]:
        if not self.non_t:
            return []

        dim_types = list(dimensions)
        value_ranges = [self.non_t[dim_type] for dim_type in dim_types]

        combinations = []
        for values in itertools.product(*value_ranges):
            combo = tuple(dim_type(value) for dim_type, value in zip(dim_types, values))
            combinations.append(combo)

        return combinations
