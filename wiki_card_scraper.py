# %%
import requests
from bs4 import BeautifulSoup


def get_expansion_cards(expansion, type_):
    """Reads the data from the wiki page of the requested expansion and returns a list of the occuring cards."""
    wiki_url = f"http://wiki.dominionstrategy.com/index.php?title={expansion}&action=edit"
    response = requests.get(wiki_url)
    soup = BeautifulSoup(response.text, "html.parser")
    editable_text = soup.find(id="wpTextbox1").string
    card_list = []
    # The idea is to scan the editable text for bullet points:
    for line in editable_text.split("\n"):
        startstring = r"* {{Cost" if type_ == "Card" else "* "
        if line.startswith(startstring):
            # The first 12 characters denote the cost
            cut = 12 if type_ == "Card" else 2
            for word in line[cut:].split(","):
                if "|" in word and type_.lower() in word.lower():
                    card = word.split("|")[1].strip(r"}},")
                    # Filter out weird edge cases
                    if r"}}" not in card:
                        card_list.append(card)
    return list(dict.fromkeys(card_list))  # remove potential duplicates


def give_table_entry_card(card_name, expansion):
    """Returns a string corresponding to a table entry on http://wiki.dominionstrategy.com/index.php/List_of_cards."""
    wiki_url = f"http://wiki.dominionstrategy.com/index.php?title={card_name}&action=edit"
    response = requests.get(wiki_url)
    soup = BeautifulSoup(response.text, "html.parser")
    editable_text = str(soup.find(id="wpTextbox1").string)
    card_info = editable_text.split(r"{{Infobox Card")[1].split(r"\n\n")[0]
    info_dict = {line.split(" = ")[0].strip(" |"): line.split(
        " = ")[1] for line in card_info.split("\n") if len(line.split(" = ")) > 1}
    start = f"|-\n|{{{{Card|{info_dict['name']}}}}}"
    exp = f"[[{expansion}]]"
    types = ", ".join([info_dict[f"type{i}"]
                      for i in range(5) if f"type{i}" in info_dict])
    cost = f'data-sort-value="{info_dict["cost"]}" | {{{{Cost|{info_dict["cost"]}}}}}'
    # Insert hrule if the text has a below the line part
    text = '<hr style="width:60%;margin-left:20%;text-align:center;" />'.join([info_dict[f"text{i}"]
                                                                               for i in ["", "2"] if f"text{i}" in info_dict])
    total_string = " || ".join(
        [start, exp, types, cost, text]) + " || <!--Actions/Villagers--> || <!--Cards--> || <!--Buys--> || <!--Coins/Coffers--> || <!--Trash/Return--> || <!--Exile--> || <!--Junk--> || <!--Gain--> ||<!--VP Points--> \n"
    return total_string


def give_table_entry_ally(ally_name):
    """Returns a string corresponding to a table entry on http://wiki.dominionstrategy.com/index.php/List_of_cards."""
    wiki_url = f"http://wiki.dominionstrategy.com/index.php?title={ally_name}&action=edit"
    response = requests.get(wiki_url)
    soup = BeautifulSoup(response.text, "html.parser")
    editable_text = str(soup.find(id="wpTextbox1").string)
    card_info = editable_text.split(r"{{Infobox Ally")[1].split(r"\n\n")[0]
    info_dict = {line.split(" = ")[0].strip(" |"): line.split(
        " = ")[1] for line in card_info.split("\n") if len(line.split(" = ")) > 1}
    start = f"|-\n|{{{{Ally|{info_dict['name']}}}}}"
    exp = "[[Allies]]"
    types = "Ally"
    text = info_dict["text"]
    total_string = " || ".join(
        [start, exp, types, "", text]) + " || <!--Actions/Villagers--> || <!--Cards--> || <!--Buys--> || <!--Coins/Coffers--> || <!--Trash/Return--> || <!--Exile--> || <!--Junk--> || <!--Gain--> ||<!--VP Points--> \n"
    return total_string


if __name__ == "__main__":
    expansion = "Allies"
    # If we want to search for only Cards, Allies, Events or whatever
    type_ = "Card"
    cards = get_expansion_cards(expansion, type_)
    print(cards)
    s = ""
    for card in cards:
        try:
            if type_ == "Card":
                s += give_table_entry_card(card, expansion)
            if type_ == "Ally":
                s += give_table_entry_ally(card)
        except IndexError:
            print(f"Could not find a proper article for {card}")
    print(s)
    # This can of course be written to a txt file.


# Reference:
"""
|-
|{{Card | Prince}} | | [[Promo]] | | Action | | data - sort - value = "8" | {{Cost | 8}} | | You may set this aside. If you do, set aside an Action card from your hand costing up to {{Cost | 4}}. At the start of each of your turns, play that Action, setting it aside again when you discard it from play. (Stop playing it if you fail to set it aside on a turn you play it.) | | data - sort - value = "+6" | N... P1 | | | | | | | | | | | | | | | |
"""
