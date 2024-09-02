from .add_amount_info import add_amount_info
from .add_bool_columns import add_bool_columns
from .add_extra_components import add_extra_components
from .add_parent_column import add_parent_column
from .add_quality_info import add_quality_info


def add_additional_info_columns(df):
    """Adds additional columns to the given dataframe."""
    df = add_parent_column(df)
    df = add_bool_columns(df)
    df = add_quality_info(df)
    df = add_amount_info(df)
    link_base = "https://wiki.dominionstrategy.com/index.php/"
    df["WikiLink"] = df["Name"].str.replace(" ", "_").apply(lambda x: link_base + x)
    df = add_extra_components(df)
    return df
