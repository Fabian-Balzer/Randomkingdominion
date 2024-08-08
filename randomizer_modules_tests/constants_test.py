"""Tests for the constants.py file."""

import random_kingdominion as rk


def test_filenames():
    for fname in [rk.FPATH_CARD_DATA, rk.FPATH_RAW_DATA]:
        assert fname.is_file()


def test_filepaths():
    for fpath in [
        rk.PATH_ASSETS,
        rk.PATH_CARD_INFO,
        rk.PATH_CARD_PICS,
        rk.PATH_MAIN,
        rk.PATH_MODULE,
    ]:
        assert fpath.is_dir()
