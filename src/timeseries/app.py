import io
import os
import sys
from pathlib import Path

# Streamlit runs this file as a standalone script, so the project root is not on
# sys.path. Add it so the `src` package is importable (No module named 'src' fix).
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import streamlit as st
from dotenv import load_dotenv

from src.db.migrations import apply_migrations
from src.etl.load import db_connect
from src.timeseries.decompose import DEFAULT_PERIOD, decompose_balance
from src.timeseries.extract import fetch_balance_series
from src.timeseries.plot import build_decomposition_figure

_ENV_FILE = Path(__file__).parent.parent.parent / "config" / ".env"

APP_TITLE = "Vektra - Data science for personal finance"


def _load_series():
    database_url = os.environ.get("DATABASE_URL", "")
    apply_migrations(database_url)
    conn = db_connect()
    try:
        return fetch_balance_series(conn)
    finally:
        conn.close()


def _render(series, period: int) -> None:
    if series.empty:
        st.warning("No daily balance data. Run the daily balance command first.")
        return
    if len(series) < 2 * period:
        st.warning(f"Need at least {2 * period} data points for a {period}-day decomposition.")
        return
    result = decompose_balance(series, period=period)
    fig = build_decomposition_figure(result)
    st.pyplot(fig)
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png")
    st.download_button("Download PNG", buffer.getvalue(), "decomposition.png", "image/png")


def main() -> None:
    st.set_page_config(page_title=APP_TITLE)
    load_dotenv(_ENV_FILE)
    st.title(APP_TITLE)
    period = st.sidebar.number_input("Seasonal period (days)", min_value=2, value=DEFAULT_PERIOD)
    _render(_load_series(), int(period))


if __name__ == "__main__":
    main()
