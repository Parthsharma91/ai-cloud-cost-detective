import os
from dataclasses import dataclass, field

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    aws_region: str = field(
        default_factory=lambda: os.getenv(
            "AWS_REGION",
            "eu-north-1",
        )
    )

    ai_provider: str = field(
        default_factory=lambda: os.getenv(
            "AI_PROVIDER",
            "mock",
        )
    )

    cost_data_provider: str = field(
        default_factory=lambda: os.getenv(
            "COST_DATA_PROVIDER",
            "aws",
        )
    )


settings = Settings()


def get_aws_region() -> str:
    return settings.aws_region


def get_ai_provider() -> str:
    return settings.ai_provider


def get_cost_data_provider() -> str:
    return settings.cost_data_provider
