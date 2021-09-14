"""Module for trying to find card info and write them to card_info"""


import json
import pandas as pd
import numpy as np
from collections import defaultdict




def main():
    fpath = "../card_info/good_card_data.csv"
    df = df = pd.read_csv(fpath, sep=";", header=0)
    df["DrawQuality"] = (2*pd.to_numeric(df["Cards"], errors='coerce')).fillna(0).astype(np.int64)
    pathbase = "../card_info/specifics/"
    with open(f"../card_info/specifics/DrawQuality.txt", "r") as f:
        data = json.load(f)
        data = defaultdict(lambda: 0, data)
    old_data = df[["Name", "DrawQuality"]].to_dict()
    old_data = {old_data["Name"][i]: old_data["DrawQuality"][i] for i in range(len(old_data["Name"]))}
    new_data = {name: max(data[name], old_data[name]) for name in sorted(old_data.keys())}
    print(new_data)
    with open(f"../card_info/specifics/DrawQuality.txt", "w") as f:
        json.dump(new_data, f)


if __name__ == '__main__':
    main()