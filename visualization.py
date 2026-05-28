# visualization.py
"""
Heatmap and convergence plot visualization module for keyboard layout optimization.
[박서연 팀원 담당 모듈]

Provides:
  - plot_heatmap:   Key-frequency heatmap overlaid on the keyboard layout.
  - plot_convergence: Algorithm convergence curves on a single axes.
  - save_all_plots: Convenience wrapper used by the main simulator.

Dependencies: matplotlib (pip install matplotlib)
"""

import math
import os
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable

from layouts import (
    PHYSICAL_COORDINATES,
    layout_str_to_coord_dict,
    visualize_layout,
    QWERTY,
)

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_KEY_W = 0.85        # key width (in layout coordinate units)
_KEY_H = 0.70        # key height
_CMAP = "YlOrRd"     # heatmap colormap (yellow -> orange -> red)


def _draw_keyboard(ax, layout_str: str, color_values: dict, title: str, vmin=None, vmax=None):
    """
    Draws the 26 keys on `ax`, coloured by `color_values` (char -> float).

    Parameters
    ----------
    ax : matplotlib.axes.Axes
    layout_str : str
        26-character layout string defining which letter sits at each slot.
    color_values : dict
        {char: float} values driving the colour (e.g., normalised frequency).
    title : str
        Plot title.
    vmin, vmax : float, optional
        Colour scale range. Defaults to data min/max.
    """
    all_vals = list(color_values.values())
    if vmin is None:
        vmin = min(all_vals)
    if vmax is None:
        vmax = max(all_vals)

    norm = Normalize(vmin=vmin, vmax=vmax)
    cmap = plt.get_cmap(_CMAP)

    coords = layout_str_to_coord_dict(layout_str)

    for char, (x, y) in coords.items():
        val = color_values.get(char, 0.0)
        facecolor = cmap(norm(val))

        rect = mpatches.FancyBboxPatch(
            (x - _KEY_W / 2, y - _KEY_H / 2),
            _KEY_W, _KEY_H,
            boxstyle="round,pad=0.05",
            linewidth=1.0,
            edgecolor="#444444",
            facecolor=facecolor,
        )
        ax.add_patch(rect)

        # Determine text colour for readability against background
        r, g, b, _ = facecolor
        luminance = 0.299 * r + 0.587 * g + 0.114 * b
        text_color = "black" if luminance > 0.5 else "white"

        ax.text(
            x, y + 0.07,
            char.upper(),
            ha="center", va="center",
            fontsize=11, fontweight="bold",
            color=text_color,
        )

        pct = val * 100
        ax.text(
            x, y - 0.18,
            f"{pct:.1f}%" if pct >= 0.1 else "",
            ha="center", va="center",
            fontsize=6.5, color=text_color,
        )

    # Axes styling
    ax.set_xlim(-0.7, 9.7)
    ax.set_ylim(-0.65, 2.65)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=13, fontweight="bold", pad=10)

    # Colour bar
    sm = ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    plt.colorbar(sm, ax=ax, orientation="horizontal", pad=0.02,
                 fraction=0.03, label="Key Usage Frequency")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def plot_heatmap(
    layout_str: str,
    unigram_counts: dict,
    title: str = "Keyboard Key-Frequency Heatmap",
    save_path: str = None,
    show: bool = True,
):
    """
    Renders a key-frequency heatmap for the given keyboard layout.

    Darker/redder keys are typed more often; lighter/yellower keys less often.

    Parameters
    ----------
    layout_str : str
        26-character layout string.
    unigram_counts : dict
        {char: count} raw frequency map from corpus.
    title : str
        Figure title.
    save_path : str, optional
        If provided, saves the figure to this file path (PNG/PDF/SVG).
    show : bool
        Whether to call plt.show(). Set False in batch/server mode.
    """
    total = sum(unigram_counts.values()) or 1
    freq = {char: count / total for char, count in unigram_counts.items()}

    # Fill missing characters with 0
    for ch in layout_str:
        if ch not in freq:
            freq[ch] = 0.0

    fig, ax = plt.subplots(figsize=(12, 4))
    _draw_keyboard(ax, layout_str, freq, title)

    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"[visualization] Heatmap saved to '{save_path}'")
    if show:
        plt.show()
    plt.close(fig)


