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
    # 3행 (y=0.0) — 실제 키보드처럼 1행과 유사한 x좌표 (1행 기준 +1.0 오프셋)
    (1.0, 0.0), (2.0, 0.0), (3.0, 0.0), (4.0, 0.0), (5.0, 0.0),
    (6.0, 0.0), (7.0, 0.0)
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
# 슬롯 순서: Q(0)~P(9) → A(10)~L(18) → Z(19)~M(25)
QWERTY  = "qwertyuiopasdfghjklzxcvbnm"

# DVORAK: 실제 드보락 자판의 QWERTY 물리 슬롯 매핑.
# - 슬롯 3~9  (R~P):  p,y,f,g,c,r,l  ← 정확
# - 슬롯 10~18(A~L):  a,o,e,u,i,d,h,t,n ← 정확
# - 슬롯 20~25(X~M):  q,j,k,x,b,m    ← 정확
# - 슬롯 0,1,2(Q,W,E): 실제로는 ' , . (비알파벳) → s,w,v 근사 배치 (실제 위치는 ;,,,.로 우측)
# - 슬롯 19  (Z):     실제로는 ; (비알파벳)     → z  근사 배치 (실제 위치는 / 우측 하단)
# ※ s,w,v,z 4글자는 위치·손 배정 오차 있음 (특히 s: 실제 RF4 → 근사 LF4).
DVORAK  = "swvpyfgcrlaoeuidhtnzqjkxbm"

# COLEMAK: 실제 콜막 자판의 QWERTY 물리 슬롯 매핑.
# - 슬롯 9(P 위치): 실제 콜막은 ;(비알파벳). o는 실제 ;키 위치 → P슬롯에 근사 배치 (인접, 오차 소).
# 나머지 25글자는 실제 콜막 위치와 정확히 일치.
COLEMAK = "qwfpgjluyoarstdhneizxcvbkm"

# ══════════════════════════════════════════════════════════════════
# 확장 물리 좌표 — Dvorak / Colemak 실제 키 위치
# ══════════════════════════════════════════════════════════════════
# QWERTY 26슬롯에 없는 ';'(x=9.5,y=1), ','(x=8,y=0), '.'(x=9,y=0), '/'(x=10,y=0) 포함.
# 각 항목: (문자, (x, y), 손가락 코드, 손)
#
# Dvorak: Q/W/E 슬롯→' , . (비알파벳), Z슬롯→; (비알파벳) → 해당 위치 제외
#         s→';'키, w→','키, v→'.'키, z→'/'키 (실제 드보락 위치)
_DVORAK_TABLE = [
    # ── 1행: R~P 위치만 알파벳 (Q,W,E 슬롯은 비알파벳이므로 제외) ──
    ('p', (3.0, 2.0), 'LF1', 'L'),  ('y', (4.0, 2.0), 'LF1', 'L'),
    ('f', (5.0, 2.0), 'RF1', 'R'),  ('g', (6.0, 2.0), 'RF1', 'R'),
    ('c', (7.0, 2.0), 'RF2', 'R'),  ('r', (8.0, 2.0), 'RF3', 'R'),
    ('l', (9.0, 2.0), 'RF4', 'R'),
    # ── 2행: A~L + ';'키(확장) ──
    ('a', (0.5, 1.0), 'LF4', 'L'),  ('o', (1.5, 1.0), 'LF3', 'L'),
    ('e', (2.5, 1.0), 'LF2', 'L'),  ('u', (3.5, 1.0), 'LF1', 'L'),
    ('i', (4.5, 1.0), 'LF1', 'L'),  ('d', (5.5, 1.0), 'RF1', 'R'),
    ('h', (6.5, 1.0), 'RF1', 'R'),  ('t', (7.5, 1.0), 'RF2', 'R'),
    ('n', (8.5, 1.0), 'RF3', 'R'),  ('s', (9.5, 1.0), 'RF4', 'R'),  # ';' 확장
    # ── 3행: X~M + ','·'.'·'/'키(확장), Z슬롯은 비알파벳이므로 제외 ──
    ('q', (2.0, 0.0), 'LF3', 'L'),  ('j', (3.0, 0.0), 'LF2', 'L'),
    ('k', (4.0, 0.0), 'LF1', 'L'),  ('x', (5.0, 0.0), 'LF1', 'L'),
    ('b', (6.0, 0.0), 'RF1', 'R'),  ('m', (7.0, 0.0), 'RF1', 'R'),
    ('w', (8.0, 0.0), 'RF2', 'R'),  ('v', (9.0, 0.0), 'RF3', 'R'),  # ',' '.' 확장
    ('z', (10.0, 0.0), 'RF4', 'R'),                                   # '/' 확장
]
DVORAK_COORDS  = {c: xy for c, xy, f, h in _DVORAK_TABLE}
DVORAK_FINGERS = {c: f  for c, xy, f, h in _DVORAK_TABLE}
DVORAK_HANDS   = {c: h  for c, xy, f, h in _DVORAK_TABLE}

