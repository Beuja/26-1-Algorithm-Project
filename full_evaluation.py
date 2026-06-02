# full_evaluation.py

import os
import time
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable

from corpus import load_corpus
from new_corpus import NEW_CORPUS
from cost_function import (compute_frequencies, calculate_layout_cost,
                           calculate_layout_cost_from_dicts)
from layouts import (QWERTY, DVORAK, COLEMAK, visualize_layout, layout_str_to_coord_dict,
                     DVORAK_COORDS, DVORAK_FINGERS, DVORAK_HANDS,
                     COLEMAK_COORDS, COLEMAK_FINGERS, COLEMAK_HANDS,
                     _DVORAK_TABLE, _COLEMAK_TABLE)
from greedy_algorithm import run_greedy_algorithm
from simulated_annealing import run_simulated_annealing
from genetic_algorithm import run_genetic_algorithm

WEIGHTS = (1.0, 2.0, 1.5)
OUT_DIR = "plots"
os.makedirs(OUT_DIR, exist_ok=True)

print("=" * 60)
print("  [Phase 1] corpus 텍스트로 알고리즘 최적 배열 도출")
print("=" * 60)

corpus_text = load_corpus()
uni_c, bi_c, tot_c = compute_frequencies(corpus_text)
print(f"  corpus 알파벳 수: {tot_c:,}\n")

print("  Greedy 실행 중...")
t0 = time.time()
greedy_layout, greedy_cost, greedy_hist, greedy_calls = run_greedy_algorithm(
    uni_c, bi_c, tot_c, WEIGHTS, num_restarts=3
)
print(f"  완료 ({time.time()-t0:.2f}s) | 비용: {greedy_cost['total_cost']:.5f} | 호출: {greedy_calls:,}회")

print("  Simulated Annealing 실행 중...")
t0 = time.time()
sa_layout, sa_cost, sa_hist, sa_calls = run_simulated_annealing(
    uni_c, bi_c, tot_c, WEIGHTS,
    initial_temp=10.0, cooling_rate=0.9992, iterations=15000,
)
print(f"  완료 ({time.time()-t0:.2f}s) | 비용: {sa_cost['total_cost']:.5f} | 호출: {sa_calls:,}회")

print("  Genetic Algorithm 실행 중...")
t0 = time.time()
ga_layout, ga_cost, ga_hist, ga_calls = run_genetic_algorithm(
    uni_c, bi_c, tot_c, WEIGHTS,
    pop_size=100, generations=150,
    crossover_rate=0.85, mutation_rate=0.25,
    elitism_count=5,
)
print(f"  완료 ({time.time()-t0:.2f}s) | 비용: {ga_cost['total_cost']:.5f} | 호출: {ga_calls:,}회\n")

LAYOUTS = {
    "QWERTY":      QWERTY,
    "Dvorak":      DVORAK_COORDS,
    "Colemak":     COLEMAK_COORDS,
    "Greedy":      greedy_layout,
    "Sim.Anneal.": sa_layout,
    "Gen.Algo.":   ga_layout,
}
_EXTENDED = {
    "Dvorak":  (DVORAK_COORDS,  DVORAK_FINGERS,  DVORAK_HANDS),
    "Colemak": (COLEMAK_COORDS, COLEMAK_FINGERS, COLEMAK_HANDS),
}

def _calc_cost(name, layout, uni, bi, tot):
    if name in _EXTENDED:
        coords, fingers, hands = _EXTENDED[name]
        return calculate_layout_cost_from_dicts(coords, fingers, hands, uni, bi, tot, WEIGHTS)
    return calculate_layout_cost(layout, uni, bi, tot, WEIGHTS)

corpus_results = {}
for name, layout in LAYOUTS.items():
    corpus_results[name] = _calc_cost(name, layout, uni_c, bi_c, tot_c)

print("=" * 60)
print("  [Phase 2] 새 텍스트로 6개 배열 교차검증")
print("=" * 60)

