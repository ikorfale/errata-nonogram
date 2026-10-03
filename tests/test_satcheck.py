import itertools, numpy as np, pytest
pytest.importorskip('pysat')
from satcheck import count_models
from nono import count_solutions, puzzle_of

def test_sat_agrees_with_counter_on_all_3x3():
    for bits in itertools.product((0, 1), repeat=9):
        g = np.array(bits).reshape(3, 3)
        rows, cols = puzzle_of(g)
        n, _ = count_solutions(rows, cols, limit=3)
        assert count_models(g.tolist(), cap=3) == n
