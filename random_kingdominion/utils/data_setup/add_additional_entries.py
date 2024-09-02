from .add_split_piles import add_split_piles


def add_additional_entries(df):
    """Add additional entries (i.e. split piles) to the dataframe which are not part of the wiki."""
    df = add_split_piles(df)
    return df
