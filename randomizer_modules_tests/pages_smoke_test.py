"""Every page renders without exceptions (M5), plus a run of the oracle with an
entered kingdom. Each page runs once through Streamlit's AppTest (~2 s each)."""

from collections.abc import Iterator
from pathlib import Path

import pytest
from streamlit import config
from streamlit.testing.v1 import AppTest

pytestmark = pytest.mark.slow

REPO_ROOT = Path(__file__).resolve().parents[1]
PAGES = sorted(REPO_ROOT.joinpath("streamlit_pages").rglob("*.py"))
PAGE_IDS = [p.relative_to(REPO_ROOT / "streamlit_pages").as_posix() for p in PAGES]


@pytest.fixture(autouse=True)
def _serializable_state_off(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    monkeypatch.chdir(REPO_ROOT)
    # Some widgets still use lambdas as callbacks, which AppTest can't serialize
    # (see the docstring of conftest.py)
    option = "runner.enforceSerializableSessionState"
    previous = config.get_option(option)
    config.set_option(option, False)
    yield
    config.set_option(option, previous)


def _run(page: Path) -> AppTest:
    return AppTest.from_file(str(page), default_timeout=120).run()


@pytest.mark.parametrize("page", PAGES, ids=PAGE_IDS)
def test_page_renders_without_exceptions(page: Path):
    at = _run(page)
    assert [e.message for e in at.exception] == []


def test_oracle_shows_an_entered_kingdom():
    at = _run(REPO_ROOT / "streamlit_pages" / "kingdom_oracle.py")
    assert len(at.get("image")) == 0

    at.text_input(key="oracle_kingdom_input").input(
        "Young Witch (Moat), Village, Smithy, Chapel, Market, Militia, Witch, "
        "Festival, Library, Laboratory, Way of the Mouse (Harbinger), Colonies"
    ).run()

    assert [e.message for e in at.exception] == []
    # The quality plot, and the kingdom's DomBot string to copy
    assert len(at.get("image")) == 1
    assert any("Young Witch (Moat)" in code.value for code in at.code)
