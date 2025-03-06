from .add_split_piles import add_split_piles
from .add_campaign_effects import add_campaign_effects


def add_additional_entries(df):
    """Add additional entries (i.e. split piles) to the dataframe which are not part of the wiki."""
    df = add_split_piles(df)
    df = add_campaign_effects(df)
    return df
