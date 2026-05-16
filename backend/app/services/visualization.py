"""
Visualization Module for Backtest Results.

Generates 2-panel matplotlib charts showing:
- Panel 1: Price chart with cluster background colors and trade markers
- Panel 2: Equity curve with drawdown shading and annotations
"""

import matplotlib
matplotlib.use('Agg')  # Must be before any other matplotlib imports — prevents display issues in server environments

import os
import glob
from datetime import datetime

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd


# Cluster color map — supports both new Indonesian labels and old English aliases
CLUSTER_COLORS = {
    # New labels (primary)
    "Beli Saat Turun": "#00FFB2",
    "Momentum": "#3B82F6",
    "Konsolidasi": "#F59E0B",
    "High Risk": "#EF4444",
    # Old labels (backward-compat aliases)
    "Buy the Dip": "#00FFB2",
    "Trending / Momentum": "#3B82F6",
    "Hold / Sideways": "#F59E0B",
    "High Risk / Avoid": "#EF4444",
}

# Fallback color for unknown labels
_DEFAULT_COLOR = "#CCCCCC"


def visualize_backtest_results(
    ticker: str,
    df: pd.DataFrame,
    cluster_timeline: dict,
    trades: list,
    equity_curve: list,
    output_path: str,
) -> str:
    """
    Generate comprehensive backtest visualization and save as PNG.

    Creates a 2-panel figure:
    - Panel 1 (top, 2/3 height): Price chart with colored cluster backgrounds,
      price line, and trade entry/exit markers.
    - Panel 2 (bottom, 1/3 height): Equity curve with drawdown shading,
      peak/max-drawdown markers, and final equity annotation.

    Args:
        ticker: Stock ticker symbol (used in chart title).
        df: OHLCV DataFrame with DatetimeIndex.
        cluster_timeline: Mapping of date string (YYYY-MM-DD) -> cluster label.
        trades: List of trade dicts (see TradeRecord in design.md).
                May be empty — handled gracefully.
        equity_curve: List of equity snapshots [{date, equity, position}, ...].
        output_path: Absolute or relative path where the PNG will be saved.

    Returns:
        The output_path string (same value passed in).
    """
    fig, (ax1, ax2) = plt.subplots(
        2, 1,
        figsize=(16, 10),
        gridspec_kw={"height_ratios": [2, 1]},
    )

    # ------------------------------------------------------------------ #
    # Panel 1 — Price chart                                               #
    # ------------------------------------------------------------------ #
    dates = df.index
    prices = df["Close"].values

    # Draw colored background spans per cluster label
    for i in range(len(dates) - 1):
        date_str = str(dates[i].date())
        label = cluster_timeline.get(date_str, "Konsolidasi")
        color = CLUSTER_COLORS.get(label, _DEFAULT_COLOR)
        ax1.axvspan(dates[i], dates[i + 1], facecolor=color, alpha=0.2, zorder=0)

    # Price line
    ax1.plot(dates, prices, color="black", linewidth=1.5, zorder=2, label="_nolegend_")

    # Trade markers — only when trades list is non-empty
    for trade in trades:
        entry_date = pd.to_datetime(trade["entry_date"])
        exit_date = pd.to_datetime(trade["exit_date"])
        entry_price = trade["entry_price"]
        exit_price = trade["exit_price"]

        # Buy marker: green triangle up
        ax1.scatter(
            entry_date, entry_price,
            marker="^", color="green", s=100, zorder=3,
        )

        # Determine exit marker type based on exit reason
        stop_loss_hit = trade.get("stop_loss_triggered", False)
        trailing_stop_hit = trade.get("trailing_stop_triggered", False)

        if stop_loss_hit:
            # Stop loss: red X
            ax1.scatter(
                exit_date, exit_price,
                marker="x", color="red", s=150, zorder=4,
            )
        elif trailing_stop_hit:
            # Trailing stop: orange X
            ax1.scatter(
                exit_date, exit_price,
                marker="x", color="orange", s=150, zorder=4,
            )
        else:
            # Normal sell: red triangle down
            ax1.scatter(
                exit_date, exit_price,
                marker="v", color="red", s=100, zorder=3,
            )

    ax1.set_title(
        f"{ticker} — Backtest Results (6 Months)",
        fontsize=14, fontweight="bold",
    )
    ax1.set_ylabel("Price (IDR)", fontsize=12)
    ax1.grid(True, alpha=0.3)

    # Legend for cluster colors
    legend_handles = [
        mpatches.Patch(facecolor="#00FFB2", alpha=0.5, label="Beli Saat Turun"),
        mpatches.Patch(facecolor="#3B82F6", alpha=0.5, label="Momentum"),
        mpatches.Patch(facecolor="#F59E0B", alpha=0.5, label="Konsolidasi"),
        mpatches.Patch(facecolor="#EF4444", alpha=0.5, label="High Risk"),
    ]
    ax1.legend(handles=legend_handles, loc="upper left", fontsize=9)

    # ------------------------------------------------------------------ #
    # Panel 2 — Equity curve                                              #
    # ------------------------------------------------------------------ #
    if equity_curve:
        eq_dates = [pd.to_datetime(e["date"]) for e in equity_curve]
        eq_values = [e["equity"] for e in equity_curve]
        initial_equity = eq_values[0]

        # Equity line
        ax2.plot(eq_dates, eq_values, color="blue", linewidth=2, label="Equity")

        # Drawdown shading: fill red where equity < initial equity
        ax2.fill_between(
            eq_dates,
            eq_values,
            initial_equity,
            where=[v < initial_equity for v in eq_values],
            color="red",
            alpha=0.3,
            label="Drawdown",
        )

        # Peak equity marker (green dot)
        peak_equity = max(eq_values)
        peak_idx = eq_values.index(peak_equity)
        ax2.scatter(
            eq_dates[peak_idx], peak_equity,
            color="green", s=100, zorder=3, label=f"Peak: {peak_equity:,.0f}",
        )

        # Max drawdown point marker (red dot)
        # Find the point with the deepest drawdown relative to running peak
        running_peak = initial_equity
        max_dd = 0.0
        max_dd_idx = 0
        for idx, val in enumerate(eq_values):
            if val > running_peak:
                running_peak = val
            dd = (running_peak - val) / running_peak if running_peak > 0 else 0.0
            if dd > max_dd:
                max_dd = dd
                max_dd_idx = idx

        ax2.scatter(
            eq_dates[max_dd_idx], eq_values[max_dd_idx],
            color="red", s=100, zorder=3,
            label=f"Max DD: {max_dd * 100:.1f}%",
        )

        # Final equity annotation as text box
        final_equity = eq_values[-1]
        ax2.annotate(
            f"Final: {final_equity:,.0f}",
            xy=(eq_dates[-1], final_equity),
            xytext=(-80, 10),
            textcoords="offset points",
            fontsize=9,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", edgecolor="gray"),
            arrowprops=dict(arrowstyle="->", color="gray"),
        )

        ax2.legend(loc="upper left", fontsize=9)

    ax2.set_title("Equity Curve", fontsize=12, fontweight="bold")
    ax2.set_xlabel("Date", fontsize=12)
    ax2.set_ylabel("Equity (IDR)", fontsize=12)
    ax2.grid(True, alpha=0.3)

    # ------------------------------------------------------------------ #
    # Save                                                                #
    # ------------------------------------------------------------------ #
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    return output_path


