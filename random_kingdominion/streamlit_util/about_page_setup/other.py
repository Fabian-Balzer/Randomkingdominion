import streamlit as st


def st_build_introduction_video_showcase():
    st.write(
        "Watch this video for an introduction to the features of this website!\\\nIt also provides a convenient venue to reach me for feedback or suggestions, just comment there."
    )
    _, container, _ = st.columns([20, 60, 20])
    with container:
        with st.container(border=True):
            st.video("https://youtu.be/1D8ivUHVUMw")
