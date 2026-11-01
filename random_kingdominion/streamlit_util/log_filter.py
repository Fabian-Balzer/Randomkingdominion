import logging


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


def remove_streamlit_logs():
    """Silence the warnings Streamlit emits when this layer is imported outside of
    `streamlit run` (e.g. in tests), where the module-level `st.cache_data` calls run
    without a runtime."""
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
