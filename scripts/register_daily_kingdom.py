"""Register the Daily Kingdom."""

import argparse

import random_kingdominion.scripting as rks


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--kingdom_string",
        type=str,
        help="The string representing the kingdom.",
    )
    parser.add_argument(
        "--date",
        "-d",
        type=str,
        required=False,
        help="The date for the Daily Kingdom in YYYY-MM-DD format.",
    )
    parser.add_argument(
        "-y",
        "--youtube-setup",
        action="store_true",
        help="Create youtube setup things within the kingdom manager.",
    )
    parser.add_argument(
        "-p",
        "--plot",
        action="store_true",
        help="Generate and show a plot of the registered kingdom.",
    )
    parser.add_argument(
        "--replace",
        "-r",
        action="store_true",
        help="Replace the existing kingdom for the given date if it exists.",
    )
    parser.add_argument(
        "--validate",
        "-v",
        action="store_true",
        default=True,
        help="Validate of the kingdom string.",
    )
    args = parser.parse_args()
    rks.log_args(args, __file__, parser=parser)
    return args


def main():
    args = parse_args()
    manager = None
    if args.kingdom_string is not None:
        manager = rks.register_daily_kingdom(
            args.kingdom_string,
            args.date,
            replace=args.replace,
            validate=args.validate,
        )
    if args.youtube_setup:
        rks.set_up_daily_video_assets(args.date, manager)
    if args.plot:
        rks.plot_daily_kingdom(args.date, manager)


if __name__ == "__main__":
    main()
