"""Independent uniqueness check by SAT (pip install python-sat): each row and column must take one of its
legal fillings; count models up to 3. Usage: python3 satcheck.py grid.json  (grid = list of 0/1 rows)."""
import json, sys, itertools
from pysat.solvers import Cadical153
from pysat.card import CardEnc
def runs(a):
    r=[];n=0
    for v in a:
        if v: n+=1
        elif n: r.append(n); n=0
    if n: r.append(n)
    return r
def fillings(clue, L):
    if not clue: yield [0]*L; return
    k=clue[0]; rest=clue[1:]; need=sum(rest)+len(rest)
    for s in range(L-k-need+1):
        head=[0]*s+[1]*k
        if rest:
            for t in fillings(rest, L-s-k-1): yield head+[0]+t
        else: yield head+[0]*(L-s-k)
def count_models(g, cap=3):
    R=len(g); C=len(g[0])
    rows=[runs(r) for r in g]; cols=[runs([g[i][j] for i in range(R)]) for j in range(C)]
    var=lambda i,j:i*C+j+1; top=[R*C]
    S=Cadical153()
    def line(cells, clue):
        sel=[]
        for f in fillings(clue,len(cells)):
            top[0]+=1; s=top[0]; sel.append(s)
            for v,x in zip(cells,f): S.add_clause([-s, v if x else -v])
        S.add_clause(sel)
    for i in range(R): line([var(i,j) for j in range(C)], rows[i])
    for j in range(C): line([var(i,j) for i in range(R)], cols[j])
    n=0
    while n<cap and S.solve():
        m=S.get_model(); n+=1
        S.add_clause([-l for l in m[:R*C]])
    return n

if __name__ == '__main__':
    print(sys.argv[1], 'models (cap 3):', count_models(json.load(open(sys.argv[1]))))
