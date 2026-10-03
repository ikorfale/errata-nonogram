"""Brute-force checks: the line solver against enumeration of every line up to length 8,
the solution counter against enumeration of every 4x4 grid."""
import itertools, sys, os, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from nono import clues, solve_line, count_solutions, puzzle_of, make_fair, classify

def test_line_solver_matches_enumeration():
    for n in range(1, 9):
        lines = [np.array(l) for l in itertools.product([0, 1], repeat=n)]
        rng = np.random.default_rng(n)
        for _ in range(300):
            true = lines[rng.integers(len(lines))]; cl = clues(true)
            known = np.array([v if rng.random() < 0.4 else -1 for v in true])
            cons = [l for l in lines if clues(l) == cl and all(k < 0 or k == v for k, v in zip(known, l))]
            exp = [int(cons[0][j]) if all(x[j] == cons[0][j] for x in cons) else -1 for j in range(n)]
            assert solve_line(cl, known) == exp

def test_contradiction():
    assert solve_line((3,), [1, 0, 1, -1]) is None

def test_counter_matches_enumeration():
    rng = np.random.default_rng(7)
    grids = [np.array(b).reshape(4, 4) for b in itertools.product([0, 1], repeat=16)]
    keys = {}
    for g in grids:
        k = puzzle_of(g); keys[str(k)] = keys.get(str(k), 0) + 1
    for _ in range(200):
        img = (rng.random((4, 4)) < 0.5).astype(int); rows, cols = puzzle_of(img)
        assert count_solutions(rows, cols, limit=100)[0] == keys[str((rows, cols))]

def test_make_fair_gives_line_solvable():
    rng = np.random.default_rng(1)
    for _ in range(10):
        out, _ = make_fair((rng.random((12, 12)) < 0.5).astype(int), rng)
        assert out is not None and classify(out)[0] == 'line'
