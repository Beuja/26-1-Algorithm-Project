# main_simulator.py
"""
키보드 배열 최적화 통합 시뮬레이터.
[정종욱 팀원 담당 모듈]

탐욕(Greedy), 담금질(SA), 유전(GA) 알고리즘을 통합하여 실행하고,
최종 성능 비교표와 시각화 결과를 출력한다.
"""

import time
from layouts import QWERTY, DVORAK, COLEMAK, visualize_layout
from cost_function import compute_frequencies, calculate_layout_cost
from greedy_algorithm import run_greedy_algorithm
from genetic_algorithm import run_genetic_algorithm
from simulated_annealing import run_simulated_annealing
from corpus import load_corpus
from visualization import save_all_plots

# ==========================================
# 메인 통합 시뮬레이션
# ==========================================

def run_simulation(
    corpus_text: str = None,
    corpus_file: str = None,
    weights=(1.0, 2.0, 1.5),
    save_plots: bool = True,
    show_plots: bool = False,
):
    """
    기준 배열 3종과 최적화 알고리즘 3종을 동일 조건에서 실행하여 비교한다.

    매개변수
    --------
    corpus_text : str, optional
        원본 코퍼스 문자열. None이면 corpus.py를 통해 로드한다.
    corpus_file : str, optional
        일반 텍스트 코퍼스 파일 경로 (corpus.load_corpus에 전달).
    weights : tuple
        (alpha, beta, gamma) 비용 가중치.
    save_plots : bool
        True이면 히트맵, 수렴 그래프, 비용 분해 차트를 ./plots/에 저장한다.
    show_plots : bool
        True이면 그래프를 화면에 대화형으로 표시한다 (창 닫기 전까지 실행 차단).
    """
    if corpus_text is None:
        corpus_text = load_corpus(corpus_file)

    print("=" * 60)
    print("      KEYBOARD LAYOUT OPTIMIZATION INTEGRATED SIMULATOR")
    print("=" * 60)

    # 텍스트 전처리 및 빈도 통계 산출
    print("[1/5] 텍스트 코퍼스 전처리 중...")
    unigrams, bigrams, total_chars = compute_frequencies(corpus_text)
    print(f"      분석된 알파벳 문자 수: {total_chars}")
    print(f"      유니그램 종류: {len(unigrams)} | 바이그램 종류: {len(bigrams)}")
    print(f"      비용 가중치 (alpha, beta, gamma): {weights}\n")

    # 결과 저장 딕셔너리
    results = {}

    # ------------------------------------------
    # 단계 A: 기준 배열 비용 평가
    # ------------------------------------------
    print("[2/5] 기준 배열 비용 평가 중...")
    for name, layout in [("QWERTY", QWERTY), ("DVORAK", DVORAK), ("COLEMAK", COLEMAK)]:
        t0 = time.time()
        cost_details = calculate_layout_cost(layout, unigrams, bigrams, total_chars, weights)
        elapsed = time.time() - t0
        results[name] = {
            "layout": layout,
            "cost": cost_details["total_cost"],
            "D": cost_details["D"],
            "F": cost_details["F"],
            "P": cost_details["P"],
            "time": elapsed
        }
        print(f"      - {name:<8} 비용: {cost_details['total_cost']:.5f}")

    qwerty_cost = results["QWERTY"]["cost"]
    print()

    # ------------------------------------------
    # 단계 B: 탐욕 알고리즘 실행 (김호재)
    # ------------------------------------------
    print("[3/5] 탐욕 알고리즘 실행 중 (팀장 김호재)...")
    t0 = time.time()
    greedy_layout, greedy_cost_details, greedy_history, greedy_calls = run_greedy_algorithm(
        unigrams, bigrams, total_chars, weights, num_restarts=3
    )
    elapsed = time.time() - t0
    results["Greedy"] = {
        "layout": greedy_layout,
        "cost": greedy_cost_details["total_cost"],
        "D": greedy_cost_details["D"],
        "F": greedy_cost_details["F"],
        "P": greedy_cost_details["P"],
        "time": elapsed,
        "calls": greedy_calls,
        "history": greedy_history
    }
    print(f"      완료: {elapsed:.4f}초 | 비용: {greedy_cost_details['total_cost']:.5f} | 호출: {greedy_calls:,}회\n")

    # ------------------------------------------
    # 단계 C: 담금질 기법 실행 (박서연)
    # ------------------------------------------
    print("[4/5] 담금질 기법 실행 중...")
    t0 = time.time()
    sa_layout, sa_cost_details, sa_history, sa_calls = run_simulated_annealing(
        unigrams, bigrams, total_chars, weights,
        initial_temp=10.0, cooling_rate=0.9992, iterations=15000,
    )
    elapsed = time.time() - t0
    results["Sim. Anneal."] = {
        "layout": sa_layout,
        "cost": sa_cost_details["total_cost"],
        "D": sa_cost_details["D"],
        "F": sa_cost_details["F"],
        "P": sa_cost_details["P"],
        "time": elapsed,
        "calls": sa_calls,
        "history": sa_history,
    }
    print(f"      완료: {elapsed:.4f}초 | 비용: {sa_cost_details['total_cost']:.5f} | 호출: {sa_calls:,}회\n")

    # ------------------------------------------
    # 단계 D: 유전 알고리즘 실행 (정종욱)
    # ------------------------------------------
    print("[5/5] 유전 알고리즘 실행 중 (팀원 정종욱)...")
    t0 = time.time()
    ga_layout, ga_cost_details, ga_history, ga_calls = run_genetic_algorithm(
        unigrams, bigrams, total_chars, weights,
        pop_size=100, generations=150,
        crossover_rate=0.85, mutation_rate=0.25,
        elitism_count=5,
    )
    elapsed = time.time() - t0
    results["Gen. Algo."] = {
        "layout": ga_layout,
        "cost": ga_cost_details["total_cost"],
        "D": ga_cost_details["D"],
        "F": ga_cost_details["F"],
        "P": ga_cost_details["P"],
        "time": elapsed,
        "calls": ga_calls,
    }
    print(f"      완료: {elapsed:.4f}초 | 비용: {ga_cost_details['total_cost']:.5f} | 호출: {ga_calls:,}회\n")

    # ==========================================
    # 최종 성능 비교표 출력
    # ==========================================
    print("=" * 70)
    print("                   FINAL PERFORMANCE EVALUATION REPORT")
    print("=" * 70)

    header = f"{'Layout Name':<13} | {'Total Cost':<10} | {'Distance (D)':<12} | {'Fatigue (F)':<11} | {'Penalty (P)':<11} | {'Improv. %':<9} | {'Calls':<8} | {'Runtime'}"
    separator = "-" * len(header)
    print(header)
    print(separator)

    # 비용 기준 오름차순 정렬
    sorted_layouts = sorted(results.items(), key=lambda x: x[1]["cost"])

    for name, data in sorted_layouts:
        improv = ((qwerty_cost - data["cost"]) / qwerty_cost) * 100
        time_str = f"{data['time']:.4f}s" if data['time'] > 0 else "N/A"
        calls_str = f"{data['calls']:,}" if "calls" in data else "-"
        print(f"{name:<13} | {data['cost']:<10.5f} | {data['D']:<12.5f} | {data['F']:<11.5f} | {data['P']:<11.5f} | {improv:>7.2f}% | {calls_str:<8} | {time_str}")

    print("=" * 70)
    print("Note: Improvement is calculated relative to QWERTY (lower cost is better).\n")

    # 최적 배열 요약 출력
    best_name, best_data = sorted_layouts[0]
    print(f"[BEST] 최적 탐색 배열: {best_name}")
    print(f"비용: {best_data['cost']:.5f} (QWERTY 대비 {((qwerty_cost - best_data['cost']) / qwerty_cost) * 100:.2f}% 개선)")
    print(visualize_layout(best_data["layout"]))
    print("=" * 70)

    # ==========================================
    # 시각화 (박서연)
    # ==========================================
    if save_plots or show_plots:
        print("\n[시각화] 그래프 생성 중...")
        histories = {}
        for algo in ("Greedy", "Sim. Anneal.", "Gen. Algo."):
            if algo in results and "history" in results[algo]:
                histories[algo] = results[algo]["history"]

        save_all_plots(
            results=results,
            histories=histories,
            unigram_counts=unigrams,
            weights=weights,
            output_dir="plots",
            show=show_plots,
        )

    return results


if __name__ == "__main__":
    run_simulation(save_plots=True, show_plots=False)
