# layouts.py
"""
키보드 배열 정의, 물리적 그리드, 손가락 배정,
그리고 기준 배열(QWERTY, Dvorak, Colemak) 모듈.
[김호재 팀장 담당 모듈]
"""

# 표준 스태거드 키보드 기준 알파벳 26키의 2D 물리 좌표.
# 1행 (y=2): 10키 (q~p)
# 2행 (y=1):  9키 (a~l)
# 3행 (y=0):  7키 (z~m)
PHYSICAL_COORDINATES = [
    # 1행 (y=2.0)
    (0.0, 2.0), (1.0, 2.0), (2.0, 2.0), (3.0, 2.0), (4.0, 2.0),
    (5.0, 2.0), (6.0, 2.0), (7.0, 2.0), (8.0, 2.0), (9.0, 2.0),
    # 2행 (y=1.0)
    (0.5, 1.0), (1.5, 1.0), (2.5, 1.0), (3.5, 1.0), (4.5, 1.0),
    (5.5, 1.0), (6.5, 1.0), (7.5, 1.0), (8.5, 1.0),
    # 3행 (y=0.0)
    (1.5, 0.0), (2.5, 0.0), (3.5, 0.0), (4.5, 0.0), (5.5, 0.0),
    (6.5, 0.0), (7.5, 0.0)
]

# 표준 터치 타이핑 기준 손가락 배정.
# LF4: 왼쪽 새끼손가락, LF3: 왼쪽 약지, LF2: 왼쪽 중지, LF1: 왼쪽 검지
# RF1: 오른쪽 검지,     RF2: 오른쪽 중지, RF3: 오른쪽 약지, RF4: 오른쪽 새끼손가락
PHYSICAL_FINGERS = [
    # 1행
    "LF4", "LF3", "LF2", "LF1", "LF1", "RF1", "RF1", "RF2", "RF3", "RF4",
    # 2행
    "LF4", "LF3", "LF2", "LF1", "LF1", "RF1", "RF1", "RF2", "RF3",
    # 3행
    "LF4", "LF3", "LF2", "LF1", "LF1", "RF1", "RF1"
]

# 손 배정: 'L' = 왼손, 'R' = 오른손
PHYSICAL_HANDS = [
    # 1행
    "L", "L", "L", "L", "L", "R", "R", "R", "R", "R",
    # 2행
    "L", "L", "L", "L", "L", "R", "R", "R", "R",
    # 3행
    "L", "L", "L", "L", "L", "R", "R"
]

# 8개 손가락의 홈포지션(휴식 위치) 좌표
FINGER_HOMES = {
    "LF4": (0.5, 1.0),  # 'a' 위 (위치 10)
    "LF3": (1.5, 1.0),  # 's' 위 (위치 11)
    "LF2": (2.5, 1.0),  # 'd' 위 (위치 12)
    "LF1": (3.5, 1.0),  # 'f' 위 (위치 13)
    "RF1": (6.5, 1.0),  # 'j' 위 (위치 16)
    "RF2": (7.5, 1.0),  # 'k' 위 (위치 17)
    "RF3": (8.5, 1.0),  # 'l' 위 (위치 18)
    "RF4": (9.5, 1.0)   # ';' 위 (26자 알파벳 밖이지만 물리 좌표 존재)
}

# 기준 배열 3종 — 26자 문자열로 표현.
# 문자열의 i번째 문자가 i번 슬롯(0~25)에 배치된 키를 나타낸다.
QWERTY  = "qwertyuiopasdfghjklzxcvbnm"
DVORAK  = "pyfgcrlaoeuidhtnsqjkxbmwvz"
COLEMAK = "qwfpgjlyuioarstdhnezkxbmvc"

def layout_str_to_coord_dict(layout_str: str) -> dict:
    """26자 배열 문자열을 {문자: (x, y)} 딕셔너리로 변환한다."""
    assert len(layout_str) == 26, "배열 문자열은 정확히 26자여야 합니다."
    return {char: PHYSICAL_COORDINATES[i] for i, char in enumerate(layout_str)}

def layout_str_to_finger_dict(layout_str: str) -> dict:
    """26자 배열 문자열을 {문자: 손가락 코드} 딕셔너리로 변환한다."""
    assert len(layout_str) == 26, "배열 문자열은 정확히 26자여야 합니다."
    return {char: PHYSICAL_FINGERS[i] for i, char in enumerate(layout_str)}

def layout_str_to_hand_dict(layout_str: str) -> dict:
    """26자 배열 문자열을 {문자: 손('L' 또는 'R')} 딕셔너리로 변환한다."""
    assert len(layout_str) == 26, "배열 문자열은 정확히 26자여야 합니다."
    return {char: PHYSICAL_HANDS[i] for i, char in enumerate(layout_str)}

def visualize_layout(layout_str: str) -> str:
    """키보드 배열을 3행으로 보기 좋게 출력하는 문자열을 반환한다."""
    assert len(layout_str) == 26, "배열 문자열은 정확히 26자여야 합니다."
    row1 = " ".join(layout_str[0:10])
    row2 = "  " + " ".join(layout_str[10:19])
    row3 = "    " + " ".join(layout_str[19:26])
    return f"[Row 1] {row1}\n[Row 2] {row2}\n[Row 3] {row3}"

if __name__ == "__main__":
    print("QWERTY:")
    print(visualize_layout(QWERTY))
    print("\nDVORAK:")
    print(visualize_layout(DVORAK))
    print("\nCOLEMAK:")
    print(visualize_layout(COLEMAK))
