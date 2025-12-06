"""Quick script to dump the current campaign from the Dominion game profile XML file into a YAML
file.

Run this script with the path to your Dominion profile XML file as an argument
using
`python dump_current_campaign.py --file <path_to_your_profile_xml>`.
"""

import argparse
from pathlib import Path

import yaml


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Dump current campaign from Dominion profile XML."
    )
    parser.add_argument(
        "--file",
        type=str,
        default=r"C:\Users\fabia\AppData\Roaming\TempleGates\Dominion\profiles.xml",
        help="Path to the Dominion profile XML file.",
    )
    return parser.parse_args()


def parse_campaign_xml(xml: str) -> list[str]:
    """Parse the XML string to extract campaign information."""
    xml = xml.replace("\n", " ")
    xml = xml.replace("    ", "")
    xml = xml.replace("<campaignSetup>", "")
    xml = xml.replace("</campaignSetup>", "")
    xml = xml.replace("<campaignSetupMissions>", "")
    xml = xml.replace("</campaignSetupMissions>", "")
    xml = xml.replace("<campaignSetupMission>", "")
    xml = xml.replace("</campaignSetupMission>", "")
    entry_list = xml.split("-k ")
    entry_list = [x.strip() for x in entry_list]
    return entry_list


def dump_current_campaign(input_fpath: Path):
    """Dump the current campaign to a YAML file."""
    xml_text = input_fpath.read_text(encoding="utf-8")
    # Campaign stuff is between and <campaignSetup> <campaignResults>
    campaign_extract = xml_text.split("<campaignSetup>")[1].split("<campaignResults>")[
        0
    ]
    extra_text = parse_campaign_xml(campaign_extract)
    info = extra_text[0].split(", ")
    info_dict = {}
    info_dict["key"] = info[0].split("general:")[1]
    info_dict["num_themes"] = (
        1 if "one_theme" in info[1] else 2 if "two_theme" in info[1] else 3
    )
    info_dict["theme_1"] = info[2].split("theme_")[1]
    if info_dict["num_themes"] > 1:
        info_dict["theme_2"] = info[3].split("theme_")[1]
    info_dict["kingdoms"] = extra_text[1:]

    newpath = Path(__file__).parent.joinpath("data/new_kingdoms/campaign_dump.yml")
    with open(newpath, "r", encoding="utf-8") as f:
        previous = yaml.safe_load(f)
        if [x["key"] for x in previous].count(info_dict["key"]) > 0:
            print(f"{info_dict['key']} already in there, skipping")
        else:
            previous.append(info_dict)
            print(f"Adding {info_dict['key']}, now {len(previous)} in total")

            with open(newpath, "w", encoding="utf-8") as f:
                yaml.safe_dump(previous, f)


def main():
    args = parse_args()
    input_fpath = Path(args.file)
    if not input_fpath.exists():
        print(f"File {args.file} does not exist.")
        return
    dump_current_campaign(input_fpath)
    print("Campaign dumped successfully.")


if __name__ == "__main__":
    main()
