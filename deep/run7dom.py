"""theone 82334/82371: 15x15 7-Dom (Greifer). Independent run with errata-nonogram probe.py."""
import sys, time, json, numpy as np
sys.path.insert(0, __import__('os').path.join(__import__('os').path.dirname(__file__), '..'))
from probe import lsolve, probe_fixpoint
R = "3|1|3 1|1|3 1|1|3 1|1|3 1|1|3 1|1|3 1|1|1"; C = "1|1|1 3|1|1 3|1|1 3|1|1 3|1|1 3|1|1 3|1|3"
rows = [[int(x) for x in s.split()] for s in R.split('|')]; cols = [[int(x) for x in s.split()] for s in C.split('|')]
g0 = np.full((15, 15), -1, dtype=int)
g, st = lsolve(rows, cols, g0); print('line', int((g >= 0).sum()), st, flush=True)
for d in (1, 2, 3):
    t = time.time(); g, st, p = probe_fixpoint(rows, cols, g, d)
    fixed = np.argwhere(g.ravel() >= 0).ravel().tolist()
    print(f'depth{d}', len(fixed), st, 'probes', p, 'sec', round(time.time() - t, 1), flush=True)
    if d == 2: print('fixed_idx', fixed, 'values', sorted(set(g.ravel()[fixed].tolist())), flush=True)
    if st == 'solved':
        print('\n'.join(''.join('#' if v else '.' for v in row) for row in g), flush=True); break
