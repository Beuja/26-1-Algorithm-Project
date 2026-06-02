import math
import random
from layouts import QWERTY
from cost_function import calculate_layout_cost

_ALPHABET = list("abcdefghijklmnopqrstuvwxyz")


def _random_swap(layout: str) -> str:
    lst = list(layout)
    i, j = random.sample(range(26), 2)
    lst[i], lst[j] = lst[j], lst[i]
    return "".join(lst)


def run_simulated_annealing(
    unigram_counts: dict,
    bigram_counts: dict,
    total_chars: int,
    weights: tuple = (1.0, 2.0, 1.5),
    initial_temp: float = 10.0,
    cooling_rate: float = 0.995,
    iterations: int = 5000,
    min_temp: float = 1e-4,
    seed_layout: str = None,
    record_interval: int = 10,
    verbose: bool = False,
) -> tuple:
    current_layout = seed_layout if (seed_layout and len(seed_layout) == 26) else QWERTY
    current_cost = calculate_layout_cost(
        current_layout, unigram_counts, bigram_counts, total_chars, weights
    )["total_cost"]

    best_layout = current_layout
    best_cost = current_cost

    temp = initial_temp
    history = [best_cost]
    accepted = 0
    improved = 0

    for step in range(1, iterations + 1):
        if temp < min_temp:
            if verbose:
                print(f"      {step}번째 스텝에서 조기 종료: T={temp:.2e}")
            break

        neighbor_layout = _random_swap(current_layout)
        neighbor_cost = calculate_layout_cost(
            neighbor_layout, unigram_counts, bigram_counts, total_chars, weights
        )["total_cost"]

        delta_e = neighbor_cost - current_cost
        if delta_e < 0:
            current_layout = neighbor_layout
            current_cost = neighbor_cost
            accepted += 1
            improved += 1
        elif temp > 0 and random.random() < math.exp(-delta_e / temp):
            # 비용이 올라도 exp(-dE/T) 확률로 채택 → 지역 최솟값 탈출
            current_layout = neighbor_layout
            current_cost = neighbor_cost
            accepted += 1

        if current_cost < best_cost:
            best_cost = current_cost
            best_layout = current_layout

        temp *= cooling_rate

        if step % record_interval == 0:
            history.append(best_cost)

        if verbose and step % 500 == 0:
            print(
                f"      스텝 {step:>5} | T={temp:.4f} | "
                f"최적={best_cost:.6f} | 채택={accepted}"
            )

    if history[-1] != best_cost:
        history.append(best_cost)

    if verbose:
        print(f"      총 채택: {accepted} / {iterations} "
              f"({100*accepted/iterations:.1f}%) | 개선: {improved}")

    total_calls = step + 2
    best_cost_details = calculate_layout_cost(
        best_layout, unigram_counts, bigram_counts, total_chars, weights
    )
    return best_layout, best_cost_details, history, total_calls


if __name__ == "__main__":
    from cost_function import compute_frequencies
    from layouts import visualize_layout, QWERTY, DVORAK, COLEMAK

    test_corpus = (
        "the quick brown fox jumps over the lazy dog "
        "pack my box with five dozen liquor jugs "
    ) * 200

    unigrams, bigrams, total = compute_frequencies(test_corpus)

    layout, cost_details, hist = run_simulated_annealing(
        unigrams, bigrams, total,
        weights=(1.0, 2.0, 1.5),
        initial_temp=10.0,
        cooling_rate=0.995,
        iterations=5000,
        verbose=True,
    )

    print(f"\n최적 배열: {layout}")
    print(visualize_layout(layout))
    print(f"총 비용: {cost_details['total_cost']:.6f}")
    print(f"  D={cost_details['D']:.6f}  F={cost_details['F']:.6f}  P={cost_details['P']:.6f}")
