"""Shared test setup.

Running the tests:
    python -m pytest randomizer_modules_tests                 # everything (~1.5 min)
    python -m pytest randomizer_modules_tests -m "not slow"   # fast part (~25 s)
    python -m pytest randomizer_modules_tests -m slow         # only the page tests

Pitfalls when writing page tests with Streamlit's AppTest:
- Mark them as slow (`pytestmark = pytest.mark.slow`): each page run takes seconds.
- matplotlib has to use the Agg backend (done below). Otherwise the test process
  dies silently (exit code 127) as soon as a page draws a figure.
- `.streamlit/config.toml` enforces picklable session state, and AppTest stores widget
  metadata in it. Lambdas as `on_click`/`on_change`/`format_func` therefore make
  AppTest fail ("Cannot serialize ... $$STREAMLIT_INTERNAL_KEY_TESTING"); use
  module-level functions or `functools.partial`. The same happens when running the
  app through `RandomKingdominion.py` (navigation), so test pages directly.
- AppTest always reruns the whole script, never just a fragment or dialog. A button
  inside an `st.dialog` is therefore only rendered while the dialog is open, and its
  click is lost on the rerun; let such buttons act in an `on_click` callback.
- After an `st.rerun()`, AppTest keeps the elements of the interrupted run in its
  tree (e.g. the quiz's start screen next to the first round) and sends their state
  with the next run. Callbacks of buttons that aren't rendered anymore then fire
  (their `False` differs from the removed old state). Handle clicks on such screens
  inline (`if st.button(...)`) instead of in `on_click`.
- AppTest can't deselect a segmented control (`set_value(None)` is ignored); emulate
  it by changing session state the way the widget's callback would.
- Popovers are generic blocks in AppTest; read their label via `.proto.popover.label`.
"""

import matplotlib

# `streamlit run` switches to the non-interactive Agg backend by itself. The tests
# have to do the same, since AppTest draws figures outside of the main thread,
# which crashes interactive backends such as Qt.
matplotlib.use("Agg")
