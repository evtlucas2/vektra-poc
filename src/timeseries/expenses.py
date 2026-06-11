import pandas as pd

EXPENSE_PERCENTILE = 5  # the most-extreme 5% of daily changes (highest expenses)


def top_expense_days(df: pd.DataFrame, percentile: int = EXPENSE_PERCENTILE) -> pd.DataFrame:
    """Select the highest-expense days from a daily_balance frame.

    A day's expense is a negative `difference`. Returns the days whose `difference` is at or
    below the `percentile`-th percentile of all daily changes (and is negative), with an added
    positive `expense` column, sorted by expense descending. Empty input -> empty output.
    """
    if df.empty:
        return df.assign(expense=pd.Series(dtype=float))
    threshold = df["difference"].quantile(percentile / 100)
    selected = df[(df["difference"] <= threshold) & (df["difference"] < 0)].copy()
    selected["expense"] = -selected["difference"]
    return selected.sort_values("difference", ascending=True).reset_index(drop=True)
