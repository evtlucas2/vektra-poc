from pathlib import Path

from src.timeseries import app

_CONFIG = Path(__file__).parent.parent.parent / ".streamlit" / "config.toml"


def test_app_title_constant():
    assert app.APP_TITLE == "Vektra - Data science for personal finance"


def test_streamlit_config_exists():
    assert _CONFIG.exists()


def test_config_forces_dark_theme():
    content = _CONFIG.read_text()
    assert 'base = "dark"' in content


def test_config_hides_toolbar():
    content = _CONFIG.read_text()
    assert 'toolbarMode = "minimal"' in content
