import logging
import warnings

from .constants import *
from .cso_frame_utils import *
from .cso_series_utils import *
from .kingdom import Kingdom, KingdomManager, KingdomRandomizer
from .logger import LOGGER
from .utils import *


# Custom logging filter to ignore specific Streamlit warning
class StreamlitFilter(logging.Filter):
    def filter(self, record):
        ignored_messages = [
            "Thread 'MainThread': missing ScriptRunContext!",
            "No runtime found, using MemoryCacheStorageManager",
            "Session state does not function when running a script without `streamlit run`",
            "to view this Streamlit app on a browser,",
            "missing ScriptRunContext! This warning can be ignored when running in bare mode.",
        ]
        return all([message not in record.getMessage() for message in ignored_messages])


def _remove_streamlit_logs():
    # Configure logging to include the logger's name
    formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    # Get the Streamlit logger and add the custom filter and handler
    for log_key in [
        "scriptrunner_utils.script_run_context",
        "caching.cache_data_api",
        "state.session_state_proxy",
        "scriptrunner",
    ]:
        streamlit_logger = logging.getLogger(f"streamlit.runtime.{log_key}")
        streamlit_logger.addFilter(StreamlitFilter())
    streamlit_logger = logging.getLogger("streamlit")
    streamlit_logger.addFilter(StreamlitFilter())


# from .streamlit_util import *

try:
    _remove_streamlit_logs()
    from .streamlit_util import *


except ImportError as e:
    LOGGER.warning(f"Couldn't locate valid streamlit installation ({e})")

try:
    from .widgets import *
except ImportError as e:
    # LOGGER.warning(f"Couldn't locate valid PyQt installation ({e})")
    pass
