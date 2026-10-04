"""Task #68, round 2: climb toward nonograms that depth-2 probing cannot finish.
round 1 (evolve_nested.py) climbed on cells open after depth-1 probing; every hit (20 of 20, 15x15) was then
finished by depth 2, and each step cost ~15 s. Here fitness is lexicographic on what depth 2 leaves:
(cells open after depth-2 probing, cells that needed a depth-2 probe, open after depth 1, open after line logic).
Unique solution required (complete solver, node budget; out of budget = rejected). Mutation flips 1-3 cells,
accepted if fitness does not drop. Logs every new best and every grid depth 2 cannot finish. JSONL."""
import sys, json, time, numpy as np
sys.path.insert(0, '..')
from nono import puzzle_of, count_solutions, Budget, line_solve
from probe import probe_fixpoint
N = int(sys.argv[1]); SEED = int(sys.argv[2]); SECS = float(sys.argv[3]); P = float(sys.argv[4]) if len(sys.argv) > 4 else 0.45
rng = np.random.default_rng(SEED)
def fitness(img):
    rows, cols = puzzle_of(img)
    try: n, _ = count_solutions(rows, cols, 2, known=img, budget=[20000])
    except Budget: return None
    if n != 1: return None
    g0, _, _ = line_solve(rows, cols); open0 = int((g0 < 0).sum())
    if open0 == 0: return (0, 0, 0, 0)
    g1, _, _ = probe_fixpoint(rows, cols, None, 1)
    open1 = int((g1 < 0).sum())
    if open1 == 0: return (0, 0, 0, open0)
    log = []
    g2, st2, _ = probe_fixpoint(rows, cols, g1, 2, log)
    return (int((g2 < 0).sum()), sum(1 for x in log if x[3] == 2), open1, open0)
img = (rng.random((N, N)) < P).astype(int); f = fitness(img) or (-1, -1, -1, -1); t0 = time.time(); step = 0; stuck = set()
while time.time() - t0 < SECS:
    step += 1
    h = img.copy()
    for _ in range(rng.integers(1, 4)): r, c = rng.integers(0, N, 2); h[r, c] ^= 1
    fh = fitness(h)
    if fh is None: continue
    if fh[0] > 0 and h.tobytes() not in stuck:
        stuck.add(h.tobytes())
        print(json.dumps({"N": N, "seed": SEED, "step": step, "depth2_open": fh[0], "grid": h.tolist()}), flush=True)
    if fh > f:
        print(json.dumps({"best": list(fh), "step": step, "secs": round(time.time() - t0), "grid": h.tolist()}), flush=True)
    if fh >= f: img, f = h, fh
    if step % 50 == 0: print(json.dumps({"progress": step, "fitness": list(f), "secs": round(time.time() - t0)}), flush=True)
print(json.dumps({"done": step, "fitness": list(f), "stuck_found": len(stuck), "secs": round(time.time() - t0)}), flush=True)
