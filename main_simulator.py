# main_simulator.py
"""
Main Simulator Skeleton and Integration Module for Keyboard Layout Optimization.
Integrates Greedy, Simulated Annealing, and Genetic Algorithms.
Outputs final comparison tables and visualizes best layouts.
"""

import time
import math
import random
from layouts import QWERTY, DVORAK, COLEMAK, visualize_layout
from cost_function import compute_frequencies, calculate_layout_cost
from greedy_algorithm import run_greedy_algorithm
from genetic_algorithm import run_genetic_algorithm

# ==========================================
# 1. Built-in Representative Corpus Sample
# ==========================================
DEFAULT_CORPUS = """
The Genetic Algorithm is a method for solving both constrained and unconstrained optimization problems 
that is based on natural selection, the process that drives biological evolution. 
The genetic algorithm repeatedly modifies a population of individual solutions. 
At each step, the genetic algorithm selects individuals at random from the current population 
to be parents and uses them to produce the children for the next generation. 
Over successive generations, the population "evolves" toward an optimal solution. 
You can apply the genetic algorithm to solve a variety of optimization problems that are not 
well suited for standard optimization algorithms, including problems in which the objective 
function is discontinuous, nondifferentiable, stochastic, or highly nonlinear. 
The genetic algorithm uses three main types of rules at each step to create the next generation 
from the current population: selection rules select the individuals, called parents, 
that contribute to the population at the next generation. 
Crossover rules combine two parents to form children for the next generation. 
Mutation rules apply random changes to individual parents to form children.
Keyboard layout optimization is a challenging combinatorial problem because there are 26! 
possible arrangements of the letters of the English alphabet. 26 factorial is approximately 
four times ten to the twenty-six, which is an extremely vast search space. 
Standard methods like brute-force are completely infeasible, making heuristic search 
algorithms like Greedy search, Simulated Annealing, and Genetic Algorithms highly suited 
and crucial for finding high-quality optimal keyboard arrangements.
"""

# ==========================================
# 2. Team Member Stubs & Implementations
# ==========================================


def simulated_annealing_optimizer(
    unigram_counts: dict,
    bigram_counts: dict,
    total_chars: int,
    weights: tuple = (1.0, 2.0, 1.5),
    initial_temp: float = 10.0,
    cooling_rate: float = 0.995,
    iterations: int = 1500
) -> tuple:
    """
    [박서연 팀원 역할 - Simulated Annealing Optimization]
    Starts with a layout, randomly swaps two keys, and decides whether to accept
    the new layout based on Metropolis criteria.
    """
    current_layout = QWERTY
    current_cost = calculate_layout_cost(current_layout, unigram_counts, bigram_counts, total_chars, weights)["total_cost"]
    
    best_layout = current_layout
    best_cost = current_cost
    
    temp = initial_temp
    
    for _ in range(iterations):
        # Swap two random keys to generate neighbor
        lst = list(current_layout)
        i, j = random.sample(range(26), 2)
        lst[i], lst[j] = lst[j], lst[i]
        neighbor_layout = "".join(lst)
        
        neighbor_cost = calculate_layout_cost(neighbor_layout, unigram_counts, bigram_counts, total_chars, weights)["total_cost"]
        
        # Metropolis acceptance criterion
        delta_e = neighbor_cost - current_cost
        if delta_e < 0 or random.random() < math.exp(-delta_e / temp):
            current_layout = neighbor_layout
            current_cost = neighbor_cost
            
            # Keep track of global best
            if current_cost < best_cost:
                best_cost = current_cost
                best_layout = current_layout
                
        # Cool down
        temp *= cooling_rate
        
    best_cost_details = calculate_layout_cost(best_layout, unigram_counts, bigram_counts, total_chars, weights)
    return best_layout, best_cost_details

# ==========================================
# 3. Main Integration and Simulation
# ==========================================

def run_simulation(corpus_text: str = None, weights=(1.0, 2.0, 1.5)):
    """Runs baselines and all three optimization algorithms to compare keyboard layouts."""
    if corpus_text is None:
        corpus_text = DEFAULT_CORPUS
        
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
    sa_layout, sa_cost_details = simulated_annealing_optimizer(unigrams, bigrams, total_chars, weights)
    elapsed = time.time() - t0
    results["Sim. Anneal."] = {
        "layout": sa_layout,
        "cost": sa_cost_details["total_cost"],
        "D": sa_cost_details["D"],
        "F": sa_cost_details["F"],
        "P": sa_cost_details["P"],
        "time": elapsed
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
    
    # Visualizations
    best_name, best_data = sorted_layouts[0]
    print(f"[BEST] BEST DETECTED KEYBOARD ARRANGEMENT: {best_name}")
    print(f"Cost: {best_data['cost']:.5f} ({((qwerty_cost - best_data['cost']) / qwerty_cost) * 100:.2f}% improvement over QWERTY)")
    print(visualize_layout(best_data["layout"]))
    print("=" * 70)
    
    return results

if __name__ == "__main__":
    run_simulation()
