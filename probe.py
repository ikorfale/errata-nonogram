"""Difficulty beyond line logic: probing, and the lines that force a guess.

Level 0: line logic to a fixpoint (nono.line_solve).
Level 1: probing. For each unknown cell, assume one value and run line logic; if that ends in a
         contradiction, the cell must take the other value. Repeat with line logic until nothing
         changes. A puzzle that finishes here never needs a real guess, only a one-step what-if.
Level 2: nested probing: a probe whose own line-logic fixpoint is then probed at level 1.

For each cell fixed by a level-1 probe we also find a line core: a set of rows and columns that is
enough, on its own, to turn the probe into a contradiction (line logic run on those lines only),
and from which no single line can be removed. It is minimal by deletion, not the smallest possible.
"""
import numpy as np

from nono import solve_line


def line_solve_subset(rows, cols, grid, use_r, use_c):
    """Line logic using only the rows in use_r and columns in use_c. Returns (grid, status)."""
    g = grid.copy()
    dirty_r, dirty_c = set(use_r), set(use_c)
    while dirty_r or dirty_c:
        for r in sorted(dirty_r):
            new = solve_line(rows[r], g[r])
            if new is None:
                return g, 'contradiction'
            for c, v in enumerate(new):
                if v != g[r, c]:
                    g[r, c] = v
                    if c in use_c:
                        dirty_c.add(c)
        dirty_r = set()
        for c in sorted(dirty_c):
            new = solve_line(cols[c], g[:, c])
            if new is None:
                return g, 'contradiction'
            for r, v in enumerate(new):
                if v != g[r, c]:
                    g[r, c] = v
                    if r in use_r:
                        dirty_r.add(r)
        dirty_c = set()
    return g, ('solved' if (g >= 0).all() else 'stuck')


def lsolve(rows, cols, grid):
    return line_solve_subset(rows, cols, grid, range(len(rows)), range(len(cols)))


def probe_fixpoint(rows, cols, grid=None, depth=1, log=None):
    """Line logic plus probing up to `depth`. Returns (grid, status, probes_used).
    log, if a list, gets (r, c, forced_value, depth) for every cell a probe fixes."""
    R, C = len(rows), len(cols)
    g = np.full((R, C), -1, dtype=int) if grid is None else grid.copy()
    g, st = lsolve(rows, cols, g)
    probes = 0
    while st == 'stuck':
        progress = False
        for r, c in map(tuple, np.argwhere(g < 0)):
            if g[r, c] >= 0:
                continue
            for v in (1, 0):
                h = g.copy(); h[r, c] = v
                probes += 1
                if depth == 1:
                    _, s = lsolve(rows, cols, h)
                else:
                    _, s, p = probe_fixpoint(rows, cols, h, depth - 1)
                    probes += p
                if s == 'contradiction':
                    g[r, c] = 1 - v
                    if log is not None:
                        log.append((int(r), int(c), 1 - v, depth))
                    g, st = lsolve(rows, cols, g)
                    progress = True
                    break
            if st != 'stuck':
                break
        if st == 'contradiction':
            return g, st, probes
        if not progress:
            break
    return g, st, probes


def level(rows, cols, max_depth=2):
    """Smallest depth at which the puzzle is solved: 0 line logic, 1 probing, 2 nested, or None."""
    g, st = lsolve(rows, cols, np.full((len(rows), len(cols)), -1, dtype=int))
    if st != 'stuck':
        return 0 if st == 'solved' else None
    for d in range(1, max_depth + 1):
        _, st, _ = probe_fixpoint(rows, cols, g, d)
        if st == 'solved':
            return d
    return None


def line_core(rows, cols, grid, r, c, wrong):
    """Rows and columns that alone refute grid[r, c] = wrong under line logic, minimal by deletion."""
    h = grid.copy(); h[r, c] = wrong
    use_r, use_c = set(range(len(rows))), set(range(len(cols)))
    assert line_solve_subset(rows, cols, h, use_r, use_c)[1] == 'contradiction'
    for kind, s in (('r', use_r), ('c', use_c)):
        for x in sorted(s):
            s.discard(x)
            if line_solve_subset(rows, cols, h, use_r, use_c)[1] != 'contradiction':
                s.add(x)
    return sorted(use_r), sorted(use_c)
