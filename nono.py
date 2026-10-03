"""Nonogram tools: clues, a line-logic solver, a complete solver that counts solutions (stops at 2),
and a generator of puzzles that are unique AND solvable by line logic alone (no guessing).

Cells: 1 = filled, 0 = empty, -1 = unknown.
"""
import numpy as np
from functools import lru_cache


def clues(line):
    out, run = [], 0
    for v in line:
        if v:
            run += 1
        elif run:
            out.append(run); run = 0
    if run:
        out.append(run)
    return tuple(out)


def solve_line(clue, known):
    """Return the line with every cell forced by (clue, known) set, or None if contradictory.
    DP over (position, block index): which placements are consistent; a cell is forced if all
    consistent placements agree on it."""
    n, k = len(known), len(clue)
    known = tuple(known)

    @lru_cache(None)
    def ok(i, b):  # can cells i.. be completed with blocks b..
        if b == k:
            return all(known[j] != 1 for j in range(i, n))
        L = clue[b]
        for s in range(i, n - L + 1):
            if any(known[j] == 1 for j in range(i, s)):
                break  # a filled cell before the block would be uncovered
            if all(known[j] != 0 for j in range(s, s + L)) and (s + L == n or known[s + L] != 1):
                if ok(min(s + L + 1, n), b + 1) if s + L < n else (b + 1 == k):
                    return True
        return False

    if not ok(0, 0):
        return None
    can1 = [False] * n; can0 = [False] * n

    # second pass: walk all consistent placements, marking cells (memoised by reachability)
    seen = set()

    def mark(i, b):
        if (i, b) in seen:
            return
        seen.add((i, b))
        if b == k:
            for j in range(i, n):
                can0[j] = True
            return
        L = clue[b]
        for s in range(i, n - L + 1):
            if any(known[j] == 1 for j in range(i, s)):
                break
            if all(known[j] != 0 for j in range(s, s + L)) and (s + L == n or known[s + L] != 1):
                nxt = min(s + L + 1, n)
                good = ok(nxt, b + 1) if s + L < n else (b + 1 == k)
                if good:
                    for j in range(i, s):
                        can0[j] = True
                    for j in range(s, s + L):
                        can1[j] = True
                    if s + L < n:
                        can0[s + L] = True
                    mark(nxt, b + 1)

    mark(0, 0)
    return [1 if (a and not z) else 0 if (z and not a) else -1 for a, z in zip(can1, can0)]


def line_solve(rows, cols, grid=None):
    """Propagate line logic to a fixpoint. Returns (grid, status) with status in
    'solved', 'stuck', 'contradiction'. Also returns the number of sweeps used."""
    R, C = len(rows), len(cols)
    g = np.full((R, C), -1, dtype=int) if grid is None else grid.copy()
    dirty_r, dirty_c, sweeps = set(range(R)), set(range(C)), 0
    while dirty_r or dirty_c:
        sweeps += 1
        for r in sorted(dirty_r):
            new = solve_line(rows[r], g[r])
            if new is None:
                return g, 'contradiction', sweeps
            for c, v in enumerate(new):
                if v != g[r, c]:
                    g[r, c] = v; dirty_c.add(c)
        dirty_r = set()
        for c in sorted(dirty_c):
            new = solve_line(cols[c], g[:, c])
            if new is None:
                return g, 'contradiction', sweeps
            for r, v in enumerate(new):
                if v != g[r, c]:
                    g[r, c] = v; dirty_r.add(r)
        dirty_c = set()
    return g, ('solved' if (g >= 0).all() else 'stuck'), sweeps


class Budget(Exception):
    pass


def count_solutions(rows, cols, limit=2, grid=None, known=None, budget=None):
    """Complete solver: line logic plus branching on an unknown cell. Counts solutions up to limit.
    If one solution is already known (the picture), branch against it first: a second solution, if
    any, is then found without walking the known one's subtree. budget = [nodes left]; raises Budget
    when it runs out."""
    if budget is not None:
        budget[0] -= 1
        if budget[0] < 0:
            raise Budget
    g, st, _ = line_solve(rows, cols, grid)
    if st == 'contradiction':
        return 0, []
    if st == 'solved':
        return 1, [g]
    r, c = map(int, np.argwhere(g < 0)[0])
    total, sols = 0, []
    for v in ((1 - known[r, c], known[r, c]) if known is not None else (1, 0)):
        h = g.copy(); h[r, c] = v
        n, s = count_solutions(rows, cols, limit - total, h, known, budget)
        total += n; sols += s
        if total >= limit:
            break
    return total, sols


def puzzle_of(img):
    img = np.asarray(img, dtype=int)
    return [clues(r) for r in img], [clues(c) for c in img.T]


def classify(img, nodes=None, order='known'):
    """'line' = unique and line-solvable; 'unique' = unique but needs branching; 'multi' = >1 solution;
    'undecided' = the branching search used up its node budget."""
    rows, cols = puzzle_of(img)
    _, st, sweeps = line_solve(rows, cols)
    if st == 'solved':
        return 'line', sweeps
    try:
        n, _ = count_solutions(rows, cols, known=np.asarray(img, dtype=int) if order == 'known' else None,
                               budget=[nodes] if nodes else None)
    except Budget:
        return 'undecided', sweeps
    return ('unique' if n == 1 else 'multi'), sweeps


def make_fair(img, rng, max_edits=60):
    """Edit an image until its puzzle is line-solvable: while line logic is stuck, toggle one
    randomly chosen stuck cell in the target image and retry. Returns the edited
    image and the number of edits, or (None, edits) if it gave up."""
    img = np.asarray(img, dtype=int).copy()
    for e in range(max_edits + 1):
        rows, cols = puzzle_of(img)
        g, st, _ = line_solve(rows, cols)
        if st == 'solved':
            return img, e
        unk = np.argwhere(g < 0)
        r, c = unk[rng.integers(len(unk))]
        img[r, c] ^= 1
    return None, max_edits
