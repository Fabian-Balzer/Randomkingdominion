import argparse

import random_kingdominion as rk
from random_kingdominion.scripting import log_args


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--campaign_name",
        type=str,
        help="The name of the campaign to set the kingdom for.",
    )
    args = parser.parse_args()
    log_args(args, __file__, parser=parser)
    return args


def main():
    args = parse_args()
    manager = rk.KingdomManager()
    manager.load_campaigns(reload=True, do_assertion=False)
    k: rk.Kingdom = manager.get_kingdom_by_name(args.campaign_name)  # type: ignore
    p = rk.PATH_ASSETS.joinpath("other/youtube/campaigns/current_caption.txt")
    p.write_text(f"Dominion Campaigns: {k.name}")
    rk.create_thumbnail(k, "Dominion Campaigns")
    print("Dombot kingdom string: ")
    print(k.get_dombot_csv_string())
    print("Expansions:")
    print(", ".join(k.expansions))


if __name__ == "__main__":
    main()
