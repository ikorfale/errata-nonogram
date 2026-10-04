"""Trace how the hardest grid from the deep search gets solved: always the cheapest tool that moves.
Stage = line logic, else one depth-1 probe that contradicts, else one depth-2 probe. Each cell is stamped with
the step at which it became known and the tool that unlocked that step. Draws the solution with that order."""
import sys, json, numpy as np
sys.path.insert(0, '..')
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from nono import puzzle_of, line_solve, count_solutions
from probe import probe_fixpoint, lsolve
from render import draw, PAPER, INK, RED, GREY
src, out = sys.argv[1], sys.argv[2]
best = [json.loads(l) for l in open(src) if '"best"' in l][-1]
img = np.array(best['grid']); R, C = img.shape; rows, cols = puzzle_of(img)
print('fitness', best['best'], 'unique', count_solutions(rows, cols, 2, known=img, budget=[200000])[0])
g = np.full((R, C), -1); g, st = lsolve(rows, cols, g)
stamp = np.full((R, C), -1); tool = np.full((R, C), -1); step = 0
stamp[g >= 0] = 0; tool[g >= 0] = 0
counts = {0: int((g >= 0).sum()), 1: 0, 2: 0}; probes = {1: 0, 2: 0}
while st == 'stuck':
    moved = False
    for d in (1, 2):
        for r, c in map(tuple, np.argwhere(g < 0)):
            for v in (1, 0):
                h = g.copy(); h[r, c] = v
                s = lsolve(rows, cols, h)[1] if d == 1 else probe_fixpoint(rows, cols, h, 1)[1]
                if s == 'contradiction':
                    g[r, c] = 1 - v; step += 1; probes[d] += 1
                    g2, st = lsolve(rows, cols, g)
                    new = (g2 >= 0) & (stamp < 0)
                    stamp[new] = step; tool[new] = d; counts[d] += int(new.sum()); g = g2; moved = True
                    print(f'step {step}: depth-{d} probe at ({r},{c})={v} contradicts -> {int(new.sum())} cells, open {int((g<0).sum())}', flush=True)
                    break
            if moved: break
        if moved: break
    if not moved: break
assert st == 'solved' and (g == img).all(), st
print('cells unlocked by line logic only', counts[0], 'after depth-1 probes', counts[1], 'after depth-2 probes', counts[2])
print('steps', step, 'depth-1 probes that fired', probes[1], 'depth-2 probes that fired', probes[2])
json.dump({'grid': img.tolist(), 'stamp': stamp.tolist(), 'tool': tool.tolist(), 'counts': counts, 'probes': probes}, open(out + '.json', 'w'))
draw(img, out + '_puzzle.png', title='errata nonogram 12x12 - no line moves at the start')
fig, ax = plt.subplots(figsize=(7.2, 7.6), facecolor=PAPER); ax.set_facecolor(PAPER)
cm = plt.get_cmap('Greys')
for r in range(R):
    for c in range(C):
        k = stamp[r, c] / max(step, 1)
        ax.add_patch(plt.Rectangle((c, r), 1, 1, color=plt.cm.cividis(0.05 + 0.9 * k)))
        if img[r, c]: ax.add_patch(plt.Rectangle((c + .3, r + .3), .4, .4, color=INK))
        if tool[r, c] == 2: ax.add_patch(plt.Rectangle((c + .06, r + .06), .88, .88, fill=False, ec=RED, lw=1.4))
for i in range(R + 1): ax.plot([0, C], [i, i], color=GREY, lw=.5)
for j in range(C + 1): ax.plot([j, j], [0, R], color=GREY, lw=.5)
ax.set_xlim(0, C); ax.set_ylim(R, 0); ax.set_aspect('equal'); ax.axis('off')
ax.set_title(f'Solve order, cheapest move first: dark blue = early, yellow = late ({step} steps)\nblack square = filled cell; red frame = unlocked by a depth-2 probe ({probes[2]} of {step} steps)', color=INK, fontsize=10)
fig.savefig(out + '_order.png', dpi=150, facecolor=PAPER); plt.close(fig)
