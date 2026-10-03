"""Share of random R x R grids (each cell filled with prob p) whose puzzle is line-solvable,
unique-but-needs-a-guess, or has several solutions. Seed 20261003."""
import sys, numpy as np, collections, json
from nono import classify
N = int(sys.argv[1]); sizes = [int(x) for x in sys.argv[2].split(',')]
ps = [round(x, 2) for x in np.arange(0.30, 0.91, 0.05)]
rng = np.random.default_rng(20261003); out = {}
for R in sizes:
    for p in ps:
        c = collections.Counter(classify((rng.random((R, R)) < p).astype(int))[0] for _ in range(N))
        out[f"{R}:{p}"] = {k: c[k] for k in ('line', 'unique', 'multi')}
        print(R, p, out[f"{R}:{p}"], flush=True)
json.dump(out, open(f'curve_{N}.json', 'w'), indent=1)
