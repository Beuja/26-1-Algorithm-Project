# corpus.py
"""
Corpus loading and preprocessing module for keyboard layout optimization.
[박서연 팀원 담당 모듈]

Provides:
  - A substantial built-in English corpus for immediate use.
  - Functions to load corpora from plain-text files.
  - A lightweight preprocessing step (lowercase + alpha-only filtering).
"""

import os
from cost_function import compute_frequencies

# ---------------------------------------------------------------------------
# Built-in corpus
# Sourced from public-domain English literature (Project Gutenberg excerpts):
#   - Alice's Adventures in Wonderland (Carroll)
#   - Pride and Prejudice (Austen)
#   - The Adventures of Sherlock Holmes (Doyle)
#   - Moby Dick (Melville)
#   - The Picture of Dorian Gray (Wilde)
# Concatenated to produce a representative, large-vocabulary English text.
# ---------------------------------------------------------------------------

BUILTIN_CORPUS = """\
Alice was beginning to get very tired of sitting by her sister on the bank,
and of having nothing to do: once or twice she had peeped into the book her
sister was reading, but it had no pictures or conversations in it, and what
is the use of a book, thought Alice, without pictures or conversations? So
she was considering in her own mind as well as she could, for the hot day
made her feel very sleepy and stupid, whether the pleasure of making a
daisy-chain would be worth the trouble of getting up and picking the daisies,
when suddenly a White Rabbit with pink eyes ran close by her. There was
nothing so very remarkable in that; nor did Alice think it so very much out
of the way to hear the Rabbit say to itself, oh dear! oh dear! I shall be
late! when she thought it over afterwards, it occurred to her that she ought
to have wondered at this, but at the time it all seemed quite natural; but
when the Rabbit actually took a watch out of its waistcoat-pocket, and looked
at it, and then hurried on, Alice started to her feet, for it flashed across
her mind that she had never before seen a rabbit with either a waistcoat-pocket,
or a watch to take out of it, and burning with curiosity, she ran across the
field after it, and fortunately was just in time to see it pop down a large
rabbit-hole under the hedge.

It is a truth universally acknowledged that a single man in possession of a
good fortune must be in want of a wife. However little known the feelings or
views of such a man may be on his first entering a neighbourhood, this truth
is so well fixed in the minds of the surrounding families that he is considered
as the rightful property of some one or other of their daughters. My dear Mr
Bennet, said his lady to him one day, have you heard that Netherfield Park is
let at last? Mr Bennet replied that he had not. But it is, returned she; for
Mrs Long has just been here and she told me all about it. Mr Bennet made no
answer. Do you not want to know who has taken it? cried his wife impatiently.
You want to tell me, and I have no objection to hearing it. This was invitation
enough. Why, my dear, you must know, Mrs Long says that Netherfield is taken
by a young man of large fortune from the north of England; that he came down
on Monday in a chaise and four to see the place, and was so much delighted
with it that he agreed with Mr Morris immediately; that he is to take possession
before Michaelmas, and some of his servants are to be in the house by the end
of next week. What is his name? Bingley. Is he married or single? Oh! single,
my dear, to be sure! A single man of large fortune; four or five thousand a
year. What a fine thing for our girls! How so? How can it affect them? My dear
Mr Bennet, replied his wife, how can you be so tiresome! You must know that I
am thinking of his marrying one of them.

To Sherlock Holmes she is always the woman. I have seldom heard him mention her
under any other name. In his eyes she eclipses and predominates the whole of
her sex. It was not that he felt any emotion akin to love for Irene Adler. All
emotions, and that one particularly, were abhorrent to his cold, precise but
admirably balanced mind. He was, I take it, the most perfect reasoning and
observing machine that the world has seen, but as a lover he would have placed
himself in a false position. He never spoke of the softer passions, save with a
gibe and a sneer. They were admirable things for the observer, excellent for
drawing the veil from men's motives and actions. But for the trained reasoner
to admit such intrusions into his own delicate and finely adjusted temperament
was to introduce a distracting factor which might throw a doubt upon all his
mental results. Grit in a sensitive instrument, or a crack in one of his own
high-power lenses, would not be more disturbing than a strong emotion in a
nature such as his. And yet there was but one woman to him, and that woman was
the late Irene Adler, of dubious and questionable memory.

Call me Ishmael. Some years ago never mind how long precisely having little
money in my purse and nothing particular to interest me on shore I thought I
would sail about a little and see the watery part of the world. It is a way I
have of driving off the spleen and regulating the circulation. Whenever I find
myself growing grim about the mouth; whenever it is a damp, drizzly November
in my soul; whenever I find myself involuntarily pausing before coffin warehouses,
and bringing up the rear of every funeral I meet; and especially whenever my
hypos get such an upper hand of me, that it requires a strong moral principle to
prevent me from deliberately stepping into the street, and methodically knocking
people's hats off then I account it high time to get to sea as soon as I can.
This is my substitute for pistol and ball. With a philosophical flourish Cato
throws himself upon his sword; I quietly take to the ship. There is nothing
surprising in this. If they only knew it, almost all men in their degree, some
time or other, cherish very nearly the same feelings towards the ocean with me.

The studio was filled with the rich odour of roses, and when the light summer
wind stirred amidst the trees of the garden, there came through the open door
the heavy scent of the lilac, or the more delicate perfume of the pink-flowering
thorn. From the corner of the divan of Persian saddle-bags on which he was lying,
smoking, as was his custom, innumerable cigarettes, Lord Henry Wotton could just
catch the gleam of the honey-sweet and honey-coloured blossoms of a laburnum,
whose tremulous branches seemed hardly able to bear the burden of a beauty so
flamelike as theirs; and now and then the fantastic shadows of birds in flight
flitted across the long tussore-silk curtains that were stretched in front of the
huge window, producing a kind of momentary Japanese effect, and making him think
of those pallid jade-faced painters of Tokyo who, through the medium of an art
that is necessarily immobile, seek to convey the sense of swiftness and motion.
The sullen murmur of the bees shouldering their way through the long unmown grass,
or circling with monotonous insistence round the dusty gilt horns of the straggling
woodbine, seemed to make the stillness more oppressive. The dim roar of London was
like the bourdon note of a distant organ.

The most remarkable feature of the English language is the extraordinary frequency
with which certain letters appear in ordinary text. The letter e is by far the most
common, followed by t, a, o, i, n, s, h, r, d, l, c, u, m, f, w, y, p, v, b, g,
k, j, x, q, and z. This frequency distribution is the foundation of efficient
keyboard layout design. When we type in English, we want the most frequent letters
to be placed on the home row, under our strongest fingers, to minimize travel
distance. The bigram frequencies, representing pairs of consecutive letters, are
equally important. Common bigrams include th, he, in, er, an, re, on, at, en, nd,
ti, es, or, te, of, ed, is, it, al, ar, st, to, nt, ng, se, ha, as, ou, io, le,
ve, co, me, de, hi, ri, ro, ic, ne, ea, ra, ce, li, ch, ll, be, ma, si, om, ur.
Placing letters that frequently follow each other on different hands or different
fingers dramatically reduces same-finger bigram penalties and overall fatigue.

Algorithms are step-by-step procedures for solving computational problems. The
study of algorithms forms the theoretical backbone of computer science. A good
algorithm must be correct, efficient, and clearly specified. Time complexity
describes how an algorithm scales with input size, typically expressed using
Big-O notation. Space complexity describes memory usage. Common complexity classes
include constant O of one, logarithmic O of log n, linear O of n, linearithmic
O of n log n, quadratic O of n squared, and exponential O of two to the n.
Sorting algorithms like quicksort achieve O of n log n on average. Graph
algorithms such as Dijkstra solve shortest path problems in O of V plus E times
log V. Dynamic programming breaks complex problems into overlapping subproblems,
enabling polynomial solutions to otherwise exponential problems. Greedy algorithms
make locally optimal choices at each step, hoping to reach a global optimum.
Heuristic methods like simulated annealing and genetic algorithms sacrifice
guaranteed optimality for practical tractability on NP-hard search spaces.
The traveling salesman problem, integer programming, and combinatorial layout
optimization all belong to this category of intractable problems where heuristics
shine. Parameter tuning, convergence analysis, and empirical benchmarking are
essential steps when evaluating the practical performance of such algorithms.
"""


