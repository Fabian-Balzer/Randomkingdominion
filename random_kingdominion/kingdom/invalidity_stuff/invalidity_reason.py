from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Type

from ...utils.utils import convert_upper_camel_to_snake_case

if TYPE_CHECKING:
    from ..kingdom import Kingdom

@dataclass
class InvalidityReason:
    params: dict[str, Any] = field(default_factory=dict)

    @property
    def key(self) -> str:
        return convert_upper_camel_to_snake_case(self.__class__.__name__)

    @property
    def name(self) -> str:
        return self.key.replace("_", " ").title()
    
    def __str__(self) -> str:
        return self.name
    
    @staticmethod
    def get_all_invalidity_reasons() -> list[Type[InvalidityReason]]:
        from . import all_invalidity_reasons  # Import the neighboring script
        members = inspect.getmembers(all_invalidity_reasons, inspect.isclass)
        return [cls
                for _, cls in members
                    if issubclass(cls, InvalidityReason)
                    and cls is not InvalidityReason
                    ]
    
    @staticmethod
    def check_kingdom_validity(k: Kingdom) -> list[InvalidityReason]:
        """Check the validity of the given kingdom."""
        reasons = []
        for reason_cls in InvalidityReason.get_all_invalidity_reasons():
            reason = reason_cls()
            if reason.check_if_invalid(k):
                reasons.append(reason)
        return reasons

    
    def get_description(self) -> str:
        raise NotImplementedError

    def check_if_invalid(self, k: Kingdom) -> bool:
        raise NotImplementedError

    def to_json(self) -> dict[str, Any]:
        return {
            "name": self.key,
            "params": self.params,
        }
