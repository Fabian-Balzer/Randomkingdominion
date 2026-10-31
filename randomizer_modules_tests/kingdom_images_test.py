"""The cached card images (M8) must look exactly like the composed ones."""

import pytest
from PIL import Image

import random_kingdominion as rk
from random_kingdominion.streamlit_util.common_widgets.kingdom_display import (
    kingdom_as_images as images,
)
from random_kingdominion.streamlit_util.image_util import img_to_html

# Between them, every kind of overlay that get_cso_display_image draws
_KINGDOMS_WITH_OVERLAYS = [
    "young_witch(moat), ferryman(cellar), obelisk(village), approaching_army(militia),"
    " way_of_the_mouse(harbinger), smithy, chapel, market, festival, library,"
    " nearby(market)",
    "riverboat(laboratory), druid(the_moons_gift, the_suns_gift, the_mountains_gift),"
    " village, smithy, chapel, militia, witch, festival, library",
]


def _same_image(a: Image.Image, b: Image.Image) -> bool:
    return a.size == b.size and a.tobytes() == b.tobytes()


@pytest.mark.parametrize("dombot_str", _KINGDOMS_WITH_OVERLAYS)
def test_overlays_are_detected_exactly_where_they_are_drawn(dombot_str: str):
    """has_kingdom_overlay decides which images may come from the cache; a CSO
    without an overlay has to look as it does in any other kingdom."""
    kingdom = rk.Kingdom.from_dombot_csv_string(dombot_str)
    assert kingdom.notes == ""
    empty = rk.Kingdom([])
    num_overlays = 0
    for cso_key in kingdom.cards + kingdom.landscapes:
        cso = rk.ALL_CACHED_CSOS.loc[cso_key]
        with_kingdom = images.get_cso_display_image(cso, kingdom)
        unchanged = _same_image(with_kingdom, images.get_cso_display_image(cso, empty))
        has_overlay = images.has_kingdom_overlay(cso_key, kingdom)
        assert unchanged != has_overlay, cso_key
        num_overlays += has_overlay
    assert num_overlays >= 2, "the kingdom should exercise some overlays"


@pytest.mark.parametrize(
    "cso_key, full_image, hide_landscape_text",
    [
        ("village", False, False),
        ("village", True, False),
        ("training", False, False),
        ("training", False, True),
    ],
)
def test_cached_image_equals_the_composed_one(
    cso_key: str, full_image: bool, hide_landscape_text: bool
):
    cso = rk.ALL_CACHED_CSOS.loc[cso_key]
    kingdom = rk.Kingdom(["village", "smithy"], landscapes=["training"])
    composed = images.get_cso_display_image(
        cso, kingdom, full_image, hide_landscape_text
    )
    cached = images._get_cso_image_html(cso, kingdom, full_image, hide_landscape_text)
    assert cached == img_to_html(composed)


def test_images_are_composed_once_per_distinct_look(monkeypatch):
    """Flags that don't change an image (full_image for landscapes, which are always
    shown in full; hide_landscape_text for cards) mustn't split the cache entries,
    and kingdoms without overlays on a CSO share its entry."""
    composed = []
    compose = images.get_cso_display_image

    def counting_compose(cso, *args, **kwargs):
        composed.append(cso.name)
        return compose(cso, *args, **kwargs)

    monkeypatch.setattr(images, "get_cso_display_image", counting_compose)
    images.get_cso_image_html_without_overlays.clear()
    for kingdom in [
        rk.Kingdom(["village"], landscapes=["training"]),
        rk.Kingdom(["village", "smithy"], landscapes=["training", "alms"]),
    ]:
        for key in ["village", "training"]:
            for full_image in (False, True):
                for hide_text in (False, True):
                    cso = rk.ALL_CACHED_CSOS.loc[key]
                    images._get_cso_image_html(cso, kingdom, full_image, hide_text)
    # Village cropped and in full, Training with and without its text
    assert sorted(composed) == ["training", "training", "village", "village"]
