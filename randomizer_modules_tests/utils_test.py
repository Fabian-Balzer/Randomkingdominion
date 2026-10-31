"""Tests for helpers in utils.py and the package's import handling."""

import random_kingdominion as rk
from random_kingdominion import _is_missing_package
from random_kingdominion.utils import utils


def test_version_is_the_highest_changelog_entry_numerically(monkeypatch):
    """As strings, "1.10.0" would sort before "1.9.1" (M15)."""
    changelog = {
        "1.9.1 (2026-11-01)": ["Older"],
        "1.10.0 (2026-12-01)": ["Newer"],
        "1.2.0 (2024-08-25)": ["Oldest"],
    }
    monkeypatch.setattr(utils, "get_changelog", lambda: changelog)
    assert utils.get_version() == "1.10.0"


def test_version_comes_from_the_changelog():
    newest = next(iter(rk.get_changelog()))
    assert rk.get_version() == newest.split(" ")[0]


def test_only_missing_optional_packages_are_skipped_at_import():
    """A missing optional package may be skipped, an import error inside our own
    code has to surface (M13)."""
    optional = {"streamlit", "streamlit_extras"}
    for name in ["streamlit", "streamlit.runtime", "streamlit_extras.grid"]:
        assert _is_missing_package(ModuleNotFoundError(name=name), optional), name
    for name in ["random_kingdominion.streamlit_util.typo", "streamlitx", None]:
        assert not _is_missing_package(ModuleNotFoundError(name=name), optional), name
