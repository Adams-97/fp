from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass


@dataclass(frozen=True)
class LookupArgs:
    index_values: dict[str, Any]
    return_col: str
    interpolated_lookup: bool


class RefTable(ABC):
    def __init__(self, index_cols: list[str]):
        self._index_cols: list[str] = index_cols
        self._cache: dict[LookupArgs, Any] = {}
        self._upper_col_bound: Optional[int] = None

    @staticmethod
    def _set_upper_col_bound(non_index_col_names: list[str]) -> Optional[int]:
        int_cols = []
        for col in non_index_col_names:
            try:
                int_cols.append(int(col))
            except (ValueError, TypeError):
                continue

        if not int_cols:
            return None
        else:
            return max(int_cols)

    @property
    def num_indexes(self) -> int:
        return len(self._index_cols)

    @property
    def index_cols(self) -> list[str]:
        return self._index_cols

    @property
    @abstractmethod
    def non_index_cols(self) -> list[str]:
        pass

    @abstractmethod
    def _retrieve_value(self, index_values: dict[str, Any], return_col: str) -> Optional[Any]:
        pass

    def interpolated_lookup(self, index_values: dict[str, Any], return_col: str):
        raise NotImplementedError()

    def lookup(self, index_values: dict[str, Any], return_col: str, interpolated_lookup: bool = False) -> Any:
        missing_index_cols = [col for col in self.index_cols if col not in index_values.keys()]
        if missing_index_cols:
            raise LookupError(f"Not all index columns specified: {", ".join(missing_index_cols)}")

        if interpolated_lookup:
            pass
        else:
            return self._retrieve_value(index_values, return_col)


class CsvTable(RefTable):
    from pandas import DataFrame

    def __init__(self, index_cols: list[str], csv: str | Path | DataFrame):
        super().__init__(index_cols)
        self._df = self._get_df(csv, index_cols)
        self._upper_col_bound = self._set_upper_col_bound(self.non_index_cols)

    def _get_df(self, csv: str | Path | DataFrame, index_cols: list[str]) -> DataFrame:
        from pandas import read_csv, DataFrame

        df = csv if isinstance(csv, DataFrame) else read_csv(csv)
        if list(df.index.names) != [None]:
            if list(df.index.names) == index_cols:
                # TODO: Log error message but ultimately respect df
                pass
            return df
        else:
            missing_index_cols = [col for col in index_cols if col not in df.columns]
            if missing_index_cols:
                raise ValueError(
                    f"The following index columns are missing from the CSV: {', '.join(missing_index_cols)}")
            df.set_index(self.index_cols, inplace=True)

        return df

    @property
    def non_index_cols(self) -> list[str]:
        return [col for col in self._df.columns if col not in self._df.index.names]

    def _retrieve_value(self, index_values: dict[str, Any], return_col: str) -> Optional[Any]:
        from pandas import Series

        index_tuple = tuple(index_values[level] for level in self._df.index.names)
        retrieved_value = self._df.loc[index_tuple, return_col]

        if isinstance(retrieved_value, Series):
            # TODO: Handle case where not just one value is present
            pass
        else:
            return retrieved_value


@dataclass(frozen=True)
class RefData:
    tables: dict[str, RefTable] | None = None
    values: dict[str, Any] | None = None

    def __hash__(self):
        return hash(id(self))
