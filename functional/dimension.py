from dataclasses import dataclass
from typing import Any, Union


@dataclass(frozen=True)
class Dimension:
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
