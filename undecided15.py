"""Close the hole in the probing study: the 49 15x15 grids whose uniqueness the 2000-node search could not
decide. Same seed and draw order as probe_study.py; uniqueness decided by SAT (satcheck.count_models),
then one-step probing, then two-step if needed."""
import sys, json, time, numpy as np
sys.path.insert(0, __import__('os').path.dirname(__file__) or '.')
from satcheck import count_models
from nono import puzzle_of, line_solve, count_solutions, Budget
from probe import probe_fixpoint
R, N, ps = 15, 300, [0.4, 0.45, 0.5, 0.55, 0.6]
rng = np.random.default_rng(20261003)
tally = {'undecided': 0, 'sat_unique': 0, 'sat_multi': 0}
for p in ps:
    for i in range(N):
        img = (rng.random((R, R)) < p).astype(int)
        rows, cols = puzzle_of(img)
        g0, st, _ = line_solve(rows, cols)
        if st == 'solved': continue
        try:
            count_solutions(rows, cols, known=img, budget=[2000]); continue
        except Budget:
            pass
        tally['undecided'] += 1
        print(json.dumps({'undecided': [p, i]}), flush=True)
        n = count_models(img.tolist(), cap=2)
        if n != 1:
            tally['sat_multi'] += 1; continue
        tally['sat_unique'] += 1
        print(json.dumps({'sat_unique': [p, i]}), flush=True)
        log = []
        g1, s1, _ = probe_fixpoint(rows, cols, g0, 1, log)
        rec = {'p': p, 'i': i, 'open': int((g0 < 0).sum()), 'probe_cells': len(log),
               'open_after_probe1': int((g1 < 0).sum()), 'level': 1 if s1 == 'solved' else None}
        if s1 != 'solved':
            t = time.time(); _, s2, _ = probe_fixpoint(rows, cols, g1, 2)
            rec['level'] = 2 if s2 == 'solved' else 'deeper'; rec['t2'] = round(time.time() - t, 1)
        print(json.dumps(rec), flush=True)
print(json.dumps({'tally': tally}), flush=True)
