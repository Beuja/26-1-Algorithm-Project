# greedy_algorithm.py
"""
키보드 배열 최적화를 위한 탐욕적 힐 클라이밍 알고리즘.
[김호재 팀장 담당 모듈]

탐색 전략: 최선 개선 힐 클라이밍 (Best-Improvement Hill Climbing).
  - QWERTY(또는 랜덤 배열)에서 시작한다.
  - 매 반복마다 C(26,2) = 325가지 모든 키 교환 쌍을 평가한다.
  - 비용을 가장 많이 줄이는 교환 1개를 채택한다.
  - 더 이상 개선되는 교환이 없을 때까지(지역 최솟값) 반복한다.
  - 랜덤 재시작으로 지역 최솟값 탈출을 보완한다.
"""

import random
from layouts import QWERTY
from cost_function import calculate_layout_cost

_ALPHABET = list("abcdefghijklmnopqrstuvwxyz")


def _hill_climb(
    init_layout: str,
    unigram_counts: dict,
    bigram_counts: dict,
    total_chars: int,
    weights: tuple,
    verbose: bool,
) -> tuple:
    """주어진 초기 배열에서 단일 힐 클라이밍 실행."""
    current_layout = init_layout
    current_cost = calculate_layout_cost(
        current_layout, unigram_counts, bigram_counts, total_chars, weights
    )["total_cost"]
    history = [current_cost]
    iteration = 0

    while True:
        best_neighbor_layout = current_layout
        best_neighbor_cost = current_cost
        found_improvement = False

        lst = list(current_layout)
        for i in range(26):
            for j in range(i + 1, 26):
                lst[i], lst[j] = lst[j], lst[i]
                candidate_cost = calculate_layout_cost(
                    "".join(lst), unigram_counts, bigram_counts, total_chars, weights
                )["total_cost"]

                if candidate_cost < best_neighbor_cost:
                    best_neighbor_cost = candidate_cost
                    best_neighbor_layout = "".join(lst)
                    found_improvement = True

                lst[i], lst[j] = lst[j], lst[i]

        if not found_improvement:
            break

        current_layout = best_neighbor_layout
        current_cost = best_neighbor_cost
        history.append(current_cost)
        iteration += 1

        if verbose:
            print(f"        반복 {iteration:>2}: 비용 = {current_cost:.6f}")

    call_count = 1 + 325 * iteration  # 초기 1회 + 매 반복 325회
    return current_layout, current_cost, history, call_count


def run_greedy_algorithm(
    unigram_counts: dict,
    bigram_counts: dict,
    total_chars: int,
    weights: tuple = (1.0, 2.0, 1.5),
    start_layout: str = None,
    num_restarts: int = 3,
    verbose: bool = False,
) -> tuple:
    """
    탐욕적 힐 클라이밍 알고리즘을 실행하여 최적 키보드 배열을 탐색한다.

    QWERTY 초기 실행 1회 후 num_restarts회 랜덤 재시작을 수행하여
    지역 최솟값 탈출을 보완한다. 전체 실행 중 가장 좋은 결과를 반환한다.

    매개변수
    --------
    unigram_counts : dict
        코퍼스 전처리로 얻은 {문자: 빈도수} 딕셔너리.
    bigram_counts : dict
        코퍼스 전처리로 얻은 {(c1, c2): 빈도수} 딕셔너리.
    total_chars : int
        코퍼스 내 알파벳 문자 총 개수.
    weights : tuple
        (alpha, beta, gamma) 비용 구성 요소 가중치.
    start_layout : str, optional
        시작 배열 문자열(26자). 기본값은 QWERTY.
    num_restarts : int
        QWERTY 초기 실행 후 추가 랜덤 재시작 횟수.
        값이 클수록 해의 품질은 높아지나 실행 시간이 늘어난다.
    verbose : bool
        True이면 반복마다 진행 상황을 출력한다.

    반환값
    ------
    best_layout : str
        전체 실행에서 발견된 최적 26자 배열 문자열.
    best_cost_details : dict
        최적 배열의 {'total_cost', 'D', 'F', 'P'} 딕셔너리.
    history : list[float]
        개선이 채택된 각 단계의 최적 비용 목록 (수렴 곡선).
        길이 = 개선 반복 횟수 + 1 (초기 비용 포함).
    """
    init = start_layout if start_layout else QWERTY

    if verbose:
        print(f"      [실행 0 / QWERTY 초기화] 힐 클라이밍 시작...")
    best_layout, best_cost, history, total_calls = _hill_climb(
        init, unigram_counts, bigram_counts, total_chars, weights, verbose
    )

    for restart_idx in range(num_restarts):
        random_init = "".join(random.sample(_ALPHABET, 26))
        if verbose:
            print(f"      [실행 {restart_idx + 1} / 랜덤 재시작] 힐 클라이밍 시작...")
        candidate_layout, candidate_cost, candidate_history, calls = _hill_climb(
            random_init, unigram_counts, bigram_counts, total_chars, weights, verbose
        )
        total_calls += calls
        if candidate_cost < best_cost:
            best_layout = candidate_layout
            best_cost = candidate_cost
            history = candidate_history
            if verbose:
                print(f"        -> 전역 최솟값 갱신: {best_cost:.6f}")

    total_calls += 1  # 최종 calculate_layout_cost 호출
    best_cost_details = calculate_layout_cost(
        best_layout, unigram_counts, bigram_counts, total_chars, weights
    )
    return best_layout, best_cost_details, history, total_calls


if __name__ == "__main__":
    from cost_function import compute_frequencies
    from layouts import visualize_layout

    test_corpus = (
        "the quick brown fox jumps over the lazy dog "
        "pack my box with five dozen liquor jugs "
    ) * 100

    unigrams, bigrams, total = compute_frequencies(test_corpus)

    print("=" * 50)
    print(" 탐욕 힐 클라이밍 - 동작 테스트")
    print("=" * 50)
    layout, cost_details, hist = run_greedy_algorithm(
        unigrams, bigrams, total,
        weights=(1.0, 2.0, 1.5),
        num_restarts=2,
        verbose=True,
    )

    print(f"\n최적 배열    : {layout}")
    print(visualize_layout(layout))
    print(f"\n총 비용      : {cost_details['total_cost']:.6f}")
    print(f"  D (이동거리): {cost_details['D']:.6f}")
    print(f"  F (피로도)  : {cost_details['F']:.6f}")
    print(f"  P (패널티)  : {cost_details['P']:.6f}")
    print(f"개선 횟수    : {len(hist) - 1}회 교환 채택")
