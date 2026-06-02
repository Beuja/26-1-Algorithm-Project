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
    DVORAK_COORDS,
    COLEMAK_COORDS,
)

_KEY_W = 0.85
_KEY_H = 0.70
_CMAP = "YlOrRd"


def _draw_keyboard(ax, layout, color_values: dict, title: str, vmin=None, vmax=None):
    all_vals = list(color_values.values())
    if vmin is None:
        vmin = min(all_vals)
    if vmax is None:
        vmax = max(all_vals)

    norm = Normalize(vmin=vmin, vmax=vmax)
    cmap = plt.get_cmap(_CMAP)

    # 문자열이면 QWERTY 26슬롯 변환, 딕셔너리면 확장 좌표로 직접 사용
    if isinstance(layout, str):
        coords = layout_str_to_coord_dict(layout)
    else:
        coords = layout

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

        r, g, b, _ = facecolor
        luminance = 0.299 * r + 0.587 * g + 0.114 * b
        text_color = "black" if luminance > 0.5 else "white"

        ax.text(x, y + 0.07, char.upper(),
                ha="center", va="center", fontsize=11, fontweight="bold", color=text_color)

        pct = val * 100
        ax.text(x, y - 0.18, f"{pct:.1f}%" if pct >= 0.1 else "",
                ha="center", va="center", fontsize=6.5, color=text_color)

    xmax = max(x for x, y in coords.values())
    ax.set_xlim(-0.7, max(9.7, xmax + 0.7))
    ax.set_ylim(-0.65, 2.65)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=13, fontweight="bold", pad=10)

    sm = ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    plt.colorbar(sm, ax=ax, orientation="horizontal", pad=0.02,
                 fraction=0.03, label="Key Usage Frequency")


def plot_heatmap(
    layout_str: str,
    unigram_counts: dict,
    title: str = "Keyboard Key-Frequency Heatmap",
    save_path: str = None,
    show: bool = True,
):
    total = sum(unigram_counts.values()) or 1
    freq = {char: count / total for char, count in unigram_counts.items()}

    chars = layout_str.keys() if isinstance(layout_str, dict) else layout_str
    for ch in chars:
        if ch not in freq:
            freq[ch] = 0.0

    fig, ax = plt.subplots(figsize=(12, 4))
    _draw_keyboard(ax, layout_str, freq, title)

    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"[visualization] 히트맵 저장 완료: '{save_path}'")
    if show:
        plt.show()
    plt.close(fig)


def plot_heatmaps_comparison(
    layouts: dict,
    unigram_counts: dict,
    save_path: str = None,
    show: bool = True,
):
    total = sum(unigram_counts.values()) or 1
    freq = {char: count / total for char, count in unigram_counts.items()}

    n = len(layouts)
    fig, axes = plt.subplots(n, 1, figsize=(12, 4 * n))
    if n == 1:
        axes = [axes]

    global_vmin = min(freq.values())
    global_vmax = max(freq.values())

    for ax, (name, layout) in zip(axes, layouts.items()):
        layout_freq = {}
        chars = layout.keys() if isinstance(layout, dict) else layout
        for ch in chars:
            layout_freq[ch] = freq.get(ch, 0.0)
        _draw_keyboard(
            ax, layout, layout_freq,
            title=f"Key Frequency Heatmap — {name}",
            vmin=global_vmin, vmax=global_vmax,
        )

    fig.tight_layout(h_pad=3.0)
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"[visualization] 비교 히트맵 저장 완료: '{save_path}'")
    if show:
        plt.show()
    plt.close(fig)


