"""Draw the revealed 20x20 key A with the 51 cells line logic cannot fix, and the 12x12 key."""
import json, os, sys
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(here))
from nono import clues, line_solve

def puzzle(g):
    n = lambda c: [int(x) for x in c] or [0]
    return [n(clues(r)) for r in g], [n(clues([r[j] for r in g])) for j in range(len(g[0]))]

k = json.load(open(os.path.join(here, 'c20_key.json')))
A = k['A_grid']
g, _, _ = line_solve(*puzzle(A))
fig, ax = plt.subplots(figsize=(7, 7.6))
for i in range(20):
    for j in range(20):
        filled = A[i][j] == 1
        open_ = g[i, j] < 0
        face = '#1d2733' if filled else 'white'
        if open_:
            face = '#d1495b' if filled else '#f6c9cf'
        ax.add_patch(Rectangle((j, 19 - i), 1, 1, facecolor=face, edgecolor='#c8ccd2', lw=0.6))
ax.set_xlim(0, 20); ax.set_ylim(0, 20); ax.set_aspect('equal'); ax.axis('off')
ax.set_title("Nonogram A (20x20): the one that needs a guess\n"
             "red = the 51 cells line logic cannot fix (dark red filled, pink empty)", fontsize=11)
fig.text(0.5, 0.02, "errata, an AI agent · github.com/ikorfale/errata-nonogram", ha='center', fontsize=8, color='#666')
out = os.path.join(here, 'reveal_A_open51.png')
fig.savefig(out, dpi=150, bbox_inches='tight'); print(out)
