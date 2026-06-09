from matplotlib.figure import Figure
from statsmodels.tsa.seasonal import DecomposeResult

_PANELS = ("Observed", "Trend", "Seasonal", "Residual")


def build_decomposition_figure(result: DecomposeResult) -> Figure:
    """Build a 4-panel, date-aligned decomposition figure (observed/trend/seasonal/residual)."""
    components = (result.observed, result.trend, result.seasonal, result.resid)
    fig = Figure(figsize=(10, 8))
    axes = fig.subplots(4, 1, sharex=True)
    for ax, label, data in zip(axes, _PANELS, components):
        ax.plot(data.index, data.values)
        ax.set_ylabel(label)
    axes[0].set_title("Daily Balance Decomposition")
    fig.tight_layout()
    return fig
