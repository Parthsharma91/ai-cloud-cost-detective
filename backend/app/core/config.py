import os


def get_aws_region() -> str:
    """
    Return the AWS region used by the application.
    """

    return os.getenv(
        "AWS_REGION",
        "eu-north-1",
    )


def get_ai_provider() -> str:
    """
    Return the configured AI provider.
    """

    return os.getenv(
        "AI_PROVIDER",
        "mock",
    )