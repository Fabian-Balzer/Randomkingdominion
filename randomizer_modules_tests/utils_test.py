"""Tests for helpers in utils.py and the package's import handling."""

import importlib
import re
import subprocess
import sys
from pathlib import Path

import pytest

import random_kingdominion as rk
import random_kingdominion.streamlit_util as rks
from random_kingdominion.utils import utils

ROOT = Path(__file__).parent.parent


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


@pytest.mark.slow
def test_the_core_imports_without_streamlit():
    """Scripts and notebooks use `rk` without the Streamlit layer (M18). A fresh
    process, as the tests themselves have imported Streamlit already."""
    code = (
        "import sys, random_kingdominion; "
        "print(sorted(m for m in sys.modules if m.split('.')[0] == 'streamlit'))"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == "[]"


@pytest.mark.parametrize(
    "init_path",
    sorted(ROOT.glob("random_kingdominion/**/__init__.py")),
    ids=lambda p: p.parent.relative_to(ROOT).as_posix(),
)
def test_every_exported_name_exists(init_path: Path):
    """Ruff flags imports missing from `__all__`, but not entries without an import
    (F822 is skipped in `__init__.py` files)."""
    package_name = ".".join(init_path.parent.relative_to(ROOT).parts)
    package = importlib.import_module(package_name)
    assert [name for name in package.__all__ if not hasattr(package, name)] == []


def _files_using_the_package() -> list[Path]:
    return [
        ROOT / "RandomKingdominion.py",
        *ROOT.glob("streamlit_pages/**/*.py"),
        *ROOT.glob("scripts/*.py"),
        *ROOT.glob("randomizer_modules_tests/*.py"),
    ]


@pytest.mark.parametrize(
    "alias, module", [("rk", rk), ("rks", rks)], ids=["core", "streamlit_util"]
)
def test_names_used_through_the_package_aliases_are_exported(alias, module):
    """`rk` and `rks` export the names used outside the package (M18); the scripts
    aren't run by any test, so a name dropped from `__all__` would only show up there.
    """
    pattern = re.compile(rf"\b{alias}\.([A-Za-z_]\w*)")
    missing = {
        f"{fpath.relative_to(ROOT).as_posix()}: {alias}.{name}"
        for fpath in _files_using_the_package()
        for name in pattern.findall(fpath.read_text(encoding="utf-8"))
        if name not in module.__all__
    }
    assert not missing
