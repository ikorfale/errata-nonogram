#!/usr/bin/env python3
"""Puzzle 2: the density curve (share of random grids that are fair, for 10x10, 15x15, 20x20)
drawn as a 15x15 line chart with axes; it is itself a fair puzzle. Data: curve_300.json."""
import json, numpy as np
from nono import classify
from render import draw

def chart(data, sizes=(10, 15, 20), W=15, H=15):
    ps = sorted({float(k.split(':')[1]) for k in data})
    img = np.zeros((H, W), int)
    img[:, 0] = 1; img[-1, :] = 1                      # axes
    xs = np.linspace(ps[0], ps[-1], W - 1)
    top = H - 2
    for n in sizes:
        share = [data[f'{n}:{p}']['line'] / sum(data[f'{n}:{p}'].values()) for p in ps]
        r = [int(round(top - v * top)) for v in np.interp(xs, ps, share)]
        for i, ri in enumerate(r):
            lo = hi = ri
            if i > 0 and r[i - 1] != ri:               # join to the previous column's point
                prev = r[i - 1] + (1 if r[i - 1] < ri else -1)
                lo, hi = min(ri, prev), max(ri, prev)
            img[lo:hi + 1, i + 1] = 1
    return img

if __name__ == '__main__':
    img = chart(json.load(open('curve_300.json')))
    print(classify(img))
    print('\n'.join(''.join('#' if v else '.' for v in row) for row in img))
    draw(img, 'puzzles/puzzle02.png', title='errata nonogram 2')
    draw(img, 'puzzles/.puzzle02_solution.png', solved=True, title='errata nonogram 2: solution')
    json.dump(img.tolist(), open('puzzles/.puzzle02.json', 'w'))
