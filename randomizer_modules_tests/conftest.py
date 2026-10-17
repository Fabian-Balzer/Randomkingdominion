import matplotlib

# `streamlit run` switches to the non-interactive Agg backend by itself. The tests
# have to do the same, since AppTest draws figures outside of the main thread,
# which crashes interactive backends such as Qt.
matplotlib.use("Agg")
