# Data Model: Dark Mode Theme and Vektra App Title

**Branch**: `006-dark-theme-app-title` | **Date**: 2026-06-10

## No Data Entities

This feature is presentation-only. It introduces **no database tables, columns, migrations,
or in-memory data entities**. It changes how the existing application looks (forced dark
theme) and its title text.

## Configuration Artifacts (not data)

| Artifact | Purpose |
|----------|---------|
| `.streamlit/config.toml` `[theme] base="dark"` | Forces dark appearance on load |
| `.streamlit/config.toml` `[client] toolbarMode="minimal"` | Hides the menu (no light-mode switch) |
| `app.py` `APP_TITLE` constant | Single source for the heading and the browser-tab title |

No reads or writes to `transactions`, `daily_balance`, or any other table are added or
changed.
