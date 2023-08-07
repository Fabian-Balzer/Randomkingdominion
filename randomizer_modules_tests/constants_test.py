"""Tests for the constants.py file."""
import randomizer_modules as rm


def test_filenames():
    for fname in [rm.FPATH_CARD_DATA, rm.FPATH_RAW_DATA]:
        assert fname.is_file()


def test_filepaths():
    for fpath in [
        rm.PATH_ASSETS,
        rm.PATH_CARD_INFO,
        rm.PATH_CARD_PICS,
        rm.PATH_MAIN,
        rm.PATH_MODULE,
    ]:
        assert fpath.is_dir()