def plot_convergence(
    histories: dict,
    title: str = "Algorithm Convergence Comparison",
    xlabel: str = "Step",
    ylabel: str = "Best Cost (lower is better)",
    save_path: str = None,
    show: bool = True,
):
    colors = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12", "#9b59b6", "#1abc9c"]
    linestyles = ["-", "--", "-.", ":", "-", "--"]

    fig, ax = plt.subplots(figsize=(10, 5))

    for idx, (name, hist) in enumerate(histories.items()):
        if not hist:
            continue
        x = list(range(len(hist)))
        color = colors[idx % len(colors)]
        ls = linestyles[idx % len(linestyles)]

        ax.plot(x, hist, label=name, color=color, linestyle=ls, linewidth=1.8, alpha=0.9)
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
        print(f"[visualization] 수렴 그래프 저장 완료: '{save_path}'")
    if show:
        plt.show()
    plt.close(fig)


def plot_cost_breakdown(
    results: dict,
    weights: tuple = (1.0, 2.0, 1.5),
    save_path: str = None,
    show: bool = True,
):
    alpha, beta, gamma = weights
    names = list(results.keys())
    d_vals = [results[n]["D"] * alpha for n in names]
    f_vals = [results[n]["F"] * beta  for n in names]
    p_vals = [results[n]["P"] * gamma for n in names]

    order = sorted(range(len(names)), key=lambda i: d_vals[i] + f_vals[i] + p_vals[i])
    names  = [names[i]  for i in order]
    d_vals = [d_vals[i] for i in order]
    f_vals = [f_vals[i] for i in order]
    p_vals = [p_vals[i] for i in order]

    y = range(len(names))
    fig, ax = plt.subplots(figsize=(9, max(4, len(names) * 0.85)))

    ax.barh(y, d_vals, color="#3498db", label=f"Distance D (x{alpha})")
    ax.barh(y, f_vals, left=d_vals, color="#e74c3c", label=f"Same-Finger Fatigue F (x{beta})")
    left_p = [d + f for d, f in zip(d_vals, f_vals)]
    ax.barh(y, p_vals, left=left_p, color="#f39c12", label=f"Same-Hand Penalty P (x{gamma})")

    ax.set_yticks(list(y))
    ax.set_yticklabels(names, fontsize=11)
    ax.set_xlabel("Weighted Cost Components", fontsize=11)
    ax.set_title("Cost Breakdown by Layout (lower is better)", fontsize=13, fontweight="bold")
    ax.legend(loc="lower right", fontsize=10)
    ax.grid(True, axis="x", linestyle="--", alpha=0.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"[visualization] 비용 분해 차트 저장 완료: '{save_path}'")
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
    os.makedirs(output_dir, exist_ok=True)

    layout_map = {name: data["layout"] for name, data in results.items()}
    plot_heatmaps_comparison(
        layout_map, unigram_counts,
        save_path=os.path.join(output_dir, "heatmap_comparison.png"),
        show=show,
    )

    if histories:
        plot_convergence(
            histories,
            save_path=os.path.join(output_dir, "convergence.png"),
            show=show,
        )

    plot_cost_breakdown(
        results, weights,
        save_path=os.path.join(output_dir, "cost_breakdown.png"),
        show=show,
    )

    print(f"[visualization] 전체 그래프 저장 완료: '{output_dir}/' 디렉토리")


if __name__ == "__main__":
    from cost_function import compute_frequencies
    from layouts import QWERTY, DVORAK, COLEMAK

    sample = (
        "the quick brown fox jumps over the lazy dog "
        "pack my box with five dozen liquor jugs "
    ) * 300

    unigrams, bigrams, total = compute_frequencies(sample)

    plot_heatmap(QWERTY, unigrams, title="QWERTY — 타건 빈도 히트맵", show=True)

    dummy_sa = [1.5 - 0.3 * math.log(1 + i * 0.1) + 0.02 * (i % 7) for i in range(100)]
    dummy_ga = [1.5 - 0.25 * math.log(1 + i * 0.2) for i in range(60)]
    plot_convergence(
        {"담금질 기법 (SA)": dummy_sa, "유전 알고리즘 (GA)": dummy_ga},
        title="수렴 속도 비교 (데모 데이터)",
        show=True,
    )
