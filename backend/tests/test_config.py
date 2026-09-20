from backend.app.config.settings import get_settings

def test_settings_load_defaults():
    s = get_settings()
    assert s.app_name.startswith('Aegis')
