import random
import copy
from cost_function import calculate_layout_cost

ALPHABET = "abcdefghijklmnopqrstuvwxyz"

def get_random_layout() -> str:
    lst = list(ALPHABET)
    random.shuffle(lst)
    return "".join(lst)

def order_crossover(parent1: str, parent2: str) -> str:
    # OX 교차: parent1 구간 보존 후 나머지를 parent2 순서로 채움
    size = len(parent1)
    cx1 = random.randint(0, size - 2)
    cx2 = random.randint(cx1 + 1, size - 1)

    child = [None] * size
    child[cx1:cx2+1] = list(parent1[cx1:cx2+1])

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
    lst = list(layout)
    i, j = random.sample(range(len(lst)), 2)
    lst[i], lst[j] = lst[j], lst[i]
    return "".join(lst)

def mutate_inversion(layout: str) -> str:
    lst = list(layout)
    cx1 = random.randint(0, len(lst) - 2)
    cx2 = random.randint(cx1 + 1, len(lst) - 1)
    lst[cx1:cx2+1] = reversed(lst[cx1:cx2+1])
    return "".join(lst)

def select_tournament(population: list, fitnesses: list, tournament_size: int = 5) -> str:
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
    mutation_decay: float = 0.99,
    elitism_count: int = 5,
    tournament_size: int = 5,
    seed_layouts: list = None
) -> tuple:
    population = []

    if seed_layouts:
        for seed in seed_layouts:
            if len(seed) == 26:
                population.append(seed)

    while len(population) < pop_size:
        population.append(get_random_layout())

    history = []
    current_mutation_rate = mutation_rate

    for _ in range(generations):
        costs = []
        fitnesses = []
        for layout in population:
            cost_details = calculate_layout_cost(layout, unigram_counts, bigram_counts, total_chars, weights)
            cost_val = cost_details["total_cost"]
            costs.append(cost_val)
            fitnesses.append(1.0 / (cost_val + 1e-6))

        best_idx = min(range(pop_size), key=lambda idx: costs[idx])
        best_layout = population[best_idx]
        best_cost_val = costs[best_idx]
        history.append(best_cost_val)

        sorted_indices = sorted(range(pop_size), key=lambda idx: costs[idx])
        new_population = [population[idx] for idx in sorted_indices[:elitism_count]]

        while len(new_population) < pop_size:
            parent1 = select_tournament(population, fitnesses, tournament_size)
            parent2 = select_tournament(population, fitnesses, tournament_size)

            if random.random() < crossover_rate:
                child = order_crossover(parent1, parent2)
            else:
                child = parent1 if random.random() < 0.5 else parent2

            if random.random() < current_mutation_rate:
                if random.random() < 0.5:
                    child = mutate_swap(child)
                else:
                    child = mutate_inversion(child)

            new_population.append(child)

        population = new_population
        current_mutation_rate *= mutation_decay

    final_costs = [calculate_layout_cost(layout, unigram_counts, bigram_counts, total_chars, weights)["total_cost"] for layout in population]
    best_final_idx = min(range(pop_size), key=lambda idx: final_costs[idx])
    best_layout = population[best_final_idx]
    best_cost_details = calculate_layout_cost(best_layout, unigram_counts, bigram_counts, total_chars, weights)

    total_calls = pop_size * generations + pop_size + 1
    return best_layout, best_cost_details, history, total_calls

if __name__ == "__main__":
    p1 = ALPHABET
    p2 = ALPHABET[::-1]
    print(f"부모1: {p1}")
    print(f"부모2: {p2}")
    print(f"OX교차: {order_crossover(p1, p2)}")
    print(f"교환돌연변이: {mutate_swap(p1)}")
