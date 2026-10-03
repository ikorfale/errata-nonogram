"""Among random R x R grids whose puzzle is unique but not line-solvable: how many does one-step
probing finish, how many need nested probing, and how big are the line cores behind each probe?
Also: does the number of cells line logic leaves open predict the level?  Seed 20261003."""
import sys, json, time, numpy as np
from nono import puzzle_of, line_solve, count_solutions, Budget
from probe import probe_fixpoint, line_core, lsolve

R, N = int(sys.argv[1]), int(sys.argv[2])
ps = [float(x) for x in sys.argv[3].split(',')]
rng = np.random.default_rng(20261003)
out = []
skipped = {'line': 0, 'undecided': 0, 'multi': 0}
for p in ps:
    for i in range(N):
        img = (rng.random((R, R)) < p).astype(int)
        rows, cols = puzzle_of(img)
        g0, st, _ = line_solve(rows, cols)
        if st == 'solved':
            skipped['line'] += 1; continue
        try:
            n, _ = count_solutions(rows, cols, known=img, budget=[2000])
        except Budget:
            skipped['undecided'] += 1; continue
        if n != 1:
            skipped['multi'] += 1; continue
        rec = {'p': p, 'i': i, 'open': int((g0 < 0).sum())}
        log = []
        g1, s1, pr = probe_fixpoint(rows, cols, g0, 1, log)
        rec['level'] = 1 if s1 == 'solved' else None
        rec['probe_cells'] = len(log)
        rec['open_after_probe1'] = int((g1 < 0).sum())
        cores, g = [], g0.copy()
        for r, c, v, _ in log:
            cr, cc = line_core(rows, cols, g, r, c, 1 - v)
            cores.append(len(cr) + len(cc))
            g[r, c] = v; g, _ = lsolve(rows, cols, g)
        rec['cores'] = cores
        if s1 != 'solved':
            t = time.time()
            _, s2, _ = probe_fixpoint(rows, cols, g1, 2)
            rec['level'] = 2 if s2 == 'solved' else 'deeper'
            rec['t2'] = round(time.time() - t, 1)
        out.append(rec)
        print(json.dumps(rec), flush=True)
print(json.dumps({'skipped': skipped}), flush=True)
json.dump(out, open(f'probe_{R}_{N}.json', 'w'), indent=0)
