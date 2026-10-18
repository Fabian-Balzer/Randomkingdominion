"""Tests for the randomizer page: AppTest runs of the page (slow) and its helpers."""

from collections.abc import Iterator
from pathlib import Path

import matplotlib.pyplot as plt
import pytest
from streamlit import config
from streamlit.testing.v1 import AppTest

from random_kingdominion.kingdom import KingdomRandomizer
from random_kingdominion.streamlit_util.common_widgets.kingdom_display import (
    build_sidebar_kingdom_info,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
RANDOMIZER_PAGE = REPO_ROOT / "streamlit_pages" / "randomizer.py"
PLOT_EXPANDER_KEY = "kingdom_plot_expander_randomizer"


@pytest.fixture
def app(monkeypatch: pytest.MonkeyPatch) -> Iterator[AppTest]:
    monkeypatch.chdir(REPO_ROOT)
    # Some option tabs still use lambdas as callbacks, which AppTest can't serialize
    # (M5 in maintenance_plan.md)
    option = "runner.enforceSerializableSessionState"
    previous = config.get_option(option)
    config.set_option(option, False)
    at = AppTest.from_file(str(RANDOMIZER_PAGE), default_timeout=120)
    at.run()
    yield at
    config.set_option(option, previous)


def _click(at: AppTest, label_start: str) -> None:
    next(b for b in at.button if b.label.startswith(label_start)).click().run()


def _plot_expander(at: AppTest):
    return next(e for e in at.sidebar.expander if e.key == PLOT_EXPANDER_KEY)


@pytest.mark.slow
def test_randomize_shows_the_kingdom_and_a_toast_with_one_click(app: AppTest) -> None:
    _click(app, "Randomize")
    first = app.session_state["randomized_kingdom"]

    assert not app.exception
    assert first != ""
    assert [t.value for t in app.toast] == [
        "Randomization successful!\nGood luck and have fun!"
    ]
    # The second time, only the kingdom's fragment is rerun (st.rerun(<key>))
    _click(app, "Randomize")
    assert not app.exception
    assert app.session_state["randomized_kingdom"] != first
    assert len(app.toast) == 1


@pytest.mark.slow
def test_randomize_without_expansions_only_warns(app: AppTest) -> None:
    _click(app, "Clear selection")
    _click(app, "Randomize")

    assert not app.exception
    assert "randomized_kingdom" not in app.session_state
    assert any("No expansions selected" in t.value for t in app.toast)


@pytest.mark.slow
def test_single_reroll_replaces_the_kingdom(app: AppTest) -> None:
    _click(app, "Randomize")
    before = app.session_state["randomized_kingdom"]

    _click(app, "Reroll")

    assert not app.exception
    assert app.session_state["randomized_kingdom"] != before


@pytest.mark.slow
def test_sidebar_plot_is_only_drawn_when_its_expander_is_open(app: AppTest) -> None:
    _click(app, "Randomize")
    assert app.session_state[PLOT_EXPANDER_KEY] is False
    assert len(_plot_expander(app).image) == 0

    # What opening the expander does (it reruns, tracking its state)
    app.session_state[PLOT_EXPANDER_KEY] = True
    app.run()

    assert not app.exception
    assert len(_plot_expander(app).image) == 1


def test_kingdom_plot_is_rendered_once_and_its_figure_closed() -> None:
    k = KingdomRandomizer().randomize_new_kingdom()
    qualities = tuple((q, float(v)) for q, v in k.total_qualities.items())
    open_figures = len(plt.get_fignums())

    png = build_sidebar_kingdom_info._get_kingdom_miniplot_png(
        qualities, k.buy_availability, ""
    )

    assert png.startswith(b"\x89PNG")
    # The figures used to stay open, i.e. one leaked per rerun
    assert len(plt.get_fignums()) == open_figures
