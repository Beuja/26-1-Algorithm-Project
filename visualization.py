# visualization.py
"""
키보드 배열 최적화 프로젝트 시각화 모듈 (히트맵 및 수렴 그래프).
[박서연 팀원 담당 모듈]

제공 함수:
  - plot_heatmap          : 단일 키보드 배열의 타건 빈도 히트맵 출력.
  - plot_heatmaps_comparison : 여러 배열을 동일 색상 척도로 나란히 비교.
  - plot_convergence      : 알고리즘별 수렴 곡선을 한 그래프에 표시.
  - plot_cost_breakdown   : D / F / P 비용 구성 요소 누적 가로 막대 차트.
  - save_all_plots        : 메인 시뮬레이터에서 호출하는 일괄 저장 래퍼.

의존성: matplotlib (pip install matplotlib)
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
# 내부 헬퍼
# ---------------------------------------------------------------------------

_KEY_W = 0.85        # 키 너비 (배열 좌표 단위)
_KEY_H = 0.70        # 키 높이
_CMAP = "YlOrRd"     # 히트맵 색상 (노랑 → 주황 → 빨강, 빈도 높을수록 진함)


def _draw_keyboard(ax, layout_str: str, color_values: dict, title: str, vmin=None, vmax=None):
    """
    ax 위에 26개 키를 그리고, color_values(문자 → 실수)에 따라 색을 입힌다.

    매개변수
    --------
    ax : matplotlib.axes.Axes
    layout_str : str
        각 슬롯에 어떤 글자가 배치되는지 나타내는 26자 문자열.
    color_values : dict
        {문자: 실수} 형태의 색상 기준값 (예: 정규화된 타건 빈도).
    title : str
        그래프 제목.
    vmin, vmax : float, optional
        색상 척도 범위. 기본값은 데이터의 최솟값/최댓값.
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

        # 배경 밝기에 따라 글자 색(검정/흰색) 자동 결정
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

    # 축 스타일 설정
    ax.set_xlim(-0.7, 9.7)
    ax.set_ylim(-0.65, 2.65)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=13, fontweight="bold", pad=10)

    # 색상 막대(컬러바) 추가
    sm = ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    plt.colorbar(sm, ax=ax, orientation="horizontal", pad=0.02,
                 fraction=0.03, label="Key Usage Frequency")


# ---------------------------------------------------------------------------
# 공개 API
# ---------------------------------------------------------------------------

