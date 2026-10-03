"""Chart of probe_15_300.jsonl: cells left open by line logic vs probes needed, one dot per puzzle."""
import json, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
L = [json.loads(l) for l in open('probe_15_300.jsonl') if l.startswith('{')]
fig, ax = plt.subplots(figsize=(8, 4.6), dpi=150); fig.patch.set_facecolor('#fcfcfb'); ax.set_facecolor('#fcfcfb')
ax.scatter([r['open'] for r in L], [r['probe_cells'] for r in L], s=[12 + 3 * max(r['cores']) for r in L],
           color='#2a78d6', alpha=0.55, lw=0)
ax.set_xlabel('cells line logic leaves open (of 225)', color='#52514e')
ax.set_ylabel('cells fixed by a one-step probe', color='#52514e')
ax.set_title(f'All {len(L)} unique 15x15 puzzles that line logic could not finish were finished by one-step probing\n'
             '(1,500 random grids; dot size = largest set of lines behind one probe)', fontsize=10, color='#0b0b0b', loc='left')
ax.grid(color='#e6e5e0', lw=0.8)
for s in ('top', 'right'): ax.spines[s].set_visible(False)
for s in ('left', 'bottom'): ax.spines[s].set_color('#c3c2b7')
ax.tick_params(colors='#52514e'); fig.tight_layout(); fig.savefig('probe_15.png', facecolor=fig.get_facecolor())
