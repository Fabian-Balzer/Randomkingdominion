"""The shareable image of a quiz result: the settings, score and time, and per kingdom
the plot of the answers vs. the solution and a miniature of its cards.
Kept free of Streamlit, like the scoring."""

from dataclasses import dataclass
from functools import lru_cache
from io import BytesIO
from math import ceil

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from matplotlib.patches import FancyBboxPatch
from PIL import Image, ImageDraw, ImageOps

from ...constants import QUALITIES_AVAILABLE
from ...kingdom import Kingdom
from ...utils import (
    DOM_BEIGE,
    DOM_BLUE,
    XKCD_FONT,
    annotate_buy_icon,
    get_square_cutout,
    get_version,
    plot_quality_polygon,
    set_up_ax_for_quality_plot,
)
from .kingdom_pool import get_curated_kingdom_name
from .run_state import QuizMode, QuizRunState
from .scoring import (
    MAX_ROUND_SCORE,
    QUIZ_QUALITY_NAMES,
    BuyAvailability,
    get_buy_points,
    get_kingdom_solution,
    get_score_band,
)

QUIZ_SHARE_URL = "randomkingdominion.streamlit.app/quiz"
MAX_PLAYER_NAME_LENGTH = 30

# The order of the kingdom plots elsewhere
_PLOT_QUALITIES = [q for q in QUALITIES_AVAILABLE if q in QUIZ_QUALITY_NAMES]

_USER_COLOR = "darkred"
_BG_COLOR = "#F3EDD8"
_PANEL_COLOR = "#E6DCB4"
_DPI = 130

# Sizes in inches
_COL_WIDTH = 3.0
_COL_PAD = 0.15
_MARGIN = 0.25
_HEADER_HEIGHT = 1.3
_LABEL_HEIGHT = 0.55
_SCORE_HEIGHT = 0.6
_EXTRAS_HEIGHT = 0.25
_FOOTER_HEIGHT = 0.35

# The card miniatures, in pixels
# The width of the miniatures, so that the tiles have the same size in all kingdoms
_MIN_TILES_PER_ROW = 5
_TILE_SIZE = 96
_TILE_GAP = 8
_LANDSCAPE_GAP = 20


@dataclass(frozen=True)
class _ShareRound:
    kingdom: str
    quality_values: tuple[float, ...]
    """The answers, in the order of `QUIZ_QUALITY_NAMES`."""
    buy_availability: BuyAvailability
    score: float
    elapsed_time: float
    name: str
    """The name of a curated kingdom, empty otherwise."""


@dataclass(frozen=True)
class _ShareSummary:
    """Everything the image shows, hashable so that the rendering can be cached."""

    title: str
    settings: str
    rounds: tuple[_ShareRound, ...]
    player_name: str
    date: str

    @property
    def total_score(self) -> float:
        return sum(r.score for r in self.rounds)

    @property
    def maximum_score(self) -> int:
        return len(self.rounds) * MAX_ROUND_SCORE

    @property
    def total_time(self) -> float:
        return sum(r.elapsed_time for r in self.rounds)


def _strip_icon(label: str) -> str:
    """The labels start with an emoji, and may contain a middle dot, neither of which
    the font can draw."""
    return label.split(" ", 1)[-1].replace("·", "|")


def _format_duration(seconds: float) -> str:
    minutes, seconds = divmod(int(seconds), 60)
    return f"{minutes:02d}:{seconds:02d}"


def _get_kingdom_name(run_state: QuizRunState, kingdom_str: str) -> str:
    name = get_curated_kingdom_name(run_state.pool, kingdom_str)
    if name is None:
        return ""
    label = run_state.pool.source.get_kingdom_name_label(name)
    return _strip_icon(label).replace("*", "").replace("Recommended kingdom ", "")


