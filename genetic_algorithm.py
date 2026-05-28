# genetic_algorithm.py
"""
Genetic Algorithm (GA) implementation for keyboard layout optimization.
Uses Order Crossover (OX), Swap/Inversion Mutation, Tournament Selection, and Elitism.
"""

import random
import copy
from cost_function import calculate_layout_cost

ALPHABET = "abcdefghijklmnopqrstuvwxyz"

def get_random_layout() -> str:
    """Generates a random permutation of the 26 alphabets as a layout string."""
    lst = list(ALPHABET)
    random.shuffle(lst)
    return "".join(lst)

def order_crossover(parent1: str, parent2: str) -> str:
    """
    Implements Order Crossover (OX) for 26-character permutation layouts.
    Preserves the relative ordering of a subset of keys from parent 1,
    then fills the remaining slots using parent 2's elements.
    """
    size = len(parent1)
    # Pick two cut points
    cx1 = random.randint(0, size - 2)
    cx2 = random.randint(cx1 + 1, size - 1)
    
    # Initialize child with None
    child = [None] * size
    
    # Copy segment from parent1 to child
    child[cx1:cx2+1] = list(parent1[cx1:cx2+1])
    
    # Fill the remaining slots with parent2 elements, wrapping around from cx2+1
    p2_idx = (cx2 + 1) % size
    child_idx = (cx2 + 1) % size
    
    filled_count = cx2 - cx1 + 1
    
    while filled_count < size:
        char_to_insert = parent2[p2_idx]
        if char_to_insert not in child:
            child[child_idx] = char_to_insert
            child_idx = (child_idx + 1) % size
            filled_count += 1
        p2_idx = (p2_idx + 1) % size
        
    return "".join(child)

def mutate_swap(layout: str) -> str:
    """Mutates a layout by swapping the positions of two random keys."""
    lst = list(layout)
    i, j = random.sample(range(len(lst)), 2)
    lst[i], lst[j] = lst[j], lst[i]
    return "".join(lst)

def mutate_inversion(layout: str) -> str:
    """Mutates a layout by reversing the order of a random sub-segment."""
    lst = list(layout)
    cx1 = random.randint(0, len(lst) - 2)
    cx2 = random.randint(cx1 + 1, len(lst) - 1)
    lst[cx1:cx2+1] = reversed(lst[cx1:cx2+1])
    return "".join(lst)

def select_tournament(population: list, fitnesses: list, tournament_size: int = 5) -> str:
    """Selects a layout using Tournament Selection."""
    selected_indices = random.sample(range(len(population)), tournament_size)
    best_idx = max(selected_indices, key=lambda idx: fitnesses[idx])
    return population[best_idx]

def run_genetic_algorithm(
    unigram_counts: dict,
    bigram_counts: dict,
    total_chars: int,
    weights: tuple = (1.0, 2.0, 1.5),
    pop_size: int = 100,
    generations: int = 150,
    crossover_rate: float = 0.8,
    mutation_rate: float = 0.2,
    mutation_decay: float = 0.99,  # reduce mutation rate gradually
    elitism_count: int = 5,
    tournament_size: int = 5,
    seed_layouts: list = None
) -> tuple:
    """
    Runs the Genetic Algorithm to optimize the keyboard layout.
    
    Parameters:
        unigram_counts, bigram_counts, total_chars: Precalculated corpus statistics.
        weights: (alpha, beta, gamma) weights for cost calculation.
        pop_size: Population size.
        generations: Number of generations.
        crossover_rate: Probability of crossover.
        mutation_rate: Initial probability of mutation.
        mutation_decay: Decaying factor for mutation rate per generation.
        elitism_count: Number of top individuals to preserve.
        tournament_size: Group size for tournament selection.
        seed_layouts: List of strings representing pre-existing layouts to inject.
        
    Returns:
        best_layout: The optimized 26-character layout string.
        best_cost: The cost dictionary of the best layout.
        history: List of floats representing the best cost at each generation.
    """
    # 1. Initialize population
    population = []
    
    # Inject seeds (e.g., QWERTY, Dvorak, Colemak) if provided
    if seed_layouts:
        for seed in seed_layouts:
            if len(seed) == 26:
                population.append(seed)
                
    # Fill remaining population with random layouts
    while len(population) < pop_size:
        population.append(get_random_layout())
        
    history = []
    current_mutation_rate = mutation_rate
    
    # Optimization loop
    for gen in range(generations):
        # Calculate cost and fitness for each layout
        # Fitness = 1.0 / (Cost + 1e-6)
        costs = []
        fitnesses = []
        for layout in population:
            cost_details = calculate_layout_cost(layout, unigram_counts, bigram_counts, total_chars, weights)
            cost_val = cost_details["total_cost"]
            costs.append(cost_val)
            fitnesses.append(1.0 / (cost_val + 1e-6))
            
        # Find best layout in current generation
        best_idx = min(range(pop_size), key=lambda idx: costs[idx])
        best_layout = population[best_idx]
        best_cost_val = costs[best_idx]
        history.append(best_cost_val)
        
        # Elitism: preserve top individuals
        sorted_indices = sorted(range(pop_size), key=lambda idx: costs[idx])
        new_population = [population[idx] for idx in sorted_indices[:elitism_count]]
        
        # Generate the rest of the new population
        while len(new_population) < pop_size:
            # 1. Selection
            parent1 = select_tournament(population, fitnesses, tournament_size)
            parent2 = select_tournament(population, fitnesses, tournament_size)
            
            # 2. Crossover
            if random.random() < crossover_rate:
                child = order_crossover(parent1, parent2)
            else:
                child = parent1 if random.random() < 0.5 else parent2
                
            # 3. Mutation
            if random.random() < current_mutation_rate:
                if random.random() < 0.5:
                    child = mutate_swap(child)
                else:
                    child = mutate_inversion(child)
                    
            new_population.append(child)
            
        population = new_population
        current_mutation_rate *= mutation_decay
        
    # Evaluate final population
    final_costs = [calculate_layout_cost(layout, unigram_counts, bigram_counts, total_chars, weights)["total_cost"] for layout in population]
    best_final_idx = min(range(pop_size), key=lambda idx: final_costs[idx])
    best_layout = population[best_final_idx]
    best_cost_details = calculate_layout_cost(best_layout, unigram_counts, bigram_counts, total_chars, weights)
    
    return best_layout, best_cost_details, history

if __name__ == "__main__":
    # Small test code to check crossover and mutations
    p1 = ALPHABET
    p2 = ALPHABET[::-1]
    print("OX Crossover:")
    print(f"P1: {p1}")
    print(f"P2: {p2}")
    print(f"CH: {order_crossover(p1, p2)}")
    
    print("\nMutation (Swap):")
    print(f"IN: {p1}")
    print(f"MU: {mutate_swap(p1)}")
