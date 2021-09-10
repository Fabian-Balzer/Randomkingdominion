# -*- coding: utf-8 -*-
"""
Created on Thu Sep 02

@author: Fabian Balzer
Script for analyzing Data in a given stem path
"""


import pandas as pd
from Modules.GUI import start_program






    



def main():
    df = read_file()
    randomizerOptions = RandomizerOptions(sets=["Base", "Hinterlands"], all_sets=set(df["Set"]))
    k = create_kingdom(df, randomizerOptions)
    return df


if __name__ == "__main__":
    start_program()
    df = main()  # For me to inspect it in variable manager