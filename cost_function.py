# cost_function.py
"""
Cost function implementation for keyboard layout optimization.
Formula: Cost = alpha * D + beta * F + gamma * P
Optimized using pre-calculated character and bigram frequencies.
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
    Preprocesses text and computes unigram and bigram frequency counts.
    Only lowercase alphabetic characters are considered (N=26).
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
    """Computes Euclidean distance between two 2D points."""
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def calculate_layout_cost(layout_str: str, unigram_counts: dict, bigram_counts: dict, total_chars: int, weights=(1.0, 2.0, 1.5)) -> dict:
    """
    Calculates the detailed and normalized cost of a keyboard layout.
    
    Parameters:
        layout_str: 26-character layout string.
        unigram_counts: Dictionary of character frequencies.
        bigram_counts: Dictionary of bigram frequencies.
        total_chars: Total count of alphabetic characters in the text.
        weights: Tuple of (alpha, beta, gamma).
        
    Returns:
        A dictionary containing:
            'total_cost': The final combined cost (Cost = alpha*D + beta*F + gamma*P)
            'D': Normalized distance cost
            'F': Normalized same-finger fatigue cost
            'P': Normalized one-hand penalty cost
    """
    alpha, beta, gamma = weights
    
    # Convert layout string to maps
    coords = layout_str_to_coord_dict(layout_str)
    fingers = layout_str_to_finger_dict(layout_str)
    hands = layout_str_to_hand_dict(layout_str)
    
    # 1. Distance (D) calculation
    # Base distance: distance of each key from its typing finger's home resting position
    d_base = 0.0
    for char, count in unigram_counts.items():
        if char in coords:
            key_coord = coords[char]
            finger = fingers[char]
            home_coord = FINGER_HOMES[finger]
            d_base += count * euclidean_distance(key_coord, home_coord)
            
    # Transition distance: distance traveled by the same finger between consecutive keys
    d_transition = 0.0
    for (c1, c2), count in bigram_counts.items():
        if c1 in coords and c2 in coords:
            if fingers[c1] == fingers[c2]:
                d_transition += count * euclidean_distance(coords[c1], coords[c2])
                
    total_d = d_base + d_transition
    
    # 2. Same-Finger Fatigue (F) calculation
    # Same Finger Bigram (SFB): Consecutive keystrokes typed by the same finger on different keys
    total_f = 0.0
    for (c1, c2), count in bigram_counts.items():
        if c1 in coords and c2 in coords and c1 != c2:
            if fingers[c1] == fingers[c2]:
                total_f += count
                
    # 3. One-Hand Penalty (P) calculation
    # Same Hand Bigram (SHB): Consecutive keystrokes typed by the same hand
    total_p = 0.0
    for (c1, c2), count in bigram_counts.items():
        if c1 in coords and c2 in coords:
            if hands[c1] == hands[c2]:
                total_p += count
                
    # Normalize costs to get average cost per character typed
    norm_factor = max(1, total_chars)
    D_norm = total_d / norm_factor
    F_norm = total_f / norm_factor
    P_norm = total_p / norm_factor
    
    # Final cost
    total_cost = alpha * D_norm + beta * F_norm + gamma * P_norm
    
    return {
        "total_cost": total_cost,
        "D": D_norm,
        "F": F_norm,
        "P": P_norm
    }
