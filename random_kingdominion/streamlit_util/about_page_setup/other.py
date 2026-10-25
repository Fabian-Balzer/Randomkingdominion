import streamlit as st

from random_kingdominion.streamlit_util.quiz_setup.explanations import (
    QUIZ_FEEDBACK_VIDEO_URL,
)


def st_build_introduction_video_showcase():
    st.write(
        "Watch this video for an introduction to the features of this website!\\\nIt also provides a convenient venue to reach me for feedback or suggestions, just comment there."
    )
    _, container, _ = st.columns([20, 60, 20])
    with container:
        with st.container(border=True):
            st.video("https://youtu.be/1D8ivUHVUMw")

    st.write(
        "Another video, introducing the quiz and its features, can be found below:"
    )
    _, container, _ = st.columns([20, 60, 20])
    with container:
        with st.container(border=True):
            st.video(QUIZ_FEEDBACK_VIDEO_URL)
