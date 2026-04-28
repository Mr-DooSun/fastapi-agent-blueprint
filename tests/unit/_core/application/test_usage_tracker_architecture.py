from pathlib import Path


def test_usage_tracker_does_not_import_provider_or_ai_usage_domain():
    source = Path("src/_core/application/usage_tracker.py").read_text()

    assert "pydantic_ai" not in source
    assert "openai" not in source
    assert "anthropic" not in source
    assert "src.ai_usage" not in source
