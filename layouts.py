# 스태거드 키보드 알파벳 26키 물리 좌표 (행별 x 오프셋 반영)
# 1행(y=2): Q~P  2행(y=1): A~L  3행(y=0): Z~M
PHYSICAL_COORDINATES = [
    (0.0, 2.0), (1.0, 2.0), (2.0, 2.0), (3.0, 2.0), (4.0, 2.0),
    (5.0, 2.0), (6.0, 2.0), (7.0, 2.0), (8.0, 2.0), (9.0, 2.0),
    (0.5, 1.0), (1.5, 1.0), (2.5, 1.0), (3.5, 1.0), (4.5, 1.0),
    (5.5, 1.0), (6.5, 1.0), (7.5, 1.0), (8.5, 1.0),
    (1.0, 0.0), (2.0, 0.0), (3.0, 0.0), (4.0, 0.0), (5.0, 0.0),
    (6.0, 0.0), (7.0, 0.0)
]

# LF4=왼새끼  LF3=왼약지  LF2=왼중지  LF1=왼검지
# RF1=오른검지  RF2=오른중지  RF3=오른약지  RF4=오른새끼
PHYSICAL_FINGERS = [
    "LF4", "LF3", "LF2", "LF1", "LF1", "RF1", "RF1", "RF2", "RF3", "RF4",
    "LF4", "LF3", "LF2", "LF1", "LF1", "RF1", "RF1", "RF2", "RF3",
    "LF4", "LF3", "LF2", "LF1", "LF1", "RF1", "RF1"
]

PHYSICAL_HANDS = [
    "L", "L", "L", "L", "L", "R", "R", "R", "R", "R",
    "L", "L", "L", "L", "L", "R", "R", "R", "R",
    "L", "L", "L", "L", "L", "R", "R"
]

FINGER_HOMES = {
    "LF4": (0.5, 1.0),   # a
    "LF3": (1.5, 1.0),   # s
    "LF2": (2.5, 1.0),   # d
    "LF1": (3.5, 1.0),   # f
    "RF1": (6.5, 1.0),   # j
    "RF2": (7.5, 1.0),   # k
    "RF3": (8.5, 1.0),   # l
    "RF4": (9.5, 1.0)    # ; (알파벳 밖 키지만 홈포지션 좌표 필요)
}

# 슬롯 i = QWERTY i번 키 위치에 배치된 문자 (Q=0 ... M=25)
QWERTY  = "qwertyuiopasdfghjklzxcvbnm"

# Dvorak: Q/W/E/Z 슬롯은 실제로 비알파벳(', ,, ., ;) → 근사 배치
DVORAK  = "swvpyfgcrlaoeuidhtnzqjkxbm"

# Colemak: P 슬롯이 ;(비알파벳), o는 ; 위치 → P 슬롯에 근사 배치
COLEMAK = "qwfpgjluyoarstdhneizxcvbkm"

# ── 확장 좌표: Dvorak/Colemak 실제 물리 위치 (;, ,, ., / 키 포함) ──
# (문자, (x, y), 손가락, 손)

# Dvorak: Q/W/E/Z 슬롯 제외, s→; w→, v→. z→/ 위치
_DVORAK_TABLE = [
    ('p', (3.0, 2.0), 'LF1', 'L'),  ('y', (4.0, 2.0), 'LF1', 'L'),
    ('f', (5.0, 2.0), 'RF1', 'R'),  ('g', (6.0, 2.0), 'RF1', 'R'),
    ('c', (7.0, 2.0), 'RF2', 'R'),  ('r', (8.0, 2.0), 'RF3', 'R'),
    ('l', (9.0, 2.0), 'RF4', 'R'),
    ('a', (0.5, 1.0), 'LF4', 'L'),  ('o', (1.5, 1.0), 'LF3', 'L'),
    ('e', (2.5, 1.0), 'LF2', 'L'),  ('u', (3.5, 1.0), 'LF1', 'L'),
    ('i', (4.5, 1.0), 'LF1', 'L'),  ('d', (5.5, 1.0), 'RF1', 'R'),
    ('h', (6.5, 1.0), 'RF1', 'R'),  ('t', (7.5, 1.0), 'RF2', 'R'),
    ('n', (8.5, 1.0), 'RF3', 'R'),  ('s', (9.5, 1.0), 'RF4', 'R'),  # ; 위치
    ('q', (2.0, 0.0), 'LF3', 'L'),  ('j', (3.0, 0.0), 'LF2', 'L'),
    ('k', (4.0, 0.0), 'LF1', 'L'),  ('x', (5.0, 0.0), 'LF1', 'L'),
    ('b', (6.0, 0.0), 'RF1', 'R'),  ('m', (7.0, 0.0), 'RF1', 'R'),
    ('w', (8.0, 0.0), 'RF2', 'R'),  ('v', (9.0, 0.0), 'RF3', 'R'),  # , . 위치
    ('z', (10.0, 0.0), 'RF4', 'R'),                                   # / 위치
]
DVORAK_COORDS  = {c: xy for c, xy, _, _ in _DVORAK_TABLE}
DVORAK_FINGERS = {c: f  for c, _,  f, _ in _DVORAK_TABLE}
DVORAK_HANDS   = {c: h  for c, _,  _, h in _DVORAK_TABLE}

