# Quickstart: Dark Mode Theme and Vektra App Title

**Branch**: `006-dark-theme-app-title` | **Date**: 2026-06-10

## What Changed

- The app now always renders in **dark mode**, regardless of your system theme.
- The toolbar menu is hidden, so there is no light-mode switch.
- The title (browser tab and in-app heading) is now
  **"Vektra - Data science for personal finance"**.

## Files

- `.streamlit/config.toml` (new) — forces the dark theme and minimal toolbar.
- `src/timeseries/app.py` — `APP_TITLE` constant + `st.set_page_config(page_title=APP_TITLE)`.

## Launching

```bash
streamlit run src/timeseries/app.py
```

Run from the project root so `.streamlit/config.toml` is picked up.

## Automated Validation (no browser)

```bash
pytest tests/unit/test_app_appearance.py -v
```

Checks:
- `app.APP_TITLE == "Vektra - Data science for personal finance"`
- `.streamlit/config.toml` exists and sets `base = "dark"`

## Manual Validation (visual)

1. Set your operating system to **light mode**.
2. Launch the app and open it in the browser.
3. Confirm:
   - The interface is **dark** (dark background, light text) on first load.
   - The **browser tab** reads "Vektra - Data science for personal finance".
   - The **main heading** reads "Vektra - Data science for personal finance".
   - There is **no** visible control to switch to light mode.

## Reference

- UI contract: [contracts/ui-appearance.md](contracts/ui-appearance.md)
- Research/decisions: [research.md](research.md)
