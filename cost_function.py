# cost_function.py
"""
키보드 배열 최적화 비용 함수 구현.
[김호재 팀장 담당 모듈]

공식: Cost = alpha * D + beta * F + gamma * P
사전 집계된 문자 및 바이그램 빈도를 이용해 비용을 계산한다.
"""

import math
from layouts import (
    layout_str_to_coord_dict,
    layout_str_to_finger_dict,
    layout_str_to_hand_dict,
    FINGER_HOMES
)

def compute_frequencies(text: str):
    """
    텍스트를 전처리하고 유니그램 및 바이그램 빈도를 집계한다.
    소문자 알파벳 26자만 대상으로 한다 (N=26).
    """
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
    """두 2D 좌표 사이의 유클리드 거리를 계산한다."""
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
    """
    coords/fingers/hands 딕셔너리를 직접 받아 비용을 계산한다.
    Dvorak·Colemak 확장 좌표 계산에 사용.
    """
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
    """
    키보드 배열의 세부 비용을 계산하고 정규화하여 반환한다.

    매개변수
    --------
    layout_str : str
        26자 배열 문자열.
    unigram_counts : dict
        문자별 빈도수 딕셔너리.
    bigram_counts : dict
        연속 문자쌍별 빈도수 딕셔너리.
    total_chars : int
        텍스트 내 알파벳 문자 총 개수.
    weights : tuple
        (alpha, beta, gamma) 가중치 튜플.

    반환값
    ------
    dict
        다음 키를 포함하는 딕셔너리:
            'total_cost' : 최종 합산 비용 (Cost = alpha*D + beta*F + gamma*P)
            'D'          : 정규화된 이동 거리 비용
            'F'          : 정규화된 동일 손가락 연타 피로도
            'P'          : 정규화된 한 손 연속 타건 패널티
    """
    coords  = layout_str_to_coord_dict(layout_str)
    fingers = layout_str_to_finger_dict(layout_str)
    hands   = layout_str_to_hand_dict(layout_str)
    return calculate_layout_cost_from_dicts(
        coords, fingers, hands, unigram_counts, bigram_counts, total_chars, weights
    )