def plot_heatmaps_comparison(
    layouts: dict,
    unigram_counts: dict,
    save_path: str = None,
    show: bool = True,
):
    """
    Renders side-by-side heatmaps for multiple layouts on the same colour scale.

    Parameters
    ----------
    layouts : dict
        {name: layout_str} e.g. {"QWERTY": "qwerty...", "SA Result": "..."}
    unigram_counts : dict
        Shared {char: count} frequency map.
    save_path : str, optional
        Output file path.
    show : bool
        Whether to call plt.show().
    """
    total = sum(unigram_counts.values()) or 1
    freq = {char: count / total for char, count in unigram_counts.items()}

    n = len(layouts)
    fig, axes = plt.subplots(n, 1, figsize=(12, 4 * n))
    if n == 1:
        axes = [axes]

    global_vmin = min(freq.values())
    global_vmax = max(freq.values())

    for ax, (name, layout_str) in zip(axes, layouts.items()):
        layout_freq = {}
        for ch in layout_str:
            layout_freq[ch] = freq.get(ch, 0.0)
        _draw_keyboard(
            ax, layout_str, layout_freq,
            title=f"Key-Frequency Heatmap — {name}",
            vmin=global_vmin, vmax=global_vmax,
        )

    fig.tight_layout(h_pad=3.0)
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"[visualization] Comparison heatmap saved to '{save_path}'")
    if show:
        plt.show()
    plt.close(fig)


def plot_convergence(
    histories: dict,
    title: str = "Algorithm Convergence Comparison",
    xlabel: str = "Recorded Step",
    ylabel: str = "Best Cost (lower is better)",
    save_path: str = None,
    show: bool = True,
):
    """
    Plots convergence curves for one or more algorithms on the same axes.

    Parameters
    ----------
    histories : dict
        {algorithm_name: list[float]}  e.g. {"SA": [...], "GA": [...]}
        Each list is a sequence of best-cost values over time.
    title : str
        Plot title.
    xlabel, ylabel : str
        Axis labels.
    save_path : str, optional
        Output file path.
    show : bool
        Whether to call plt.show().
    """
    colors = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12", "#9b59b6", "#1abc9c"]
    linestyles = ["-", "--", "-.", ":", "-", "--"]

    fig, ax = plt.subplots(figsize=(10, 5))

    for idx, (name, hist) in enumerate(histories.items()):
        if not hist:
            continue
        x = list(range(len(hist)))
        color = colors[idx % len(colors)]
        ls = linestyles[idx % len(linestyles)]

        ax.plot(x, hist, label=name, color=color, linestyle=ls,
                linewidth=1.8, alpha=0.9)

        # Mark final best value
        ax.annotate(
            f"{hist[-1]:.4f}",
            xy=(x[-1], hist[-1]),
            xytext=(5, 4),
            textcoords="offset points",
            fontsize=8,
            color=color,
        )

    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.set_xlabel(xlabel, fontsize=11)
    ax.set_ylabel(ylabel, fontsize=11)
    ax.legend(loc="upper right", fontsize=10)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"[visualization] Convergence plot saved to '{save_path}'")
    if show:
        plt.show()
    plt.close(fig)


