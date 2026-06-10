# Contract: UI Appearance

**Feature**: Dark Mode Theme and Vektra App Title | **Date**: 2026-06-10

## Theme Contract

| Property | Required value |
|----------|----------------|
| Appearance on load | Dark (dark background, light text) |
| Follows system theme | No — always dark |
| Light-mode switch exposed | No |

Delivered by `.streamlit/config.toml`:

```toml
[theme]
base = "dark"

[client]
toolbarMode = "minimal"
```

## Title Contract

| Surface | Required text |
|---------|---------------|
| In-app main heading | `Vektra - Data science for personal finance` |
| Browser tab / window title | `Vektra - Data science for personal finance` |

Delivered in `src/timeseries/app.py`:

```python
APP_TITLE = "Vektra - Data science for personal finance"
# first Streamlit call:
st.set_page_config(page_title=APP_TITLE)
...
st.title(APP_TITLE)
```

## Testable Surface (no Streamlit runtime required)

```python
# app.py exposes:
APP_TITLE == "Vektra - Data science for personal finance"

# .streamlit/config.toml contains:
[theme] base == "dark"
```

## Manual Verification (visual)

- With the host OS set to light mode, the app still loads dark.
- The browser tab and the heading both read "Vektra - Data science for personal finance".
- No theme switcher is reachable in the UI.
