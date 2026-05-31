# genetic_algorithm.py
"""
키보드 배열 최적화를 위한 유전 알고리즘(GA) 구현.
[정종욱 팀원 담당 모듈]

순서 교차(OX), 교환/역전 돌연변이, 토너먼트 선택, 엘리티즘을 사용한다.
"""

import random
import copy
from cost_function import calculate_layout_cost

ALPHABET = "abcdefghijklmnopqrstuvwxyz"

def get_random_layout() -> str:
    """알파벳 26자를 랜덤으로 섞어 배열 문자열을 생성한다."""
    lst = list(ALPHABET)
    random.shuffle(lst)
    return "".join(lst)

def order_crossover(parent1: str, parent2: str) -> str:
    """
    26자 순열 배열에 대한 순서 교차(OX, Order Crossover)를 수행한다.
    부모1에서 일부 구간의 키 순서를 보존하고,
    나머지 슬롯은 부모2의 요소로 순서대로 채운다.
    """
    size = len(parent1)
    # 두 교차점 선택
    cx1 = random.randint(0, size - 2)
    cx2 = random.randint(cx1 + 1, size - 1)

    # 자식 배열을 None으로 초기화
    child = [None] * size

    # 부모1의 구간을 자식에 복사
    child[cx1:cx2+1] = list(parent1[cx1:cx2+1])

    # 나머지 슬롯을 부모2 요소로 cx2+1부터 순환하며 채움
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
    """랜덤하게 선택한 두 키의 위치를 교환하는 돌연변이."""
    lst = list(layout)
    i, j = random.sample(range(len(lst)), 2)
    lst[i], lst[j] = lst[j], lst[i]
    return "".join(lst)

def mutate_inversion(layout: str) -> str:
    """랜덤하게 선택한 부분 구간의 순서를 역전시키는 돌연변이."""
    lst = list(layout)
    cx1 = random.randint(0, len(lst) - 2)
    cx2 = random.randint(cx1 + 1, len(lst) - 1)
    lst[cx1:cx2+1] = reversed(lst[cx1:cx2+1])
    return "".join(lst)

def select_tournament(population: list, fitnesses: list, tournament_size: int = 5) -> str:
    """토너먼트 선택으로 다음 세대의 부모 배열을 선택한다."""
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
    mutation_decay: float = 0.99,  # 세대마다 돌연변이율을 점진적으로 감소
    elitism_count: int = 5,
    tournament_size: int = 5,
    seed_layouts: list = None
) -> tuple:
    """
    유전 알고리즘으로 키보드 배열을 최적화한다.

    매개변수
    --------
    unigram_counts, bigram_counts, total_chars : 사전 계산된 코퍼스 통계.
    weights : (alpha, beta, gamma) 비용 계산 가중치.
    pop_size : 집단(population) 크기.
    generations : 세대 수.
    crossover_rate : 교차 발생 확률.
    mutation_rate : 초기 돌연변이 발생 확률.
    mutation_decay : 세대마다 돌연변이율에 곱해지는 감소 계수.
    elitism_count : 다음 세대에 그대로 보존할 상위 개체 수.
    tournament_size : 토너먼트 선택의 그룹 크기.
    seed_layouts : 초기 집단에 주입할 기존 배열 목록 (예: QWERTY, Dvorak).

    반환값
    ------
    best_layout : str
        최적화된 26자 배열 문자열.
    best_cost : dict
        최적 배열의 비용 딕셔너리.
    history : list[float]
        세대마다 기록된 최적 비용 목록.
    """
    # 1. 초기 집단 생성
    population = []

    # 시드 배열(QWERTY, Dvorak, Colemak 등) 주입
    if seed_layouts:
        for seed in seed_layouts:
            if len(seed) == 26:
                population.append(seed)

    # 나머지는 랜덤 배열로 채움
    while len(population) < pop_size:
        population.append(get_random_layout())

    history = []
    current_mutation_rate = mutation_rate

    # 최적화 반복 루프
    for gen in range(generations):
        # 각 배열의 비용과 적합도 계산
        # 적합도 = 1.0 / (비용 + 1e-6) — 비용이 낮을수록 적합도 높음
        costs = []
        fitnesses = []
        for layout in population:
            cost_details = calculate_layout_cost(layout, unigram_counts, bigram_counts, total_chars, weights)
            cost_val = cost_details["total_cost"]
            costs.append(cost_val)
            fitnesses.append(1.0 / (cost_val + 1e-6))

        # 현재 세대 최적 배열 탐색
        best_idx = min(range(pop_size), key=lambda idx: costs[idx])
        best_layout = population[best_idx]
        best_cost_val = costs[best_idx]
        history.append(best_cost_val)

        # 엘리티즘: 상위 개체를 다음 세대에 그대로 보존
        sorted_indices = sorted(range(pop_size), key=lambda idx: costs[idx])
        new_population = [population[idx] for idx in sorted_indices[:elitism_count]]

        # 나머지 새 개체 생성
        while len(new_population) < pop_size:
            # 1단계: 선택
            parent1 = select_tournament(population, fitnesses, tournament_size)
            parent2 = select_tournament(population, fitnesses, tournament_size)

            # 2단계: 교차
            if random.random() < crossover_rate:
                child = order_crossover(parent1, parent2)
            else:
                child = parent1 if random.random() < 0.5 else parent2

            # 3단계: 돌연변이
            if random.random() < current_mutation_rate:
                if random.random() < 0.5:
                    child = mutate_swap(child)
                else:
                    child = mutate_inversion(child)

            new_population.append(child)

        population = new_population
        current_mutation_rate *= mutation_decay  # 돌연변이율 점진 감소

    # 최종 집단 평가
    final_costs = [calculate_layout_cost(layout, unigram_counts, bigram_counts, total_chars, weights)["total_cost"] for layout in population]
    best_final_idx = min(range(pop_size), key=lambda idx: final_costs[idx])
    best_layout = population[best_final_idx]
    best_cost_details = calculate_layout_cost(best_layout, unigram_counts, bigram_counts, total_chars, weights)

    total_calls = pop_size * generations + pop_size + 1  # 세대별 + 최종평가 + 최종 1회
    return best_layout, best_cost_details, history, total_calls

if __name__ == "__main__":
    # 교차 및 돌연변이 동작 확인용 간단 테스트
    p1 = ALPHABET
    p2 = ALPHABET[::-1]
    print("순서 교차(OX):")
    print(f"부모1: {p1}")
    print(f"부모2: {p2}")
    print(f"자식 : {order_crossover(p1, p2)}")

    print("\n돌연변이 (교환):")
    print(f"입력: {p1}")
    print(f"출력: {mutate_swap(p1)}")
