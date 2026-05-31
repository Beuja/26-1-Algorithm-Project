# simulated_annealing.py
"""
키보드 배열 최적화를 위한 담금질 기법(Simulated Annealing) 구현.
[박서연 팀원 담당 모듈]

탐색 전략: 메트로폴리스 기준 기반 확률적 탐색.
  - 초기 배열(기본값: QWERTY)에서 시작한다.
  - 매 반복마다 두 키를 랜덤 교환하여 이웃 배열을 생성한다.
  - 비용이 줄면 항상 채택, 비용이 늘어도 exp(-ΔE/T) 확률로 채택하여 지역 최솟값 탈출.
  - 온도 T는 매 반복마다 기하급수적으로 감소한다 (기하 냉각 스케줄).
  - 현재 탐색 경로와 별개로 전역 최적해를 별도로 추적한다.
"""

import math
import random
from layouts import QWERTY
from cost_function import calculate_layout_cost

_ALPHABET = list("abcdefghijklmnopqrstuvwxyz")


def _random_swap(layout: str) -> str:
    """랜덤하게 선택한 두 키를 교환한 새 배열을 반환한다."""
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
    담금질 기법으로 최적 키보드 배열을 탐색한다.

    매개변수
    --------
    unigram_counts : dict
        코퍼스 전처리로 얻은 {문자: 빈도수} 딕셔너리.
    bigram_counts : dict
        코퍼스 전처리로 얻은 {(c1, c2): 빈도수} 딕셔너리.
    total_chars : int
        코퍼스 내 알파벳 문자 총 개수.
    weights : tuple
        (alpha, beta, gamma) 비용 구성 요소 가중치.
    initial_temp : float
        냉각 스케줄의 초기 온도.
    cooling_rate : float
        매 반복마다 곱해지는 냉각 계수 (0 < rate < 1).
        T_{t+1} = T_t * cooling_rate
    iterations : int
        최대 반복 횟수.
    min_temp : float
        온도 하한선 — T가 이 값 이하로 내려가면 조기 종료.
    seed_layout : str, optional
        시작 배열 문자열(26자). 기본값은 QWERTY.
    record_interval : int
        매 N 반복마다 최적 비용을 히스토리에 기록한다.
        값이 작을수록 수렴 곡선이 부드럽지만 데이터가 많아진다.
    verbose : bool
        True이면 500 반복마다 진행 상황을 출력한다.

    반환값
    ------
    best_layout : str
        실행 중 발견된 최적 26자 배열 문자열.
    best_cost_details : dict
        최적 배열의 {'total_cost', 'D', 'F', 'P'} 딕셔너리.
    history : list[float]
        record_interval마다 샘플링한 최적 비용 목록 (수렴 곡선용).
    """
    # 시드 배열 또는 QWERTY에서 초기화
    current_layout = seed_layout if (seed_layout and len(seed_layout) == 26) else QWERTY
    current_cost = calculate_layout_cost(
        current_layout, unigram_counts, bigram_counts, total_chars, weights
    )["total_cost"]

    best_layout = current_layout
    best_cost = current_cost

    temp = initial_temp
    history = [best_cost]

    accepted = 0   # 채택된 이웃 수 (개선 + 확률적 채택 포함)
    improved = 0   # 실제 비용이 줄어든 채택 수

    for step in range(1, iterations + 1):
        if temp < min_temp:
            if verbose:
                print(f"      {step}번째 스텝에서 조기 종료: T={temp:.2e} < min_temp")
            break

        # 두 키를 랜덤 교환하여 이웃 배열 생성
        neighbor_layout = _random_swap(current_layout)
        neighbor_cost = calculate_layout_cost(
            neighbor_layout, unigram_counts, bigram_counts, total_chars, weights
        )["total_cost"]

        # 메트로폴리스 채택 기준
        delta_e = neighbor_cost - current_cost
        if delta_e < 0:
            # 비용 감소 → 항상 채택
            current_layout = neighbor_layout
            current_cost = neighbor_cost
            accepted += 1
            improved += 1
        elif temp > 0 and random.random() < math.exp(-delta_e / temp):
            # 비용 증가지만 e^{-dE/T} 확률로 채택 (지역 최솟값 탈출)
            current_layout = neighbor_layout
            current_cost = neighbor_cost
            accepted += 1

        # 전역 최적해 갱신
        if current_cost < best_cost:
            best_cost = current_cost
            best_layout = current_layout

        # 기하 냉각
        temp *= cooling_rate

        # 수렴 데이터 기록
        if step % record_interval == 0:
            history.append(best_cost)

        if verbose and step % 500 == 0:
            print(
                f"      스텝 {step:>5} | T={temp:.4f} | "
                f"최적={best_cost:.6f} | 채택={accepted}"
            )

    # 마지막 최적 비용이 히스토리에 반드시 포함되도록 보장
    if history[-1] != best_cost:
        history.append(best_cost)

    if verbose:
        print(f"      총 채택: {accepted} / {iterations} "
              f"({100*accepted/iterations:.1f}%) | 개선: {improved}")

    total_calls = step + 2  # 초기 1회 + 루프 step회 + 최종 1회
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

    print("=" * 50)
    print(" 담금질 기법 - 동작 테스트")
    print("=" * 50)

    layout, cost_details, hist = run_simulated_annealing(
        unigrams, bigrams, total,
        weights=(1.0, 2.0, 1.5),
        initial_temp=10.0,
        cooling_rate=0.995,
        iterations=5000,
        verbose=True,
    )

    print(f"\n최적 배열    : {layout}")
    print(visualize_layout(layout))
    print(f"\n총 비용      : {cost_details['total_cost']:.6f}")
    print(f"  D (이동거리): {cost_details['D']:.6f}")
    print(f"  F (피로도)  : {cost_details['F']:.6f}")
    print(f"  P (패널티)  : {cost_details['P']:.6f}")
    print(f"기록 포인트  : {len(hist)}개 스텝")

    # 기준 배열과 비교
    print("\n--- 기준 배열 비교 ---")
    for name, bl in [("QWERTY", QWERTY), ("DVORAK", DVORAK), ("COLEMAK", COLEMAK)]:
        c = calculate_layout_cost(bl, unigrams, bigrams, total)["total_cost"]
        print(f"{name:<8}: {c:.6f}")
    print(f"SA 결과     : {cost_details['total_cost']:.6f}")