def plot_cost_breakdown(
    results: dict,
    weights: tuple = (1.0, 2.0, 1.5),
    save_path: str = None,
    show: bool = True,
):
    """
    Renders a stacked horizontal bar chart breaking down D, F, P costs per layout.

    Parameters
    ----------
    results : dict
        {layout_name: {"D": float, "F": float, "P": float, "cost": float}}
        as produced by the main simulator.
    weights : tuple
        (alpha, beta, gamma) used to scale each component visually.
    save_path : str, optional
        Output file path.
    show : bool
        Whether to call plt.show().
    """
    alpha, beta, gamma = weights
    names = list(results.keys())
    d_vals = [results[n]["D"] * alpha for n in names]
    f_vals = [results[n]["F"] * beta  for n in names]
    p_vals = [results[n]["P"] * gamma for n in names]

    # Sort by total cost ascending
    order = sorted(range(len(names)), key=lambda i: d_vals[i] + f_vals[i] + p_vals[i])
    names   = [names[i]  for i in order]
    d_vals  = [d_vals[i] for i in order]
    f_vals  = [f_vals[i] for i in order]
    p_vals  = [p_vals[i] for i in order]

    y = range(len(names))
    fig, ax = plt.subplots(figsize=(9, max(4, len(names) * 0.85)))

    bars_d = ax.barh(y, d_vals, color="#3498db", label=f"Distance D (×{alpha})")
    bars_f = ax.barh(y, f_vals, left=d_vals, color="#e74c3c",
                     label=f"Fatigue F (×{beta})")
    left_p = [d + f for d, f in zip(d_vals, f_vals)]
    bars_p = ax.barh(y, p_vals, left=left_p, color="#f39c12",
                     label=f"Penalty P (×{gamma})")

    ax.set_yticks(list(y))
    ax.set_yticklabels(names, fontsize=11)
    ax.set_xlabel("Weighted Cost Component", fontsize=11)
    ax.set_title("Cost Breakdown by Layout (lower is better)", fontsize=13, fontweight="bold")
    ax.legend(loc="lower right", fontsize=10)
    ax.grid(True, axis="x", linestyle="--", alpha=0.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"[visualization] Cost breakdown saved to '{save_path}'")
    if show:
        plt.show()
    plt.close(fig)


def save_all_plots(
    results: dict,
    histories: dict,
    unigram_counts: dict,
    weights: tuple = (1.0, 2.0, 1.5),
    output_dir: str = "plots",
    show: bool = False,
):
    """
    Generates and saves all standard plots used in the project report.

    Plots produced
    --------------
    1. plots/heatmap_comparison.png — Key-frequency heatmaps for every layout.
    2. plots/convergence.png        — Convergence curves for optimisation algorithms.
    3. plots/cost_breakdown.png     — Stacked bar chart of D / F / P components.

    Parameters
    ----------
    results : dict
        Full results dict from main_simulator.run_simulation().
    histories : dict
        {algo_name: list[float]} convergence histories.
    unigram_counts : dict
        Corpus unigram frequencies.
    weights : tuple
        (alpha, beta, gamma) passed through to cost_breakdown.
    output_dir : str
        Directory in which to save the PNG files.
    show : bool
        Whether to call plt.show() for each plot (False in automated runs).
    """
    os.makedirs(output_dir, exist_ok=True)

    # 1. Heatmap comparison
    layout_map = {name: data["layout"] for name, data in results.items()}
    plot_heatmaps_comparison(
        layout_map, unigram_counts,
        save_path=os.path.join(output_dir, "heatmap_comparison.png"),
        show=show,
    )

    # 2. Convergence
    if histories:
        plot_convergence(
            histories,
            save_path=os.path.join(output_dir, "convergence.png"),
            show=show,
        )

    # 3. Cost breakdown
    plot_cost_breakdown(
        results, weights,
        save_path=os.path.join(output_dir, "cost_breakdown.png"),
        show=show,
    )

    print(f"[visualization] All plots saved to '{output_dir}/' directory.")


# ---------------------------------------------------------------------------
# Smoke test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from cost_function import compute_frequencies
    from layouts import QWERTY, DVORAK, COLEMAK

    sample = (
        "the quick brown fox jumps over the lazy dog "
        "pack my box with five dozen liquor jugs "
    ) * 300

    unigrams, bigrams, total = compute_frequencies(sample)

    print("Plotting single heatmap (QWERTY)...")
    plot_heatmap(QWERTY, unigrams, title="QWERTY — Key Frequency Heatmap", show=True)

    print("Plotting comparison heatmaps...")
    plot_heatmaps_comparison(
        {"QWERTY": QWERTY, "DVORAK": DVORAK, "COLEMAK": COLEMAK},
        unigrams,
        show=True,
    )

    print("Plotting convergence curves...")
    dummy_sa = [1.5 - 0.3 * math.log(1 + i * 0.1) + 0.02 * (i % 7) for i in range(100)]
    dummy_ga = [1.5 - 0.25 * math.log(1 + i * 0.2) for i in range(60)]
    plot_convergence(
        {"Simulated Annealing": dummy_sa, "Genetic Algorithm": dummy_ga},
        title="Convergence Comparison (demo data)",
        show=True,
    )
