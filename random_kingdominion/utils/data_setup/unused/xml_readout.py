"""This file contains a script that I used to extract all of my saved kingdoms. Might be of use to someone in the future so I kept the script here.
"""

import xml.etree.ElementTree as ET
from pathlib import Path

from ....kingdom import Kingdom, KingdomManager


def load_own_saved_kingdoms_from_xml(
    fpath: Path = Path.home().joinpath(
        "AppData/Roaming/TempleGates/Dominion/profiles.xml"
    ),
):
    # 1) Load the setlist from my TGG Dominion profile
    with fpath.open("r") as f:
        xml_str = f.read()

    root = ET.fromstring(xml_str)
    saved_set_xml = root.find("profiles").find("saveSets")  # type: ignore

    # Initialize an empty list to store the sets as small dictionaries, and iterate over it
    sets_list = []
    for set_elem in saved_set_xml.findall("sets"):  # type: ignore
        # Extract the name and strKingdom
        name = set_elem.find("name").text  # type: ignore
        str_kingdom = set_elem.find("strKingdom").text  # type: ignore
        sets_list.append({"name": name, "strKingdom": str_kingdom})

    # This is enough to get a dictionary with all owned kingdoms.

    # 2) Load all previously saved custom sets, so we don't overwrite them:
    fabi_recset_manager = KingdomManager()
    fabi_recset_manager.load_fabi_recsets_kingdoms()
    for set_dict in sets_list:
        name = set_dict["name"]
        if name in [k["name"] for k in fabi_recset_manager.kingdoms]:
            continue
        kingdom_str = set_dict["strKingdom"].replace("-m", ", ").replace("-k", ", ")
        try:
            k = Kingdom.from_dombot_csv_string(kingdom_str, name=set_dict["name"])
        except ValueError as e:
            print(e)
            print(kingdom_str)
            continue
        if k.notes != "":
            print(k.name)
            print(k.notes)
            k.notes = ""
        fabi_recset_manager.add_kingdom(k, try_save=False)
