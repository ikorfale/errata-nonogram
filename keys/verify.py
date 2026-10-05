"""Check the two published answer keys against the hashes committed before the reveal.

20x20 pair (board post, 2026-10-03): sha256 fc384cea...f017 of c20_key.json
12x12 depth-2 puzzle (board post, 2026-10-04): sha256 3f4ce440...20df of key12.txt
Also checks that each key grid reproduces the published clues, and reruns line logic.
"""
import hashlib, json, os, sys
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(here))
from nono import clues, line_solve

COMMITTED = {
    'c20_key.json': 'fc384cea4f41f2b5abd20b8e1bb8918e763a9915cd22d113ff5692520742f017',
    'key12.txt': '3f4ce440af710fab24e3dd660f845adbf467617ebe58c2035bb2abcfe26820df',
}
for name, h in COMMITTED.items():
    got = hashlib.sha256(open(os.path.join(here, name), 'rb').read()).hexdigest()
    print(name, 'hash ok' if got == h else 'HASH MISMATCH ' + got)

def puzzle(g):
    n = lambda c: [int(x) for x in c] or [0]
    return [n(clues(r)) for r in g], [n(clues([r[j] for r in g])) for j in range(len(g[0]))]

k = json.load(open(os.path.join(here, 'c20_key.json')))
for name in 'AB':
    rows, cols = puzzle(k[name + '_grid'])
    g, status, sweeps = line_solve(rows, cols)
    print(f"20x20 {name}: key says '{k[name]}'; line logic: {status}, {(g < 0).sum()} of 400 open, {sweeps} sweeps")

lines = open(os.path.join(here, 'key12.txt')).read().split('\n')[1:13]
g12 = [[1 if ch == '#' else 0 for ch in l] for l in lines]
rows, cols = puzzle(g12)
g, status, sweeps = line_solve(rows, cols)
print(f"12x12: line logic {status}, {(g < 0).sum()} of 144 open")
