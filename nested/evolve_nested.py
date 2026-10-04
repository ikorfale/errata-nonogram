"""Task #68: search for nonograms that one-step probing cannot finish, on purpose.
Hill climb on N x N grids: fitness = cells still open after line logic + depth-1 probing (ties broken by cells open after line logic alone), for puzzles whose solution
is unique (complete solver with node budget; out of budget = rejected). Mutations flip 1-3 cells, accepted if fitness
does not drop. Every unique puzzle with fitness > 0 is logged with its level (2 = nested probing finishes it,
None = not even depth 2), open-cell count, and the grid. Seeds are fixed; output is JSONL."""
import sys, json, time, numpy as np
sys.path.insert(0, '..')
from nono import puzzle_of, count_solutions, Budget, line_solve
from probe import probe_fixpoint
N = int(sys.argv[1]) if len(sys.argv) > 1 else 12; SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 0
STEPS = int(sys.argv[3]) if len(sys.argv) > 3 else 4000; P = float(sys.argv[4]) if len(sys.argv) > 4 else 0.55
rng = np.random.default_rng(SEED)
def fitness(img):
    rows, cols = puzzle_of(img)
    try: n, _ = count_solutions(rows, cols, 2, known=img, budget=[20000])
    except Budget: return -1, None
    if n != 1: return -1, None
    g0, _, _ = line_solve(rows, cols)
    g, st, _ = probe_fixpoint(rows, cols, None, 1)
    return int((g < 0).sum()) * 10000 + int((g0 < 0).sum()), (rows, cols)   # lexicographic: probe-1 open, then line open
img = (rng.random((N, N)) < P).astype(int); f, _ = fitness(img); seen = set(); t0 = time.time()
for step in range(STEPS):
    h = img.copy()
    for _ in range(rng.integers(1, 4)): r, c = rng.integers(0, N, 2); h[r, c] ^= 1
    fh, rc = fitness(h)
    if fh >= f: img, f = h, fh
    key = h.tobytes()
    if fh >= 10000 and key not in seen:
        seen.add(key); rows, cols = rc
        g2, st2, _ = probe_fixpoint(rows, cols, None, 2)
        print(json.dumps({"N": N, "seed": SEED, "step": step, "open_after_probe1": fh // 10000, "open_after_line": fh % 10000, "level2_solves": st2 == "solved",
                          "open_after_probe2": int((g2 < 0).sum()), "density": float(h.mean()), "grid": h.tolist()}), flush=True)
    if step % 250 == 0: print(json.dumps({"progress": step, "fitness": f, "found": len(seen), "secs": round(time.time() - t0)}), flush=True)
print(json.dumps({"done": STEPS, "found": len(seen), "secs": round(time.time() - t0)}), flush=True)
