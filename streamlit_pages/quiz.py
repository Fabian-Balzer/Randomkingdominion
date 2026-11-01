import random_kingdominion.streamlit_util as rks

rks.build_page_header(
    "Dominion Kingdom Engine Qualities Quiz",
    (
        "Test your knowledge of Dominion by trying to infer the engine qualities for a given kingdom. I highly recommend to read the instructions first."
    ),
    "Learn more about the CSO and kingdom qualities on the about page.",
)
rks.st_build_full_quiz_display()
