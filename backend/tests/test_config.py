"""
Tests for Aegis Configuration & Settings.
"""

from backend.app.config.settings import Settings, get_settings


def test_settings_load_defaults():
    """Verify settings load with standard safe defaults."""
    settings = get_settings()
    assert settings.app_name.startswith("Aegis")
    assert settings.max_self_correction_attempts == 3
    assert settings.grounding_threshold > 0.0
    assert settings.chunk_size > 0
    assert settings.chunk_overlap >= 0
    assert settings.retrieval_top_k > 0
    assert settings.reranking_top_k > 0
    assert settings.reranking_top_k <= settings.retrieval_top_k


def test_settings_custom_values():
    """Verify settings can be instantiated with custom values."""
    custom = Settings(
        app_env="testing",
        chunk_size=1000,
        grounding_threshold=0.85,
        max_self_correction_attempts=2,
    )
    assert custom.app_env == "testing"
    assert custom.chunk_size == 1000
    assert custom.grounding_threshold == 0.85
    assert custom.max_self_correction_attempts == 2
