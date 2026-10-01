from backend.app.core.config import Settings


def test_settings_reads_environment_variables(monkeypatch):
    monkeypatch.setenv("AWS_REGION", "ap-south-1")
    monkeypatch.setenv("AI_PROVIDER", "test-ai")
    monkeypatch.setenv("COST_DATA_PROVIDER", "aws")

    test_settings = Settings()

    assert test_settings.aws_region == "ap-south-1"
    assert test_settings.ai_provider == "test-ai"
    assert test_settings.cost_data_provider == "aws"


def test_settings_defaults_when_environment_variables_are_missing(
    monkeypatch,
):
    monkeypatch.delenv("AWS_REGION", raising=False)
    monkeypatch.delenv("AI_PROVIDER", raising=False)
    monkeypatch.delenv("COST_DATA_PROVIDER", raising=False)

    test_settings = Settings()

    assert test_settings.aws_region == "eu-north-1"
    assert test_settings.ai_provider == "mock"
    assert test_settings.cost_data_provider == "aws"


def test_settings_object_uses_current_project_configuration():
    from backend.app.core.config import settings

    assert settings.aws_region == "eu-north-1"
    assert settings.ai_provider == "mock"
    assert settings.cost_data_provider == "mock"