# Colemak: P 슬롯 제외, o는 ; 위치
_COLEMAK_TABLE = [
    ('q', (0.0, 2.0), 'LF4', 'L'),  ('w', (1.0, 2.0), 'LF3', 'L'),
    ('f', (2.0, 2.0), 'LF2', 'L'),  ('p', (3.0, 2.0), 'LF1', 'L'),
    ('g', (4.0, 2.0), 'LF1', 'L'),  ('j', (5.0, 2.0), 'RF1', 'R'),
    ('l', (6.0, 2.0), 'RF1', 'R'),  ('u', (7.0, 2.0), 'RF2', 'R'),
    ('y', (8.0, 2.0), 'RF3', 'R'),
    ('a', (0.5, 1.0), 'LF4', 'L'),  ('r', (1.5, 1.0), 'LF3', 'L'),
    ('s', (2.5, 1.0), 'LF2', 'L'),  ('t', (3.5, 1.0), 'LF1', 'L'),
    ('d', (4.5, 1.0), 'LF1', 'L'),  ('h', (5.5, 1.0), 'RF1', 'R'),
    ('n', (6.5, 1.0), 'RF1', 'R'),  ('e', (7.5, 1.0), 'RF2', 'R'),
    ('i', (8.5, 1.0), 'RF3', 'R'),  ('o', (9.5, 1.0), 'RF4', 'R'),  # ; 위치
    ('z', (1.0, 0.0), 'LF4', 'L'),  ('x', (2.0, 0.0), 'LF3', 'L'),
    ('c', (3.0, 0.0), 'LF2', 'L'),  ('v', (4.0, 0.0), 'LF1', 'L'),
    ('b', (5.0, 0.0), 'LF1', 'L'),  ('k', (6.0, 0.0), 'RF1', 'R'),
    ('m', (7.0, 0.0), 'RF1', 'R'),
]
COLEMAK_COORDS  = {c: xy for c, xy, _, _ in _COLEMAK_TABLE}
COLEMAK_FINGERS = {c: f  for c, _,  f, _ in _COLEMAK_TABLE}
COLEMAK_HANDS   = {c: h  for c, _,  _, h in _COLEMAK_TABLE}


def visualize_layout_from_table(table: list) -> str:
    rows = {2.0: [], 1.0: [], 0.0: []}
    for char, (x, y), _, _ in table:
        rows[y].append((x, char))
    lines = []
    for y, label, indent in [(2.0, "Row 1", ""), (1.0, "Row 2", "  "), (0.0, "Row 3", "    ")]:
        keys = " ".join(c for _, c in sorted(rows[y]))
        lines.append(f"[{label}] {indent}{keys}")
    return "\n".join(lines)


def layout_str_to_coord_dict(layout_str: str) -> dict:
    assert len(layout_str) == 26
    return {char: PHYSICAL_COORDINATES[i] for i, char in enumerate(layout_str)}

def layout_str_to_finger_dict(layout_str: str) -> dict:
    assert len(layout_str) == 26
    return {char: PHYSICAL_FINGERS[i] for i, char in enumerate(layout_str)}

def layout_str_to_hand_dict(layout_str: str) -> dict:
    assert len(layout_str) == 26
    return {char: PHYSICAL_HANDS[i] for i, char in enumerate(layout_str)}

def visualize_layout(layout_str: str) -> str:
    assert len(layout_str) == 26
    row1 = " ".join(layout_str[0:10])
    row2 = "  " + " ".join(layout_str[10:19])
    row3 = "    " + " ".join(layout_str[19:26])
    return f"[Row 1] {row1}\n[Row 2] {row2}\n[Row 3] {row3}"

if __name__ == "__main__":
    print("QWERTY:")
    print(visualize_layout(QWERTY))
    print("\nDVORAK:")
    print(visualize_layout_from_table(_DVORAK_TABLE))
    print("\nCOLEMAK:")
    print(visualize_layout_from_table(_COLEMAK_TABLE))