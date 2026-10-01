from abc import ABC, abstractmethod
from typing import Any

from backend.app.ai.models import AIAnalysisResponse


class AIProvider(ABC):
    @abstractmethod
    def analyze(
        self,
        question: str,
        investigation_data: dict[str, Any],
    ) -> AIAnalysisResponse:
        raise NotImplementedError