from dataclasses import dataclass
from typing import Any, Union


@dataclass(frozen=True)
class Dimension:
    name: str
    value: Any

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
            return Dimension(self.name,self.value * other)

    def __truediv__(self, other: Union['Dimension', Any]):
        if isinstance(other, Dimension):
            self._check_equal_name(other)
            return Dimension(self.name, self.value / other.value)
        else:
            return Dimension(self.name, self.value / other)

    def _check_equal_name(self, other: 'Dimension'):
        if self.name != other.name:
            raise ValueError('Trying to perform operation on two different dimensions')