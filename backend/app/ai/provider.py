from abc import ABC, abstractmethod
from typing import Any


class AIProvider(ABC):
    """
    Interface for AI providers.

    Any AI provider used by the application must implement
    the analyze() method.
    """

    @abstractmethod
    def analyze(
        self,
        question: str,
        investigation_data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Analyze AWS cost investigation data.
        """
        raise NotImplementedError