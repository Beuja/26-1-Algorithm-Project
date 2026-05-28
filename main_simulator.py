# main_simulator.py
"""
Main Simulator and Integration Module for Keyboard Layout Optimization.
Integrates Greedy, Simulated Annealing, and Genetic Algorithms.
Outputs final comparison tables and visualizes best layouts.
"""

import time
from layouts import QWERTY, DVORAK, COLEMAK, visualize_layout
from cost_function import compute_frequencies, calculate_layout_cost
from greedy_algorithm import run_greedy_algorithm
from genetic_algorithm import run_genetic_algorithm
from simulated_annealing import run_simulated_annealing   # 박서연
from corpus import load_corpus                             # 박서연
from visualization import save_all_plots                   # 박서연

# ==========================================
# 2. Main Integration and Simulation
# ==========================================

def run_simulation(
    corpus_text: str = None,
    corpus_file: str = None,
    weights=(1.0, 2.0, 1.5),
    save_plots: bool = True,
    show_plots: bool = False,
):
    """
    Runs baselines and all three optimization algorithms to compare keyboard layouts.

    Parameters
    ----------
    corpus_text : str, optional
        Raw corpus string. If None, loads via corpus.py (file or built-in).
    corpus_file : str, optional
        Path to a plain-text corpus file (passed to corpus.load_corpus).
    weights : tuple
        (alpha, beta, gamma) cost weights.
    save_plots : bool
        If True, saves heatmap, convergence, and breakdown plots to ./plots/.
    show_plots : bool
        If True, displays plots interactively (blocks execution until closed).
    """
    if corpus_text is None:
        corpus_text = load_corpus(corpus_file)

    print("=" * 60)
    print("      KEYBOARD LAYOUT OPTIMIZATION INTEGRATED SIMULATOR")
    print("=" * 60)

    # Preprocess text and calculate statistics
    print("[1/5] Preprocessing text corpus...")
    unigrams, bigrams, total_chars = compute_frequencies(corpus_text)
    print(f"      Total alphabetic characters analyzed: {total_chars}")
    print(f"      Unique unigrams: {len(unigrams)} | Unique bigrams: {len(bigrams)}")
    print(f"      Cost Weights (alpha, beta, gamma): {weights}\n")
    
    # Store results for final table
    results = {}
    
    # ------------------------------------------
    # Step A: Evaluate Baselines
    # ------------------------------------------
    print("[2/5] Evaluating Baseline Layouts...")
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
        print(f"      - {name:<8} Cost: {cost_details['total_cost']:.5f}")
        
    qwerty_cost = results["QWERTY"]["cost"]
    print()
    
    # ------------------------------------------
    # Step B: Run Greedy Optimizer (Kim Ho-jae)
    # ------------------------------------------
    print("[3/5] Running Greedy Optimizer (팀장 김호재)...")
    t0 = time.time()
    greedy_layout, greedy_cost_details, greedy_history = run_greedy_algorithm(
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
        "history": greedy_history
    }
    print(f"      Completed in {elapsed:.4f}s | Cost: {greedy_cost_details['total_cost']:.5f}\n")
    
    # ------------------------------------------
    # Step C: Run Simulated Annealing (Park Seo-yeon)
    # ------------------------------------------
    print("[4/5] Running Simulated Annealing Optimizer (팀원 박서연)...")
    t0 = time.time()
    sa_layout, sa_cost_details, sa_history = run_simulated_annealing(
        unigrams, bigrams, total_chars, weights,
        initial_temp=10.0, cooling_rate=0.995, iterations=5000,
    )
    elapsed = time.time() - t0
    results["Sim. Anneal."] = {
        "layout": sa_layout,
        "cost": sa_cost_details["total_cost"],
        "D": sa_cost_details["D"],
        "F": sa_cost_details["F"],
        "P": sa_cost_details["P"],
        "time": elapsed,
        "history": sa_history,
    }
    print(f"      Completed in {elapsed:.4f}s | Cost: {sa_cost_details['total_cost']:.5f}\n")
    
    # ------------------------------------------
    # Step D: Run Genetic Algorithm (Jeong Jong-wook - Core)
    # ------------------------------------------
    print("[5/5] Running Genetic Algorithm Optimizer (팀원 정종욱)...")
    t0 = time.time()
    # Inject baseline layouts as seeds to guarantee optimization threshold
    seeds = [QWERTY, DVORAK, COLEMAK, greedy_layout, sa_layout]
    ga_layout, ga_cost_details, ga_history = run_genetic_algorithm(
        unigrams, bigrams, total_chars, weights,
        pop_size=100, generations=150,
        crossover_rate=0.85, mutation_rate=0.25,
        elitism_count=5, seed_layouts=seeds
    )
    elapsed = time.time() - t0
    results["Gen. Algo."] = {
        "layout": ga_layout,
        "cost": ga_cost_details["total_cost"],
        "D": ga_cost_details["D"],
        "F": ga_cost_details["F"],
        "P": ga_cost_details["P"],
        "time": elapsed
    }
    print(f"      Completed in {elapsed:.4f}s | Cost: {ga_cost_details['total_cost']:.5f}\n")
    
    # ==========================================
    # 4. Generate Performance Comparison Table
    # ==========================================
    print("=" * 70)
    print("                   FINAL PERFORMANCE EVALUATION REPORT")
    print("=" * 70)
    
    header = f"{'Layout Name':<13} | {'Total Cost':<10} | {'Distance (D)':<12} | {'Fatigue (F)':<11} | {'Penalty (P)':<11} | {'Improv. %':<9} | {'Runtime'}"
    separator = "-" * len(header)
    print(header)
    print(separator)
    
    sorted_layouts = sorted(results.items(), key=lambda x: x[1]["cost"])
    
    for name, data in sorted_layouts:
        improv = ((qwerty_cost - data["cost"]) / qwerty_cost) * 100
        time_str = f"{data['time']:.4f}s" if data['time'] > 0 else "N/A"
        print(f"{name:<13} | {data['cost']:<10.5f} | {data['D']:<12.5f} | {data['F']:<11.5f} | {data['P']:<11.5f} | {improv:>7.2f}% | {time_str}")
        
    print("=" * 70)
    print("Note: Improvement is calculated relative to QWERTY (lower cost is better).\n")

    # Best layout summary
    best_name, best_data = sorted_layouts[0]
    print(f"[BEST] BEST DETECTED KEYBOARD ARRANGEMENT: {best_name}")
    print(f"Cost: {best_data['cost']:.5f} ({((qwerty_cost - best_data['cost']) / qwerty_cost) * 100:.2f}% improvement over QWERTY)")
    print(visualize_layout(best_data["layout"]))
    print("=" * 70)

    # ==========================================
    # 5. Visualization (박서연)
    # ==========================================
    if save_plots or show_plots:
        print("\n[Visualization] Generating plots (박서연)...")
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
