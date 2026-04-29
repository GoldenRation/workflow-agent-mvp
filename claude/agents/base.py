from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentResult:
    name: str
    summary: str
    data: Any = field(default_factory=dict)


class BaseAgent:
    name = "BaseAgent"

    def run(self, *args, **kwargs) -> AgentResult:
        raise NotImplementedError
