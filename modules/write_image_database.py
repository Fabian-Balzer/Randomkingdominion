from bs4 import BeautifulSoup
import requests
import os


def write_image_database(df, dirname="card_pictures"):
    # answer = input(f"\nDo you want to scrape the Wiki to create an image database?\n"
    #     f"This may take some time. Please write (y) or cancel (n).\n>>> ")
    # while True:
    #     if answer is "n":
    #         print("Did not download an image database due to your concerns.")
    #         return
    #     if answer is "y":
    #         break
    #     answer = input("Please type y for creating an image db or n for cancelling.\n>>> ")
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    for set_ in set(df["Set"]):
        p = f"{dirname}/{set_.replace(', ', '_')}"
        if not os.path.exists(p):
            os.makedirs(p)
    nums = len(df)
    print("Starting to download pictures, this might take a while")
    impaths = []
    for i, card in df.iterrows():
        cname = card["Name"].replace(' ', '_')
        set_ = card["Set"].replace(', ', '_')
        impath = f"{dirname}/{set_}/{cname}.jpg"
        if not os.path.exists(impath):
            save_image(impath, cname)
        impaths.append(impath)
        if i % 50 == 0:
            print(f"Currently at {i} of {nums} cards ({cname})")
    df["ImagePath"] = impaths
    print("Card image database successfully written.")
    return df


def save_image(impath, card_name):
    """Search the wiki for the pic url of card_name and save a picture in
    impath"""
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
        print(f"No picture matching criteria could be found for {card_name}.")
        return
    with open(impath, "wb") as f:
        site = requests.get(pic_link)
        f.write(site.content)