def plot_heatmap(
    layout_str: str,
    unigram_counts: dict,
    title: str = "Keyboard Key-Frequency Heatmap",
    save_path: str = None,
    show: bool = True,
):
    """
    주어진 키보드 배열의 타건 빈도 히트맵을 렌더링한다.

    색이 진할수록(빨간색) 자주 타건되는 키, 옅을수록(노란색) 적게 타건되는 키.

    매개변수
    --------
    layout_str : str
        26자 배열 문자열.
    unigram_counts : dict
        코퍼스에서 추출한 {문자: 빈도수} 딕셔너리.
    title : str
        그래프 제목.
    save_path : str, optional
        지정하면 해당 경로에 파일 저장 (PNG/PDF/SVG 지원).
    show : bool
        True이면 plt.show() 호출. 배치 실행 시 False로 설정.
    """
    total = sum(unigram_counts.values()) or 1
    freq = {char: count / total for char, count in unigram_counts.items()}

    # 코퍼스에 등장하지 않은 문자는 빈도 0으로 채움
    for ch in layout_str:
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
    """
    여러 배열의 히트맵을 동일한 색상 척도로 세로로 나란히 렌더링한다.

    매개변수
    --------
    layouts : dict
        {배열명: 배열문자열} 예: {"QWERTY": "qwerty...", "SA 결과": "..."}
    unigram_counts : dict
        공유 {문자: 빈도수} 딕셔너리.
    save_path : str, optional
        저장 파일 경로.
    show : bool
        plt.show() 호출 여부.
    """
    total = sum(unigram_counts.values()) or 1
    freq = {char: count / total for char, count in unigram_counts.items()}

    n = len(layouts)
    fig, axes = plt.subplots(n, 1, figsize=(12, 4 * n))
    if n == 1:
        axes = [axes]

    # 모든 배열에 동일한 색상 범위 적용
    global_vmin = min(freq.values())
    global_vmax = max(freq.values())

    for ax, (name, layout_str) in zip(axes, layouts.items()):
        layout_freq = {}
        for ch in layout_str:
            layout_freq[ch] = freq.get(ch, 0.0)
        _draw_keyboard(
            ax, layout_str, layout_freq,
            title=f"타건 빈도 히트맵 — {name}",
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
    title: str = "알고리즘 수렴 속도 비교",
    xlabel: str = "기록 스텝",
    ylabel: str = "최적 비용 (낮을수록 좋음)",
    save_path: str = None,
    show: bool = True,
):
    """
    하나 이상의 알고리즘 수렴 곡선을 같은 축에 플롯한다.

    매개변수
    --------
    histories : dict
        {알고리즘명: list[float]} 예: {"SA": [...], "GA": [...]}
        각 리스트는 시간 순서대로 기록된 최적 비용값 시퀀스.
    title : str
        그래프 제목.
    xlabel, ylabel : str
        x축, y축 레이블.
    save_path : str, optional
        저장 파일 경로.
    show : bool
        plt.show() 호출 여부.
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

        # 최종 수렴값 표시
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
    """
    배열별 D / F / P 비용 구성 요소를 누적 가로 막대 차트로 렌더링한다.

    매개변수
    --------
    results : dict
        {배열명: {"D": float, "F": float, "P": float, "cost": float}}
        메인 시뮬레이터의 results 딕셔너리를 그대로 전달.
    weights : tuple
        (alpha, beta, gamma) 각 구성 요소의 시각화 스케일에 사용.
    save_path : str, optional
        저장 파일 경로.
    show : bool
        plt.show() 호출 여부.
    """
    alpha, beta, gamma = weights
    names = list(results.keys())
    d_vals = [results[n]["D"] * alpha for n in names]
    f_vals = [results[n]["F"] * beta  for n in names]
    p_vals = [results[n]["P"] * gamma for n in names]

    # 총 비용 기준 오름차순 정렬
    order = sorted(range(len(names)), key=lambda i: d_vals[i] + f_vals[i] + p_vals[i])
    names   = [names[i]  for i in order]
    d_vals  = [d_vals[i] for i in order]
    f_vals  = [f_vals[i] for i in order]
    p_vals  = [p_vals[i] for i in order]

    y = range(len(names))
    fig, ax = plt.subplots(figsize=(9, max(4, len(names) * 0.85)))

    bars_d = ax.barh(y, d_vals, color="#3498db", label=f"이동거리 D (×{alpha})")
    bars_f = ax.barh(y, f_vals, left=d_vals, color="#e74c3c",
                     label=f"동일손가락 피로도 F (×{beta})")
    left_p = [d + f for d, f in zip(d_vals, f_vals)]
    bars_p = ax.barh(y, p_vals, left=left_p, color="#f39c12",
                     label=f"한손 연속 패널티 P (×{gamma})")

    ax.set_yticks(list(y))
    ax.set_yticklabels(names, fontsize=11)
    ax.set_xlabel("가중 비용 구성 요소", fontsize=11)
    ax.set_title("배열별 비용 구성 분석 (낮을수록 좋음)", fontsize=13, fontweight="bold")
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
    """
    프로젝트 보고서에 사용되는 표준 그래프 3종을 일괄 생성 및 저장한다.

    생성되는 파일
    -------------
    1. plots/heatmap_comparison.png — 모든 배열의 타건 빈도 히트맵 비교.
    2. plots/convergence.png        — 최적화 알고리즘별 수렴 곡선.
    3. plots/cost_breakdown.png     — D / F / P 구성 요소 누적 막대 차트.

    매개변수
    --------
    results : dict
        main_simulator.run_simulation()이 반환하는 전체 결과 딕셔너리.
    histories : dict
        {알고리즘명: list[float]} 수렴 히스토리.
    unigram_counts : dict
        코퍼스 단일문자 빈도 딕셔너리.
    weights : tuple
        (alpha, beta, gamma), plot_cost_breakdown에 전달.
    output_dir : str
        PNG 파일을 저장할 디렉토리 경로.
    show : bool
        각 그래프에서 plt.show() 호출 여부 (자동 실행 시 False).
    """
    os.makedirs(output_dir, exist_ok=True)

    # 1. 히트맵 비교
    layout_map = {name: data["layout"] for name, data in results.items()}
    plot_heatmaps_comparison(
        layout_map, unigram_counts,
        save_path=os.path.join(output_dir, "heatmap_comparison.png"),
        show=show,
    )

    # 2. 수렴 그래프
    if histories:
        plot_convergence(
            histories,
            save_path=os.path.join(output_dir, "convergence.png"),
            show=show,
        )

    # 3. 비용 구성 분석 차트
    plot_cost_breakdown(
        results, weights,
        save_path=os.path.join(output_dir, "cost_breakdown.png"),
        show=show,
    )

    print(f"[visualization] 전체 그래프 저장 완료: '{output_dir}/' 디렉토리")


# ---------------------------------------------------------------------------
# 단독 실행 테스트
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from cost_function import compute_frequencies
    from layouts import QWERTY, DVORAK, COLEMAK

    sample = (
        "the quick brown fox jumps over the lazy dog "
        "pack my box with five dozen liquor jugs "
    ) * 300

    unigrams, bigrams, total = compute_frequencies(sample)

    print("단일 히트맵 출력 (QWERTY)...")
    plot_heatmap(QWERTY, unigrams, title="QWERTY — 타건 빈도 히트맵", show=True)

    print("비교 히트맵 출력...")
    plot_heatmaps_comparison(
        {"QWERTY": QWERTY, "DVORAK": DVORAK, "COLEMAK": COLEMAK},
        unigrams,
        show=True,
    )

    print("수렴 곡선 출력...")
    dummy_sa = [1.5 - 0.3 * math.log(1 + i * 0.1) + 0.02 * (i % 7) for i in range(100)]
    dummy_ga = [1.5 - 0.25 * math.log(1 + i * 0.2) for i in range(60)]
    plot_convergence(
        {"담금질 기법 (SA)": dummy_sa, "유전 알고리즘 (GA)": dummy_ga},
        title="수렴 속도 비교 (데모 데이터)",
        show=True,
    )
