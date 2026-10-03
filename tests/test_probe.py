"""Probing is sound: whenever it finishes a puzzle, the puzzle has exactly one solution and probing
found it. Every line core refutes its probe on its own and loses that power if any line is removed."""
import sys, os, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from nono import puzzle_of, count_solutions, line_solve
from probe import probe_fixpoint, line_core, line_solve_subset, lsolve


def test_probing_sound_and_cores_minimal():
    rng = np.random.default_rng(7)
    seen_probe = 0
    for _ in range(400):
        img = (rng.random((7, 7)) < 0.5).astype(int)
        rows, cols = puzzle_of(img)
        g0, st, _ = line_solve(rows, cols)
        if st != 'stuck':
            continue
        log = []
        g1, s1, _ = probe_fixpoint(rows, cols, g0, 1, log)
        n, _ = count_solutions(rows, cols, limit=2)
        if s1 == 'solved':
            assert n == 1 and (g1 == img).all()
        g = g0.copy()
        for r, c, v, _ in log:
            assert img[r, c] == v
            cr, cc = line_core(rows, cols, g, r, c, 1 - v)
            h = g.copy(); h[r, c] = 1 - v
            assert line_solve_subset(rows, cols, h, set(cr), set(cc))[1] == 'contradiction'
            for x in cr:
                assert line_solve_subset(rows, cols, h, set(cr) - {x}, set(cc))[1] != 'contradiction'
            for x in cc:
                assert line_solve_subset(rows, cols, h, set(cr), set(cc) - {x})[1] != 'contradiction'
            g[r, c] = v; g, _ = lsolve(rows, cols, g)
            seen_probe += 1
    assert seen_probe > 0
