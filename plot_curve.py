"""Chart of curve_300.json: share of random R x R grids whose clues are solvable by line logic alone."""
import json, math, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
D = json.load(open('curve_300.json')); COL = {10: '#2a78d6', 15: '#eb6834', 20: '#1baf7a'}
def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z*z/n; c = p + z*z/(2*n); h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n)); return (c-h)/d, (c+h)/d
fig, ax = plt.subplots(figsize=(8, 4.6), dpi=150); fig.patch.set_facecolor('#fcfcfb'); ax.set_facecolor('#fcfcfb')
for R, col in COL.items():
    ks = sorted((float(k.split(':')[1]), v) for k, v in D.items() if int(k.split(':')[0]) == R)
    ps = [p for p, _ in ks]; n = [sum(v.values()) for _, v in ks]; y = [v['line'] / m for (_, v), m in zip(ks, n)]
    lo, hi = zip(*[wilson(v['line'], m) for (_, v), m in zip(ks, n)])
    ax.fill_between(ps, [100*a for a in lo], [100*b for b in hi], color=col, alpha=0.15, lw=0)
    ax.plot(ps, [100*v for v in y], color=col, lw=2, marker='o', ms=4, label=f'{R}x{R}')
    i = ps.index(0.5); ax.annotate(f'{R}x{R}', (0.5, 100*y[i]), xytext=(-38, 4), textcoords='offset points', color='#0b0b0b', fontsize=9)
ax.set_xlabel('fill probability of each cell', color='#52514e'); ax.set_ylabel('% solvable without guessing', color='#52514e')
ax.set_title('Random nonograms: how many can be solved by line logic alone? (300 grids per point, 95% band)', fontsize=10, color='#0b0b0b', loc='left')
ax.set_ylim(0, 101); ax.grid(axis='y', color='#e6e5e0', lw=0.8); ax.legend(frameon=False, loc='lower right')
for s in ('top', 'right'): ax.spines[s].set_visible(False)
for s in ('left', 'bottom'): ax.spines[s].set_color('#c3c2b7')
ax.tick_params(colors='#52514e'); fig.tight_layout(); fig.savefig('density_curve.png', facecolor=fig.get_facecolor())
