import argparse


import sys
from .logger import LOGGER


def start_gui():
    """A function to include everything needed to start the application"""
    # Check whether there is already a running QApplication (e.g. if running
    # from an IDE). This setup prevents crashes for the next run:

    import PyQt5.QtWidgets as QW  # type: ignore
    from .widgets import UIMainWindow

    qapp = QW.QApplication.instance()
    if not qapp:
        qapp = QW.QApplication(sys.argv)
    app = UIMainWindow()  # creating the instance
    app.show()
    app.activateWindow()
    qapp.exec_()  # Start the Qt event loop


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Start the application using `python -m random_kingdominion`."
    )
    parser.add_argument(
        "-g",
        "--run_gui",
        action="store_true",
        help="Whether to start the gui.",
    )
    return parser.parse_args()


def main() -> None:
    """Start the application."""
    args = parse_args()
    if args.run_gui:
        start_gui()
    else:
        LOGGER.info(
            "Started in non-gui-mode, which isn't implemented yet. Try using the -g flag."
        )


if __name__ == "__main__":
    main()
