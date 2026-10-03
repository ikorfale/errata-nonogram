"""Draw a nonogram (blank grid with clues) or its solution as PNG, in the errata palette."""
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, numpy as np
from nono import puzzle_of
PAPER, INK, RED, GREY = '#f6f1e7', '#1a1a1a', '#b3261e', '#8a8378'

def draw(img, path, solved=False, title=None, cell=0.42):
    img = np.asarray(img); R, C = img.shape; rows, cols = puzzle_of(img)
    lw = max(len(r) for r in rows) or 1; ch = max(len(c) for c in cols) or 1
    fig = plt.figure(figsize=((C + lw * 0.75 + 1) * cell, (R + ch * 0.75 + 1.4) * cell), facecolor=PAPER)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_facecolor(PAPER); ax.axis('off')
    ax.set_xlim(-lw * 0.75 - 0.5, C + 0.5); ax.set_ylim(R + 0.5, -ch * 0.75 - 1.4)
    for r in range(R):
        for c in range(C):
            if solved and img[r, c]:
                ax.add_patch(plt.Rectangle((c, r), 1, 1, color=INK))
    for i in range(R + 1):
        ax.plot([0, C], [i, i], color=INK if i % 5 == 0 or i == R else GREY, lw=1.6 if i % 5 == 0 or i == R else 0.5)
    for j in range(C + 1):
        ax.plot([j, j], [0, R], color=INK if j % 5 == 0 or j == C else GREY, lw=1.6 if j % 5 == 0 or j == C else 0.5)
    fs = cell * 26
    for r, cl in enumerate(rows):
        for k, v in enumerate(reversed(cl or (0,))):
            ax.text(-0.4 - k * 0.75, r + 0.5, str(v), ha='right', va='center', fontsize=fs, color=INK, family='DejaVu Sans Mono')
    for c, cl in enumerate(cols):
        for k, v in enumerate(reversed(cl or (0,))):
            ax.text(c + 0.5, -0.3 - k * 0.75, str(v), ha='center', va='bottom', fontsize=fs, color=INK, family='DejaVu Sans Mono')
    if title:
        ax.text(-lw * 0.75 - 0.3, -ch * 0.75 - 0.9, title, ha='left', va='center', fontsize=fs * 1.05, color=RED, weight='bold')
    fig.savefig(path, dpi=160, facecolor=PAPER); plt.close(fig)
