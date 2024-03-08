#!/usr/bin/env python3
"""
Data Structures and Algorithms for CL 3, Project 1
See <https://https://dsacl3-2022.github.io/p1/> for detailed instructions.
Author:      Pun Ching Nei, Lorena Raichle, Kateryna Smykovska
Honor Code:  I pledge that this program represents my work.
We received help from: no one in designing and debugging our program.
"""

import numpy as np
import json


def cost(ch1, ch2, counts=None):
    """ Given two aligned characters, return cost for ch1 -> ch2.
    This function should be called from the find_edits() function
    below when calculating costs for the edit operations.  If the
    first character is the empty string, it indicates an insert.
    Similarly an empty string as the second character indicates a
    deletion.
    If `counts` is not given, the function should return 1 for all
    operations. if `counts` is given, you are strongly recommended to
    use estimated probability p of the edit operation from the given
    counts, and return `1 - p` as the cost (you should also consider
    using a smoothing technique). You are also welcome to
    experiment with other scoring functions.
    """
    if counts is None:
        if ch1 == ch2:
            return 0
        else:
            return 1
    else:
        if ch1 not in counts:
            w = 1/sum(nested_dict_values(counts))
            return 1-w
        elif ch2 not in counts[ch1]:
            w = 1/(sum(nested_dict_values(counts[ch1]))+len(counts[ch1].values()))
            return 1-w
        else:
            w = counts[ch1][ch2]/sum(nested_dict_values(counts[ch1]))
            return 1-w


def nested_dict_values(d):
    for v in d.values():
        if isinstance(v, dict):
            yield from nested_dict_values(v)
        else:
            yield v

def find_edits(s1, s2, counts=None):
    """ Find edits with minimum cost for given sequences.
    This function should implement the edit distance algorithm, using
    the scoring function above. If `counts` is given, the scoring
    should be based on the counts edits passed.
    The return value from this function should be a list of tuples.
    For example if the best alignment between correct word `work` and
    the misspelling `wrok` is as follows
                        wor-k
                        w-rok
    the return value should be
    [('w', 'w'), ('o', ''), ('r', 'r'), ('', 'o'), ('k', 'k')].
    Parameters
    ---
    s1      The source sequences.
    s2      The target sequences.
    counts  A dictionary of dictionaries with counts of edit
            operations (see assignment description for more
            information and an example)
    """
    lens1, lens2 = len(s1), len(s2)
    d = np.zeros((lens1 + 1, lens2 + 1))
    edits = []

    # finds a MED between s1 and s2
    # iterates over the indices of s1 from 1 to lens1, and the inner loop - over s2 from 1 to lens2
    for i in range(1, lens1 + 1):
        # initializes the first column of d with the cost of transforming the empty string to the prefix of s1 from 1 to i
        d[i, 0] = d[i - 1, 0] + cost(s1[i - 1], '', counts)

    # initializes the first row of d with the cost of transforming the empty string to the prefix of s2 from 1 to j
    for j in range(1, lens2 + 1):
        d[0, j] = d[0, j - 1] + cost('', s2[j - 1], counts)

    # fills in the remaining entries of d using the recursive formula for the minimum edit distance
    for i in range(1, lens1 + 1):
        for j in range(1, lens2 + 1):
            # the cost of transforming the prefix of s1 up to i-1 to the prefix of s2 up to j (by deleting s1[i-1])
            d[i, j] = min(d[i - 1, j] + cost(s1[i - 1], '', counts),
                          # the cost of transforming the prefix of s1 up to i to the prefix of s2 up to j-1 (by inserting s2[j-1])
                          d[i, j - 1] + cost('', s2[j - 1], counts),
                          # the cost of transforming the prefix of s1 up to i-1 to the prefix of s2 up to j-1 (by replacing s1[i-1] with s2[j-1])
                          d[i - 1, j - 1] + cost(s1[i - 1], s2[j - 1], counts))

    # BACKTRACKING
    x, y = lens1, lens2
    while x > 0 and y > 0:
        c1, c2 = s1[x - 1], s2[y - 1]
        # substitution
        if y > 0 and d[x, y] == d[x, y - 1] + cost('', s2[y - 1], counts):
            edits.insert(0, ('', s2[y - 1]))
            y -= 1
        # deletion
        elif x > 0 and d[x, y] == d[x - 1, y] + cost(s1[x - 1], '', counts):
            edits.insert(0, (s1[lens1 - 1], ''))
            x -= 1
        # insertion
        elif x > 0 and y > 0 and d[x, y] == d[x - 1, y - 1] + cost(s1[x - 1], s2[y - 1], counts):
            edits.insert(0, (s1[x - 1], s2[y - 1]))
            x -= 1
            y -= 1
        else:
            break
    return edits


def count_edits(filename, counts=None):
    """ Calculate and return pairs of letters aligned by find_edits().
    Parameters
    ---
    filename    A file containing word - misspelling pairs.
                One pair per line, pairs separated by tab.
    counts      If given use as initial counts.
    """
    if counts is None:
        counts = {'': {'': 0}}

    with open(filename, 'r') as fin:
        for line in fin:
            word, misspelling = line.strip().split('\t')
            for ch1, ch2 in find_edits(word, misspelling):
                if ch1 not in counts:
                    counts[ch1] = {}
                if ch2 not in counts[ch1]:
                    counts[ch1][ch2] = 0
                counts[ch1][ch2] += 1
    return counts


if __name__ == "__main__":
    # The code below shows the intended use of your implementation above.
    counts = None
    counts_new = count_edits('spelling-data.txt')
    while counts != counts_new:
        counts = counts_new
        counts_new = count_edits('spelling-data.txt', counts)

    with open('spell-errors.json', 'wt') as f:
        json.dump(counts, f, ensure_ascii=False, indent=2)