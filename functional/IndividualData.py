from dataclasses import dataclass
from typing import Any

from functional.RefTable import RefTable


@dataclass(frozen=True)
class IndividualData:
    general_data: dict[str, RefTable] = None
    general_values: dict[str, Any] = None
