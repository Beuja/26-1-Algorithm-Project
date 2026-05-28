# simulated_annealing.py
"""
Simulated Annealing (SA) implementation for keyboard layout optimization.
[박서연 팀원 담당 모듈]

Strategy: Metropolis criterion-based stochastic search.
  - Start from an initial layout (default: QWERTY).
  - Each iteration randomly swaps two keys to generate a neighbor.
  - Accept improving neighbors always; accept worsening neighbors with
    probability exp(-delta_E / T) to escape local optima.
  - Temperature T decreases geometrically each iteration (geometric cooling).
  - Track global best layout separately from the current walk.
"""

import math
import random
from layouts import QWERTY
from cost_function import calculate_layout_cost

_ALPHABET = list("abcdefghijklmnopqrstuvwxyz")


def _random_swap(layout: str) -> str:
    """Returns a new layout with two randomly chosen keys swapped."""
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
    """
    Runs Simulated Annealing to find an optimized keyboard layout.

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
    initial_temp : float
        Starting temperature for the annealing schedule.
    cooling_rate : float
        Multiplicative cooling factor per iteration (0 < rate < 1).
        T_{t+1} = T_t * cooling_rate
    iterations : int
        Maximum number of iteration steps.
    min_temp : float
        Temperature floor — stops early if T falls below this.
    seed_layout : str, optional
        26-char starting layout string. Defaults to QWERTY.
    record_interval : int
        Record best cost to history every N iterations.
        Lower values produce smoother convergence curves but more data.
    verbose : bool
        Print progress every 500 iterations if True.

    Returns
    -------
    best_layout : str
        Best 26-character layout string found during the run.
    best_cost_details : dict
        {'total_cost', 'D', 'F', 'P'} for the best layout.
    history : list[float]
        Best cost sampled every `record_interval` iterations.
        Suitable for plotting the convergence curve.
    """
    # Initialise from seed or QWERTY
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
                print(f"      Early stop at step {step}: T={temp:.2e} < min_temp")
            break

        # Generate neighbour by swapping two random keys
        neighbor_layout = _random_swap(current_layout)
        neighbor_cost = calculate_layout_cost(
            neighbor_layout, unigram_counts, bigram_counts, total_chars, weights
        )["total_cost"]

        # Metropolis acceptance criterion
        delta_e = neighbor_cost - current_cost
        if delta_e < 0:
            # Always accept improvement
            current_layout = neighbor_layout
            current_cost = neighbor_cost
            accepted += 1
            improved += 1
        elif temp > 0 and random.random() < math.exp(-delta_e / temp):
            # Accept worsening move with probability e^{-dE/T}
            current_layout = neighbor_layout
            current_cost = neighbor_cost
            accepted += 1

        # Update global best
        if current_cost < best_cost:
            best_cost = current_cost
            best_layout = current_layout

        # Geometric cooling
        temp *= cooling_rate

        # Record convergence data
        if step % record_interval == 0:
            history.append(best_cost)

        if verbose and step % 500 == 0:
            print(
                f"      Step {step:>5} | T={temp:.4f} | "
                f"Best={best_cost:.6f} | Accepted={accepted}"
            )

    # Guarantee the final best cost is in history
    if history[-1] != best_cost:
        history.append(best_cost)

    if verbose:
        print(f"      Total accepted: {accepted} / {iterations} "
              f"({100*accepted/iterations:.1f}%) | Improved: {improved}")

    best_cost_details = calculate_layout_cost(
        best_layout, unigram_counts, bigram_counts, total_chars, weights
    )
    return best_layout, best_cost_details, history


if __name__ == "__main__":
    from cost_function import compute_frequencies
    from layouts import visualize_layout, QWERTY, DVORAK, COLEMAK

    test_corpus = (
        "the quick brown fox jumps over the lazy dog "
        "pack my box with five dozen liquor jugs "
    ) * 200

    unigrams, bigrams, total = compute_frequencies(test_corpus)

    print("=" * 50)
    print(" Simulated Annealing - Smoke Test")
    print("=" * 50)

    layout, cost_details, hist = run_simulated_annealing(
        unigrams, bigrams, total,
        weights=(1.0, 2.0, 1.5),
        initial_temp=10.0,
        cooling_rate=0.995,
        iterations=5000,
        verbose=True,
    )

    print(f"\nBest layout  : {layout}")
    print(visualize_layout(layout))
    print(f"\nTotal cost   : {cost_details['total_cost']:.6f}")
    print(f"  D (distance): {cost_details['D']:.6f}")
    print(f"  F (fatigue) : {cost_details['F']:.6f}")
    print(f"  P (penalty) : {cost_details['P']:.6f}")
    print(f"History pts  : {len(hist)} recorded steps")

    # Compare with baselines
    print("\n--- Baseline Comparison ---")
    for name, bl in [("QWERTY", QWERTY), ("DVORAK", DVORAK), ("COLEMAK", COLEMAK)]:
        c = calculate_layout_cost(bl, unigrams, bigrams, total)["total_cost"]
        print(f"{name:<8}: {c:.6f}")
    print(f"SA Result   : {cost_details['total_cost']:.6f}")
