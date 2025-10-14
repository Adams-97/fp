from typing import Any
from pandas import DataFrame
from dataclasses import dataclass


@dataclass(frozen=True)
class RefTable:
    data: DataFrame

    def lookup(self, column: str, value: Any, res_col: str):
        lookup = self.data[self.data[column] == value]
        try:
            return lookup.iloc[0][res_col]
        except IndexError:
            print(f'Index error on value: {value} and column: {column}')
            max_index = self.data[column].idxmax()
            return self.data.loc[max_index][res_col]


@dataclass(frozen=True)
class RefData:
    tables: dict[str, RefTable] | None = None
    values: dict[str, Any] | None = None

    def __hash__(self):
        return hash(id(self))
