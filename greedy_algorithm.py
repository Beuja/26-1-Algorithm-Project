# Best-Improvement Hill Climbing: 매 반복마다 C(26,2)=325가지 교환을 모두 평가해 최선 채택

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

    call_count = 1 + 325 * iteration
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

    total_calls += 1
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
    layout, cost_details, hist = run_greedy_algorithm(
        unigrams, bigrams, total,
        weights=(1.0, 2.0, 1.5),
        num_restarts=2,
        verbose=True,
    )

    print(f"\n최적 배열: {layout}")
    print(visualize_layout(layout))
    print(f"총 비용: {cost_details['total_cost']:.6f}")
    print(f"  D={cost_details['D']:.6f}  F={cost_details['F']:.6f}  P={cost_details['P']:.6f}")
    print(f"개선 횟수: {len(hist) - 1}회")
