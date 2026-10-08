import pytest

from random_kingdominion.utils.data_setup.youtube_setup import download_yt_info
from random_kingdominion.utils.data_setup.youtube_setup import process_titles


@pytest.mark.parametrize(
    ("title", "expected_date"),
    [
        ("TGG Daily Dominion 2026/9/12", "2026-09-12"),
        ("TGG Daily Dominion 10/08/2026", "2026-10-08"),
    ],
)
def test_yudai_processor_accepts_both_date_formats(
    monkeypatch, title: str, expected_date: str
):
    monkeypatch.setattr(
        process_titles,
        "yml_load_entries",
        lambda _key: [{"id": "video-id", "title": title}],
    )

    result = process_titles.PROCESSOR_DICT["yudai_dailies"]()

    assert result == {expected_date: "video-id"}


def test_yudai_processor_ignores_non_daily_video_with_year(monkeypatch):
    monkeypatch.setattr(
        process_titles,
        "yml_load_entries",
        lambda _key: [
            {"id": "video-id", "title": "2026 Spending Summary: Google Gemini"}
        ],
    )

    result = process_titles.PROCESSOR_DICT["yudai_dailies"]()

    assert result == {}


def test_load_yt_info_skips_unavailable_entries(monkeypatch):
    saved_entries = []
    monkeypatch.setattr(download_yt_info, "yml_load_entries", lambda _key: [])
    monkeypatch.setattr(
        download_yt_info,
        "yml_save_entries",
        lambda entries, _key: saved_entries.extend(entries),
    )

    class FakeYoutubeDL:
        def __init__(self, _options):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def extract_info(self, _url, download):
            assert download is False
            return {
                "entries": [
                    None,
                    {"id": "available-id", "title": "TGG Daily Dominion 2026/10/08"},
                ]
            }

    monkeypatch.setattr(download_yt_info, "YoutubeDL", FakeYoutubeDL)

    entries = download_yt_info.load_yt_info(
        {
            "url": "https://youtube.com/playlist",
            "key": "test_playlist",
            "cols": ["id", "title"],
        }
    )

    assert len(entries) == 1
    assert entries[0]["id"] == "available-id"
    assert len(saved_entries) == 1


def test_youtubedl_private_video_errors_are_logged_at_debug(monkeypatch):
    debug_messages = []
    error_messages = []
    monkeypatch.setattr(download_yt_info.LOGGER, "debug", debug_messages.append)
    monkeypatch.setattr(download_yt_info.LOGGER, "error", error_messages.append)
    logger = download_yt_info._YoutubeDLLogger()

    logger.error("[youtube] video-id: Private video")
    logger.error("[youtube] video-id: Unexpected extractor failure")

    assert debug_messages == ["[youtube] video-id: Private video"]
    assert error_messages == ["[youtube] video-id: Unexpected extractor failure"]
