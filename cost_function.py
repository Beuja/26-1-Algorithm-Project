# Cost = alpha * D + beta * F + gamma * P

import math
from layouts import (
    layout_str_to_coord_dict,
    layout_str_to_finger_dict,
    layout_str_to_hand_dict,
    FINGER_HOMES
)

def compute_frequencies(text: str):
    cleaned_text = [char.lower() for char in text if char.isalpha()]
    total_chars = len(cleaned_text)

    unigram_counts = {}
    for char in cleaned_text:
        unigram_counts[char] = unigram_counts.get(char, 0) + 1

    bigram_counts = {}
    for i in range(len(cleaned_text) - 1):
        c1, c2 = cleaned_text[i], cleaned_text[i+1]
        bigram_counts[(c1, c2)] = bigram_counts.get((c1, c2), 0) + 1

    return unigram_counts, bigram_counts, total_chars

def euclidean_distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def calculate_layout_cost_from_dicts(
    coords: dict,
    fingers: dict,
    hands: dict,
    unigram_counts: dict,
    bigram_counts: dict,
    total_chars: int,
    weights=(1.0, 2.0, 1.5),
) -> dict:
    # Dvorak·Colemak처럼 확장 좌표를 직접 넘길 때 사용
    alpha, beta, gamma = weights

    d_base = 0.0
    for char, count in unigram_counts.items():
        if char in coords:
            d_base += count * euclidean_distance(coords[char], FINGER_HOMES[fingers[char]])

    d_transition = 0.0
    for (c1, c2), count in bigram_counts.items():
        if c1 in coords and c2 in coords and fingers[c1] == fingers[c2]:
            d_transition += count * euclidean_distance(coords[c1], coords[c2])

    total_f = 0.0
    for (c1, c2), count in bigram_counts.items():
        if c1 in coords and c2 in coords and c1 != c2 and fingers[c1] == fingers[c2]:
            total_f += count

    total_p = 0.0
    for (c1, c2), count in bigram_counts.items():
        if c1 in coords and c2 in coords and hands[c1] == hands[c2]:
            total_p += count

    norm = max(1, total_chars)
    D_norm = (d_base + d_transition) / norm
    F_norm = total_f / norm
    P_norm = total_p / norm
    return {
        "total_cost": alpha * D_norm + beta * F_norm + gamma * P_norm,
        "D": D_norm, "F": F_norm, "P": P_norm,
    }


def calculate_layout_cost(layout_str: str, unigram_counts: dict, bigram_counts: dict, total_chars: int, weights=(1.0, 2.0, 1.5)) -> dict:
    coords  = layout_str_to_coord_dict(layout_str)
    fingers = layout_str_to_finger_dict(layout_str)
    hands   = layout_str_to_hand_dict(layout_str)
    return calculate_layout_cost_from_dicts(
        coords, fingers, hands, unigram_counts, bigram_counts, total_chars, weights
    )
