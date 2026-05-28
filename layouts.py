# layouts.py
"""
Keyboard layout definitions, physical grids, finger assignments,
and baseline layouts (QWERTY, Dvorak, Colemak) for the optimization project.
"""

# Physical 2D Coordinates for the 26 alphabetic keys based on standard staggered keyboard.
# Row 1 (y=2): 10 keys (q to p)
# Row 2 (y=1): 9 keys (a to l)
# Row 3 (y=0): 7 keys (z to m)
PHYSICAL_COORDINATES = [
    # Row 1 (y=2.0)
    (0.0, 2.0), (1.0, 2.0), (2.0, 2.0), (3.0, 2.0), (4.0, 2.0),
    (5.0, 2.0), (6.0, 2.0), (7.0, 2.0), (8.0, 2.0), (9.0, 2.0),
    # Row 2 (y=1.0)
    (0.5, 1.0), (1.5, 1.0), (2.5, 1.0), (3.5, 1.0), (4.5, 1.0),
    (5.5, 1.0), (6.5, 1.0), (7.5, 1.0), (8.5, 1.0),
    # Row 3 (y=0.0)
    (1.5, 0.0), (2.5, 0.0), (3.5, 0.0), (4.5, 0.0), (5.5, 0.0),
    (6.5, 0.0), (7.5, 0.0)
]

# Physical Finger assignments for standard touch-typing
# LF4: Left Pinky, LF3: Left Ring, LF2: Left Middle, LF1: Left Index
# RF1: Right Index, RF2: Right Middle, RF3: Right Ring, RF4: Right Pinky
PHYSICAL_FINGERS = [
    # Row 1
    "LF4", "LF3", "LF2", "LF1", "LF1", "RF1", "RF1", "RF2", "RF3", "RF4",
    # Row 2
    "LF4", "LF3", "LF2", "LF1", "LF1", "RF1", "RF1", "RF2", "RF3",
    # Row 3
    "LF4", "LF3", "LF2", "LF1", "LF1", "RF1", "RF1"
]

# Physical Hand assignments: 'L' for Left Hand, 'R' for Right Hand
PHYSICAL_HANDS = [
    # Row 1
    "L", "L", "L", "L", "L", "R", "R", "R", "R", "R",
    # Row 2
    "L", "L", "L", "L", "L", "R", "R", "R", "R",
    # Row 3
    "L", "L", "L", "L", "L", "R", "R"
]

# Resting Home Position Coordinates of the 8 fingers
FINGER_HOMES = {
    "LF4": (0.5, 1.0),  # resting on 'a' (Pos 10)
    "LF3": (1.5, 1.0),  # resting on 's' (Pos 11)
    "LF2": (2.5, 1.0),  # resting on 'd' (Pos 12)
    "LF1": (3.5, 1.0),  # resting on 'f' (Pos 13)
    "RF1": (6.5, 1.0),  # resting on 'j' (Pos 16)
    "RF2": (7.5, 1.0),  # resting on 'k' (Pos 17)
    "RF3": (8.5, 1.0),  # resting on 'l' (Pos 18)
    "RF4": (9.5, 1.0)   # resting on ';' (out of the 26 letters, but physical coordinate exists)
}

# Standard baselines represented as 26-character strings
# Each character in the string represents the key at that index (0 to 25)
QWERTY = "qwertyuiopasdfghjklzxcvbnm"
DVORAK = "pyfgcrlaoeuidhtnsqjkxbmwvz"
COLEMAK = "qwfpgjlyuioarstdhnezkxbmvc"

def layout_str_to_coord_dict(layout_str: str) -> dict:
    """Converts a 26-character layout string to a dictionary mapping char -> (x, y)."""
    assert len(layout_str) == 26, "Layout string must be exactly 26 characters."
    return {char: PHYSICAL_COORDINATES[i] for i, char in enumerate(layout_str)}

def layout_str_to_finger_dict(layout_str: str) -> dict:
    """Converts a 26-character layout string to a dictionary mapping char -> finger."""
    assert len(layout_str) == 26, "Layout string must be exactly 26 characters."
    return {char: PHYSICAL_FINGERS[i] for i, char in enumerate(layout_str)}

def layout_str_to_hand_dict(layout_str: str) -> dict:
    """Converts a 26-character layout string to a dictionary mapping char -> hand ('L' or 'R')."""
    assert len(layout_str) == 26, "Layout string must be exactly 26 characters."
    return {char: PHYSICAL_HANDS[i] for i, char in enumerate(layout_str)}

def visualize_layout(layout_str: str) -> str:
    """Returns a neat multi-line string visualizing the keyboard layout in 3 rows."""
    assert len(layout_str) == 26, "Layout string must be exactly 26 characters."
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