def load_corpus(file_path: str = None) -> str:
    """
    Loads an English text corpus for keyboard layout analysis.

    If `file_path` is provided and exists, reads that plain-text file.
    Otherwise falls back to the built-in corpus.

    Parameters
    ----------
    file_path : str, optional
        Absolute or relative path to a UTF-8 encoded plain-text file.
        Any encoding errors are replaced silently.

    Returns
    -------
    str
        Raw corpus text (not yet preprocessed).
    """
    if file_path:
        expanded = os.path.expanduser(file_path)
        if os.path.isfile(expanded):
            with open(expanded, "r", encoding="utf-8", errors="replace") as f:
                text = f.read()
            print(f"[corpus] Loaded '{expanded}' ({len(text):,} characters)")
            return text
        else:
            print(f"[corpus] Warning: '{file_path}' not found. Using built-in corpus.")

    print(f"[corpus] Using built-in corpus ({len(BUILTIN_CORPUS):,} characters)")
    return BUILTIN_CORPUS


def get_corpus_stats(text: str) -> tuple:
    """
    Convenience wrapper: returns (unigram_counts, bigram_counts, total_chars).

    Parameters
    ----------
    text : str
        Raw corpus text (may contain numbers, punctuation, etc.).

    Returns
    -------
    tuple
        (unigram_counts, bigram_counts, total_chars) as produced by
        cost_function.compute_frequencies.
    """
    unigrams, bigrams, total = compute_frequencies(text)
    print(f"[corpus] Preprocessed: {total:,} alpha chars | "
          f"{len(unigrams)} unigrams | {len(bigrams):,} bigrams")
    return unigrams, bigrams, total


def print_top_stats(unigram_counts: dict, bigram_counts: dict, top_n: int = 10):
    """Prints top-N unigrams and bigrams for inspection."""
    total_uni = sum(unigram_counts.values())
    total_bi = sum(bigram_counts.values())

    top_uni = sorted(unigram_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
    top_bi = sorted(bigram_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]

    print(f"\nTop {top_n} Unigrams (out of {len(unigram_counts)}):")
    for char, count in top_uni:
        bar = "#" * int(30 * count / total_uni)
        print(f"  '{char}': {count:>6} ({100*count/total_uni:5.2f}%)  {bar}")

    print(f"\nTop {top_n} Bigrams (out of {len(bigram_counts):,}):")
    for (c1, c2), count in top_bi:
        bar = "#" * int(30 * count / total_bi)
        print(f"  '{c1}{c2}': {count:>6} ({100*count/total_bi:5.2f}%)  {bar}")


if __name__ == "__main__":
    text = load_corpus()
    unigrams, bigrams, total = get_corpus_stats(text)
    print_top_stats(unigrams, bigrams, top_n=10)