# Colemak: P슬롯→';'(비알파벳) 제외, 'o'는 실제 ';'키 위치(확장)에 배치
_COLEMAK_TABLE = [
    # ── 1행: Q~O 위치 (P슬롯은 비알파벳이므로 제외) ──
    ('q', (0.0, 2.0), 'LF4', 'L'),  ('w', (1.0, 2.0), 'LF3', 'L'),
    ('f', (2.0, 2.0), 'LF2', 'L'),  ('p', (3.0, 2.0), 'LF1', 'L'),
    ('g', (4.0, 2.0), 'LF1', 'L'),  ('j', (5.0, 2.0), 'RF1', 'R'),
    ('l', (6.0, 2.0), 'RF1', 'R'),  ('u', (7.0, 2.0), 'RF2', 'R'),
    ('y', (8.0, 2.0), 'RF3', 'R'),
    # ── 2행: A~L + ';'키(확장)에 'o' ──
    ('a', (0.5, 1.0), 'LF4', 'L'),  ('r', (1.5, 1.0), 'LF3', 'L'),
    ('s', (2.5, 1.0), 'LF2', 'L'),  ('t', (3.5, 1.0), 'LF1', 'L'),
    ('d', (4.5, 1.0), 'LF1', 'L'),  ('h', (5.5, 1.0), 'RF1', 'R'),
    ('n', (6.5, 1.0), 'RF1', 'R'),  ('e', (7.5, 1.0), 'RF2', 'R'),
    ('i', (8.5, 1.0), 'RF3', 'R'),  ('o', (9.5, 1.0), 'RF4', 'R'),  # ';' 확장
    # ── 3행: Z~M (QWERTY와 동일, N→k만 변경) ──
    ('z', (1.0, 0.0), 'LF4', 'L'),  ('x', (2.0, 0.0), 'LF3', 'L'),
    ('c', (3.0, 0.0), 'LF2', 'L'),  ('v', (4.0, 0.0), 'LF1', 'L'),
    ('b', (5.0, 0.0), 'LF1', 'L'),  ('k', (6.0, 0.0), 'RF1', 'R'),
    ('m', (7.0, 0.0), 'RF1', 'R'),
]
COLEMAK_COORDS  = {c: xy for c, xy, f, h in _COLEMAK_TABLE}
COLEMAK_FINGERS = {c: f  for c, xy, f, h in _COLEMAK_TABLE}
COLEMAK_HANDS   = {c: h  for c, xy, f, h in _COLEMAK_TABLE}


def visualize_layout_from_table(table: list) -> str:
    """확장 레이아웃 테이블(list of (char,coord,finger,hand))을 행별로 출력한다."""
    rows = {2.0: [], 1.0: [], 0.0: []}
    for char, (x, y), _, _ in table:
        rows[y].append((x, char))
    lines = []
    for y, label, indent in [(2.0, "Row 1", ""), (1.0, "Row 2", "  "), (0.0, "Row 3", "    ")]:
        keys = " ".join(c for _, c in sorted(rows[y]))
        lines.append(f"[{label}] {indent}{keys}")
    return "\n".join(lines)


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