def generate_backtest_chart_path(
    ticker: str,
    output_dir: str = "static/backtests",
) -> str:
    """
    Build a timestamped output path for a backtest chart PNG.

    Creates output_dir if it doesn't exist.

    Args:
        ticker: Stock ticker symbol.
        output_dir: Directory where the PNG will be saved.

    Returns:
        Full path string: ``{output_dir}/{ticker}_backtest_{YYYYMMDD_HHMMSS}.png``
    """
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{ticker}_backtest_{timestamp}.png"
    return os.path.join(output_dir, filename)


def get_backtest_chart_url(
    ticker: str,
    static_dir: str = "static/backtests",
) -> str | None:
    """
    Find the most recent backtest chart PNG for a given ticker.

    Args:
        ticker: Stock ticker symbol.
        static_dir: Directory to search for PNG files.

    Returns:
        Relative URL path to the most recent matching PNG,
        or ``None`` if no matching file is found.
    """
    pattern = os.path.join(static_dir, f"{ticker}_backtest_*.png")
    matches = glob.glob(pattern)

    if not matches:
        return None

    # Sort by modification time descending — most recent first
    matches.sort(key=os.path.getmtime, reverse=True)
    most_recent = matches[0]

    # Return as a relative URL path (forward slashes, no leading slash)
    return most_recent.replace(os.sep, "/")
