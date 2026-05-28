# greedy_algorithm.py
"""
Greedy Hill Climbing algorithm for keyboard layout optimization.
[김호재 팀장 담당 모듈]

Strategy: Best-improvement hill climbing.
  - Start from QWERTY (and optionally random restarts).
  - Each iteration evaluates all C(26,2) = 325 pairwise key swaps.
  - Accept the single best swap that reduces cost.
  - Repeat until no improving swap exists (local minimum reached).
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
    """Single best-improvement hill climbing run from init_layout."""
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
            print(f"        Iter {iteration:>2}: Cost = {current_cost:.6f}")

    return current_layout, current_cost, history


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
    Runs the Greedy Hill Climbing algorithm to find an optimized keyboard layout.

    Performs one QWERTY-seeded run followed by num_restarts random-restart runs
    to escape local optima. Returns the globally best result found.

    Parameters
    ----------
    unigram_counts : dict
        {char: count} mapping from corpus preprocessing.
    bigram_counts : dict
        {(c1, c2): count} mapping from corpus preprocessing.
    total_chars : int
        Total alphabetic character count in the corpus.
    weights : tuple
        (alpha, beta, gamma) cost component weights.
    start_layout : str, optional
        26-char starting layout string. Defaults to QWERTY.
    num_restarts : int
        Number of additional random-restart runs after the primary QWERTY run.
        Higher values improve solution quality at the cost of runtime.
    verbose : bool
        Print per-iteration progress if True.

    Returns
    -------
    best_layout : str
        Best 26-character layout string found across all runs.
    best_cost_details : dict
        {'total_cost', 'D', 'F', 'P'} for the best layout.
    history : list[float]
        Best cost at each accepted improvement step (convergence curve).
        Length equals number of improving iterations + 1 (initial cost).
    """
    init = start_layout if start_layout else QWERTY

    if verbose:
        print(f"      [Run 0 / QWERTY-init] Starting hill climb...")
    best_layout, best_cost, history = _hill_climb(
        init, unigram_counts, bigram_counts, total_chars, weights, verbose
    )

    for restart_idx in range(num_restarts):
        random_init = "".join(random.sample(_ALPHABET, 26))
        if verbose:
            print(f"      [Run {restart_idx + 1} / random-restart] Starting hill climb...")
        candidate_layout, candidate_cost, candidate_history = _hill_climb(
            random_init, unigram_counts, bigram_counts, total_chars, weights, verbose
        )
        if candidate_cost < best_cost:
            best_layout = candidate_layout
            best_cost = candidate_cost
            history = candidate_history
            if verbose:
                print(f"        -> New global best: {best_cost:.6f}")

    best_cost_details = calculate_layout_cost(
        best_layout, unigram_counts, bigram_counts, total_chars, weights
    )
    return best_layout, best_cost_details, history


if __name__ == "__main__":
    from cost_function import compute_frequencies
    from layouts import visualize_layout

    test_corpus = (
        "the quick brown fox jumps over the lazy dog "
        "pack my box with five dozen liquor jugs "
    ) * 100

    unigrams, bigrams, total = compute_frequencies(test_corpus)

    print("=" * 50)
    print(" Greedy Hill Climbing - Smoke Test")
    print("=" * 50)
    layout, cost_details, hist = run_greedy_algorithm(
        unigrams, bigrams, total,
        weights=(1.0, 2.0, 1.5),
        num_restarts=2,
        verbose=True,
    )

    print(f"\nBest layout  : {layout}")
    print(visualize_layout(layout))
    print(f"\nTotal cost   : {cost_details['total_cost']:.6f}")
    print(f"  D (distance): {cost_details['D']:.6f}")
    print(f"  F (fatigue) : {cost_details['F']:.6f}")
    print(f"  P (penalty) : {cost_details['P']:.6f}")
    print(f"Improvements : {len(hist) - 1} accepted swaps")