def _get_share_summary(run_state: QuizRunState, player_name: str) -> _ShareSummary:
    if not run_state.completed_rounds:
        raise ValueError("There are no completed rounds to share.")
    rounds = tuple(
        _ShareRound(
            kingdom=r.kingdom,
            quality_values=tuple(
                r.submitted_answers.quality_values[q] for q in QUIZ_QUALITY_NAMES
            ),
            buy_availability=r.submitted_answers.buy_availability,
            score=r.score,
            elapsed_time=r.elapsed_time,
            name=_get_kingdom_name(run_state, r.kingdom),
        )
        for r in run_state.completed_rounds
    )
    if run_state.mode is QuizMode.PRACTICE:
        title = "Practice"
    else:
        title = f"{run_state.round_count} Kingdom Run"
    return _ShareSummary(
        title=title,
        settings=f"{_strip_icon(run_state.difficulty.label)} | {_strip_icon(run_state.pool.label)}",
        rounds=rounds,
        player_name=player_name.strip()[:MAX_PLAYER_NAME_LENGTH],
        # The end of the last round instead of today, so that the image stays the same
        date=run_state.completed_rounds[-1].end_time.strftime("%Y-%m-%d"),
    )


def _fig_to_png(fig: Figure, **kwargs) -> bytes:
    buffer = BytesIO()
    fig.savefig(buffer, format="png", **kwargs)
    plt.close(fig)
    return buffer.getvalue()


def _get_quality_plot_img(share_round: _ShareRound) -> np.ndarray:
    """The plot of the answers (red) and the solution (blue), as in the quiz."""
    solution = get_kingdom_solution(share_round.kingdom)
    answers = dict(zip(QUIZ_QUALITY_NAMES, share_round.quality_values))
    fig, ax = set_up_ax_for_quality_plot(_PLOT_QUALITIES)
    annotate_buy_icon(ax, solution.buy_availability)
    plot_quality_polygon(
        ax, [answers[q] for q in _PLOT_QUALITIES], linecolor=_USER_COLOR
    )
    plot_quality_polygon(ax, [solution.quality_values[q] for q in _PLOT_QUALITIES])
    png = _fig_to_png(fig, bbox_inches="tight", dpi=120, transparent=True)
    return plt.imread(BytesIO(png))


def _get_tile(cso_key: str) -> Image.Image:
    tile = ImageOps.fit(get_square_cutout(cso_key).convert("RGBA"), (_TILE_SIZE,) * 2)
    mask = Image.new("L", tile.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, _TILE_SIZE - 1, _TILE_SIZE - 1], radius=12, fill=255
    )
    tile.putalpha(mask)
    return tile


