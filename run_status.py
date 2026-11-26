from contextlib import contextmanager
from html import escape

import streamlit as st


@contextmanager
def running(message):
    slot = st.empty()
    slot.markdown(
        '<div role="status" class="run-status"><span aria-hidden="true">🔥</span>'
        f'{escape(message)}</div>', unsafe_allow_html=True)
    try:
        yield
    finally:
        slot.empty()