uni_n, bi_n, tot_n = compute_frequencies(NEW_CORPUS)
print(f"  new corpus 알파벳 수: {tot_n:,}\n")

new_results = {}
for name, layout in LAYOUTS.items():
    cd = _calc_cost(name, layout, uni_n, bi_n, tot_n)
    new_results[name] = cd
    print(f"  {name:<12}: {cd['total_cost']:.5f}")

ROW_COLORS = {
    "top":    "#AED6F1",
    "home":   "#A9DFBF",
    "bottom": "#FAD7A0",
}
KEY_W, KEY_H = 0.85, 0.70

def draw_layout_diagram(ax, layout, title):
    if isinstance(layout, str):
        coords = layout_str_to_coord_dict(layout)
    else:
        coords = layout

    xmax = max(x for x, y in coords.values())
    xlim_max = max(9.7, xmax + 0.7)

    for char, (x, y) in coords.items():
        if y == 2.0:
            fc = ROW_COLORS["top"]
        elif y == 1.0:
            fc = ROW_COLORS["home"]
        else:
            fc = ROW_COLORS["bottom"]

        rect = mpatches.FancyBboxPatch(
            (x - KEY_W/2, y - KEY_H/2), KEY_W, KEY_H,
            boxstyle="round,pad=0.05",
            linewidth=1.2, edgecolor="#555555", facecolor=fc,
        )
        ax.add_patch(rect)
        ax.text(x, y, char.upper(), ha="center", va="center",
                fontsize=13, fontweight="bold", color="#1a1a1a")

    ax.set_xlim(-0.7, xlim_max)
    ax.set_ylim(-0.6, 2.6)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=13, fontweight="bold", pad=8)

    legend_patches = [
        mpatches.Patch(color=ROW_COLORS["top"],    label="Top row"),
        mpatches.Patch(color=ROW_COLORS["home"],   label="Home row"),
        mpatches.Patch(color=ROW_COLORS["bottom"], label="Bottom row"),
    ]
    ax.legend(handles=legend_patches, loc="lower right",
              fontsize=7, framealpha=0.8)

fig, axes = plt.subplots(3, 2, figsize=(16, 12))
axes = axes.flatten()
for ax, (name, layout) in zip(axes, LAYOUTS.items()):
    draw_layout_diagram(ax, layout, name)

fig.suptitle("Keyboard Layout Comparison — All 6 Layouts",
             fontsize=16, fontweight="bold", y=1.01)
fig.tight_layout(h_pad=2.5, w_pad=1.5)
kb_path = os.path.join(OUT_DIR, "keyboard_layouts.png")
fig.savefig(kb_path, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"\n  [저장] {kb_path}")

qw_corpus = corpus_results["QWERTY"]["total_cost"]
qw_new    = new_results["QWERTY"]["total_cost"]

order = sorted(LAYOUTS.keys(), key=lambda n: corpus_results[n]["total_cost"])

col_labels = ["Layout", "Corpus Cost", "Corpus Improv.", "New Text Cost", "New Improv."]
table_data = []
for name in order:
    cr = corpus_results[name]
    nr = new_results[name]
    imp_c = (qw_corpus - cr["total_cost"]) / qw_corpus * 100
    imp_n = (qw_new    - nr["total_cost"]) / qw_new    * 100
    table_data.append([
        name,
        f"{cr['total_cost']:.5f}",
        f"{imp_c:+.2f}%",
        f"{nr['total_cost']:.5f}",
        f"{imp_n:+.2f}%",
    ])

fig, ax = plt.subplots(figsize=(11, 3.2))
ax.axis("off")

tbl = ax.table(
    cellText=table_data,
    colLabels=col_labels,
    loc="center",
    cellLoc="center",
)
tbl.auto_set_font_size(False)
tbl.set_fontsize(11)
tbl.scale(1.2, 1.8)

for j in range(len(col_labels)):
    tbl[0, j].set_facecolor("#2C3E50")
    tbl[0, j].set_text_props(color="white", fontweight="bold")

