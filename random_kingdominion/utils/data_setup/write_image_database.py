import os

import requests
from ...constants import PATH_CARD_PICS
from pathlib import Path


def write_image_database(df):
    if not PATH_CARD_PICS.exists():
        PATH_CARD_PICS.mkdir()
    for exp in set(df["Expansion"]):
        p = PATH_CARD_PICS.joinpath(exp)
        if not p.exists():
            p.mkdir()
    nums = len(df)
    print("Starting to download pictures, this might take a while")
    impaths = []
    for i, card in df.iterrows():
        cname = card["Name"].replace(" ", "_")
        exp = card["Expansion"].replace(", ", "_")
        impathname = f"{exp}/{cname}.jpg"
        impath = PATH_CARD_PICS.joinpath(impathname)
        if not impath.exists():
            save_image(impath, cname)
        impaths.append(impathname)
        if i % 50 == 0:
            print(f"Currently at {i} of {nums} cards ({cname})")
    df["ImagePath"] = impaths
    print("Card image database successfully written.")
    return df


def save_image(impath: Path, card_name):
    """Search the wiki for the pic url of card_name and save a picture in
    impath.
    """
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print(
            "BeautifulSoup is not installed. Please install it with 'pip install beautifulsoup4'."
        )
        return
    link_base = "http://wiki.dominionstrategy.com"
    sitename = link_base + f"/index.php/File:{card_name}.jpg"
    response = requests.get(sitename)
    soup = BeautifulSoup(response.text, "html.parser")
    ims = soup.find_all("img")
    pic_link = None
    for im in ims:
        # Find an image with a resolution between 300 and 1000, starting with
        # the lowest. This is probably pretty inefficient.
        for i in range(300, 1000):
            if card_name and f"{i}px" in im["src"]:
                pic_link = link_base + im["src"]
                break
    if pic_link is None:
        for im in ims:
            if card_name in im["src"]:
                pic_link = link_base + im["src"]
                print(f"Reverting to alternative link for {card_name}")
                break
    if pic_link is None:
        print(f"No picture matching criteria could be found for {card_name}.")
        return
    with open(impath, "wb") as f:
        site = requests.get(pic_link)
        f.write(site.content)


def download_icons():
    """Function to download images from the card symbols page"""
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print(
            "BeautifulSoup is not installed. Please install it with 'pip install beautifulsoup4'."
        )
        return
    sitename = "http://wiki.dominionstrategy.com/index.php/Category:Card_symbols"
    response = requests.get(sitename)

    soup = BeautifulSoup(response.text, "html.parser")
    link_base = "http://wiki.dominionstrategy.com"
    ims = soup.find_all("img")
    dirname = "assets/icons/"
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    for image in ims:
        impath = dirname + image["src"].split("/")[-1]
        print(f'Downloading {image["src"].split("/")[-1]}')
        pic_link = link_base + image["src"]
        if not os.path.exists(impath):
            with open(impath, "wb") as f:
                site = requests.get(pic_link)
                f.write(site.content)
        # cname = card["Name"].replace(' ', '_')
        # set_ = card["Expansion"].replace(', ', '_')
        # impath = f"{dirname}/{set_}/{cname}.jpg"
        # if not os.path.exists(impath):
        #     save_image(impath, cname)
        # impaths.append(impath)
        # if i % 50 == 0:
        #     print(f"Currently at {i} of {nums} cards ({cname})")
