import random_kingdominion.streamlit_util as rks

rks.build_page_header(
    "Dominion Kingdom Oracle",
    (
        "This page allows you to easily input a kingdom to visualize its engine qualities "
        "and take a more detailed look on its Card-Shaped Objects (CSOs). "
        "The resulting plot also shows any extra components you'd need to set up the kingdom in its physical form."
    ),
    "Learn more about the CSO and kingdom qualities on the 'About' page.",
)

rks.st_build_existing_kingdom_select()

k = rks.st_build_oracle_kingdom_input_display()

rks.st_build_oracle_kingdom_display(k)
