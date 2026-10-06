from abc import ABC, abstractmethod
from typing import Generic, TypeVar


InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")


class BaseAgent(ABC, Generic[InputT, OutputT]):
    """Base contract for all agents."""

    name: str

    @abstractmethod
    async def run(self, input_data: InputT) -> OutputT:
        """Execute the agent and return its typed result."""
        raise NotImplementedError