def _get_card_grid_positions(num_cards: int) -> list[tuple[int, int]]:
    """The (column, row) of each card, sorted by cost, as in the quiz's kingdom
    view: two rows, the cheaper half in the lower one, cost rising left to right."""
    num_cols = ceil(num_cards / 2)
    positions = []
    for i in range(num_cards):
        # Filled from the most expensive card on, from the top right
        j = num_cards - 1 - i
        positions.append((num_cols - j % num_cols - 1, j // num_cols))
    return positions


def _get_card_mosaic(k: Kingdom) -> Image.Image:
    """The art of the kingdom's cards (arranged by cost, as in the quiz), with the
    landscapes in framed rows below."""
    cards = k.kingdom_card_df
    cards = cards.assign(CostSort=cards["Cost"].str.replace("$", "Z"))
    card_keys = list(cards.sort_values(["CostSort", "Name"]).index)
    card_positions = _get_card_grid_positions(len(card_keys))
    landscape_keys = list(k.kingdom_landscape_df.index)
    num_cols = max(ceil(len(card_keys) / 2), _MIN_TILES_PER_ROW)
    card_rows = max((row + 1 for _, row in card_positions), default=0)
    landscape_rows = ceil(len(landscape_keys) / num_cols)
    step = _TILE_SIZE + _TILE_GAP
    width = num_cols * step - _TILE_GAP
    height = (card_rows + landscape_rows) * step - _TILE_GAP
    if landscape_rows > 0:
        height += _LANDSCAPE_GAP
    mosaic = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(mosaic)
    for key, (col, row) in zip(card_keys, card_positions):
        mosaic.alpha_composite(_get_tile(str(key)), (col * step, row * step))
    landscapes_top = card_rows * step + _LANDSCAPE_GAP
    for i, key in enumerate(landscape_keys):
        x = (i % num_cols) * step
        y = landscapes_top + (i // num_cols) * step
        mosaic.alpha_composite(_get_tile(str(key)), (x, y))
        draw.rounded_rectangle(
            [x, y, x + _TILE_SIZE - 1, y + _TILE_SIZE - 1],
            radius=12,
            outline=DOM_BLUE,
            width=4,
        )
    return mosaic


def _get_extras_text(k: Kingdom) -> str:
    extras = ["Colonies"] * k.use_colonies + ["Shelters"] * k.use_shelters
    return " + ".join(extras)


class _Layout:
    """Places axes and texts in inches, measured from the top left corner."""

    def __init__(self, fig: Figure, width: float, height: float):
        self.fig = fig
        self.width = width
        self.height = height

    def add_axes(self, x: float, top: float, width: float, height: float):
        ax = self.fig.add_axes(
            (
                x / self.width,
                1 - (top + height) / self.height,
                width / self.width,
                height / self.height,
            )
        )
        ax.set_axis_off()
        return ax

    def add_panel(self, x: float, top: float, width: float, height: float, **kwargs):
        self.fig.patches.append(
            FancyBboxPatch(
                (x / self.width, 1 - (top + height) / self.height),
                width / self.width,
                height / self.height,
                boxstyle="round,pad=0,rounding_size=0.01",
                transform=self.fig.transFigure,
                figure=self.fig,
                # Behind the axes
                zorder=-1,
                **kwargs,
            )
        )

    def text(self, x: float, top: float, text: str, size: float, **kwargs):
        kwargs.setdefault("color", "black")
        self.fig.text(
            x / self.width,
            1 - top / self.height,
            text,
            fontproperties=XKCD_FONT,
            fontsize=size,
            va="top",
            **kwargs,
        )


def _get_score_box(score: float, maximum: float) -> dict:
    band = get_score_band(score / maximum * MAX_ROUND_SCORE)
    return {
        "boxstyle": "round,pad=0.3",
        "facecolor": band.color,
        "edgecolor": "black",
        "linewidth": 1.5,
    }


def _draw_header(layout: _Layout, summary: _ShareSummary) -> None:
    right = layout.width - _MARGIN
    layout.text(_MARGIN, _MARGIN, f"Dominion Kingdom Quiz - {summary.title}", 24)
    layout.text(_MARGIN, _MARGIN + 0.5, summary.settings, 14)
    if summary.player_name:
        layout.text(_MARGIN, _MARGIN + 0.8, f"Played by {summary.player_name}", 14)
    layout.text(
        right,
        _MARGIN + 0.05,
        f"{summary.total_score:g}/{summary.maximum_score}",
        26,
        ha="right",
        bbox=_get_score_box(summary.total_score, summary.maximum_score),
    )
    details = f"Time {_format_duration(summary.total_time)}"
    if len(summary.rounds) > 1:
        perfect = sum(r.score == MAX_ROUND_SCORE for r in summary.rounds)
        details = f"{perfect}/{len(summary.rounds)} perfect | " + details
    layout.text(right, _MARGIN + 0.75, details, 14, ha="right")


def _draw_round(
    layout: _Layout,
    x: float,
    top: float,
    index: int,
    share_round: _ShareRound,
    mosaic: Image.Image,
    extras: str,
    show_number: bool,
) -> None:
    inner_width = _COL_WIDTH - 2 * _COL_PAD
    x_inner = x + _COL_PAD
    center = x + _COL_WIDTH / 2
    label = f"Kingdom {index + 1}" if show_number else "Kingdom"
    layout.text(center, top + 0.1, label, 15, ha="center")
    if share_round.name:
        layout.text(center, top + 0.38, share_round.name[:34], 10, ha="center")
    top += _LABEL_HEIGHT

    plot_ax = layout.add_axes(x_inner, top, inner_width, inner_width)
    plot_ax.imshow(_get_quality_plot_img(share_round))
    top += inner_width

    layout.text(
        center,
        top + 0.02,
        f"{share_round.score:g}/{MAX_ROUND_SCORE}   {_format_duration(share_round.elapsed_time)}",
        14,
        ha="center",
        bbox=_get_score_box(share_round.score, MAX_ROUND_SCORE)
        | {"linewidth": 1, "boxstyle": "round,pad=0.2"},
    )
    solution_buy = get_kingdom_solution(share_round.kingdom).buy_availability
    answer = share_round.buy_availability.capitalize()
    if get_buy_points(share_round.buy_availability, solution_buy) > 0:
        buy_text, buy_color = f"+Buy: {answer} - correct", "darkgreen"
    else:
        buy_text = f"+Buy: {answer} - actually {solution_buy.capitalize()}"
        buy_color = _USER_COLOR
    layout.text(center, top + 0.33, buy_text, 10, ha="center", color=buy_color)
    top += _SCORE_HEIGHT

    mosaic_height = inner_width * mosaic.height / mosaic.width
    mosaic_ax = layout.add_axes(x_inner, top, inner_width, mosaic_height)
    mosaic_ax.imshow(mosaic)
    if extras:
        layout.text(center, top + mosaic_height + 0.05, f"+ {extras}", 10, ha="center")


@lru_cache(maxsize=16)
def _render_share_png(summary: _ShareSummary) -> bytes:
    num_rounds = len(summary.rounds)
    # At least two columns wide, so that a single practice kingdom leaves room for
    # the header
    width = 2 * _MARGIN + max(num_rounds, 2) * _COL_WIDTH
    inner_width = _COL_WIDTH - 2 * _COL_PAD
    kingdoms = [Kingdom.from_dombot_csv_string(r.kingdom) for r in summary.rounds]
    mosaics = [_get_card_mosaic(k) for k in kingdoms]
    extras = [_get_extras_text(k) for k in kingdoms]
    mosaic_height = max(inner_width * m.height / m.width for m in mosaics)
    has_extras = any(extras)
    column_height = (
        _LABEL_HEIGHT
        + inner_width
        + _SCORE_HEIGHT
        + mosaic_height
        + (_EXTRAS_HEIGHT if has_extras else 0)
        + _COL_PAD
    )
    height = _HEADER_HEIGHT + column_height + _FOOTER_HEIGHT
    fig = plt.figure(figsize=(width, height), facecolor=_BG_COLOR)
    layout = _Layout(fig, width, height)
    _draw_header(layout, summary)

    first_x = (width - num_rounds * _COL_WIDTH) / 2
    for i, (share_round, mosaic, extra) in enumerate(
        zip(summary.rounds, mosaics, extras)
    ):
        x = first_x + i * _COL_WIDTH
        layout.add_panel(
            x + 0.05,
            _HEADER_HEIGHT,
            _COL_WIDTH - 0.1,
            column_height,
            facecolor=_PANEL_COLOR,
            edgecolor=DOM_BEIGE,
            linewidth=2,
        )
        _draw_round(
            layout, x, _HEADER_HEIGHT, i, share_round, mosaic, extra, num_rounds > 1
        )

    footer_top = _HEADER_HEIGHT + column_height + 0.08
    layout.text(
        _MARGIN,
        footer_top,
        f"{QUIZ_SHARE_URL} | v{get_version()} | {summary.date}",
        10,
        color="dimgray",
    )
    layout.text(
        width - _MARGIN,
        footer_top,
        "Red: your answers | Blue: solution",
        10,
        ha="right",
        color="dimgray",
    )
    return _fig_to_png(fig, dpi=_DPI, facecolor=_BG_COLOR)


def get_quiz_share_png(run_state: QuizRunState, player_name: str = "") -> bytes:
    """A PNG of the completed rounds of the run: settings, score, time, and per
    kingdom the plot of the answers vs. the solution and its cards.
    Cached, as rendering takes a few seconds for a full run."""
    return _render_share_png(_get_share_summary(run_state, player_name))
