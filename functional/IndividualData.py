from dataclasses import dataclass
from typing import Any

from functional.RefTable import RefTable


@dataclass(frozen=True)
class IndividualData:
    tables: dict[str, RefTable] | None = None
    values: dict[str, Any] | None = None