algo_names = {"Greedy", "Sim.Anneal.", "Gen.Algo."}
for i, name in enumerate(order):
    fc = "#EBF5FB" if name in algo_names else "#FDFEFE"
    for j in range(len(col_labels)):
        tbl[i+1, j].set_facecolor(fc)

ax.set_title("Cost Comparison: Training Corpus vs. New Text",
             fontsize=13, fontweight="bold", pad=12)
fig.tight_layout()
tbl_path = os.path.join(OUT_DIR, "comparison_table.png")
fig.savefig(tbl_path, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"  [저장] {tbl_path}")

COLORS = {
    "QWERTY":      "#E74C3C",
    "Dvorak":      "#E67E22",
    "Colemak":     "#F1C40F",
    "Greedy":      "#27AE60",
    "Sim.Anneal.": "#2980B9",
    "Gen.Algo.":   "#8E44AD",
}

names_sorted = order
corpus_costs = [corpus_results[n]["total_cost"] for n in names_sorted]
new_costs    = [new_results[n]["total_cost"]    for n in names_sorted]
colors       = [COLORS[n] for n in names_sorted]

x = range(len(names_sorted))
w = 0.38

fig, ax = plt.subplots(figsize=(11, 5))
bars1 = ax.bar([i - w/2 for i in x], corpus_costs, width=w,
               color=colors, alpha=0.85, label="Training Corpus", edgecolor="white")
bars2 = ax.bar([i + w/2 for i in x], new_costs,    width=w,
               color=colors, alpha=0.45, label="New Text",        edgecolor="white",
               hatch="//")

for bar in bars1:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
            f"{bar.get_height():.4f}", ha="center", va="bottom", fontsize=8)
for bar in bars2:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
            f"{bar.get_height():.4f}", ha="center", va="bottom", fontsize=8)

ax.set_xticks(list(x))
ax.set_xticklabels(names_sorted, fontsize=11)
ax.set_ylabel("Total Cost (lower is better)", fontsize=11)
ax.set_title("Total Cost: Training Corpus vs. New Text (All 6 Layouts)",
             fontsize=13, fontweight="bold")
ax.legend(fontsize=10)
ax.grid(axis="y", linestyle="--", alpha=0.5)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
fig.tight_layout()
bar_path = os.path.join(OUT_DIR, "cost_comparison_bar.png")
fig.savefig(bar_path, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"  [저장] {bar_path}")

print("\n" + "=" * 70)
print("  FINAL SUMMARY")
print("=" * 70)
ALGO_CALLS = {"Greedy": greedy_calls, "Sim.Anneal.": sa_calls, "Gen.Algo.": ga_calls}

header = f"{'Layout':<13} | {'Corpus Cost':>11} | {'Corpus Improv.':>14} | {'New Cost':>9} | {'New Improv.':>11} | {'Calls':>8}"
print(header)
print("-" * len(header))
for name in order:
    cr = corpus_results[name]
    nr = new_results[name]
    ic = (qw_corpus - cr["total_cost"]) / qw_corpus * 100
    in_ = (qw_new   - nr["total_cost"]) / qw_new    * 100
    calls_str = f"{ALGO_CALLS[name]:,}" if name in ALGO_CALLS else "-"
    print(f"{name:<13} | {cr['total_cost']:>11.5f} | {ic:>13.2f}% | {nr['total_cost']:>9.5f} | {in_:>10.2f}% | {calls_str:>8}")

print("=" * 70)
print(f"\n생성된 파일:")
print(f"  {kb_path}")
print(f"  {tbl_path}")
print(f"  {bar_path}")

print("\n최적 배열 (알고리즘 3종):")
for name in ["Greedy", "Sim.Anneal.", "Gen.Algo."]:
    print(f"\n  [{name}] {LAYOUTS[name]}")
    for line in visualize_layout(LAYOUTS[name]).split("\n"):
        print(f"    {line}")
