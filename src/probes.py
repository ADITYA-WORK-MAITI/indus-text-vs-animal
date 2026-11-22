"""Four structural probes on unbroken inscriptions (no boundary, no uncertain sign).
1. Are long texts built from shorter texts that occur on their own?
2. Which signs are locked to the start or end of a text?
3. Which sign pairs occur in the same contexts but rarely together?
4. (numerals.py) How do the stroke signs behave?
Writes results/probes.json, results/positions.csv, results/context_pairs.csv."""
import json
from collections import Counter, defaultdict
import numpy as np, pandas as pd
from corpus import load_inscriptions, unbroken_text, ROOT

rng = np.random.default_rng(0)
d = load_inscriptions()
texts = [t for t in d.text.apply(unbroken_text) if t]
texts = list(dict.fromkeys(texts))                      # distinct texts
freq = Counter(x for t in texts for x in t)
out = dict(n_distinct_unbroken_texts=len(texts), n_tokens=sum(map(len, texts)))

# 1. compositionality
def segmentable(t, pool):
    n = len(t); ok = [False] * (n + 1); ok[0] = True
    for i in range(n):
        if ok[i]:
            for j in range(i + 2, n + 1):
                if j - i < n and t[i:j] in pool:
                    ok[j] = True
    return ok[n]

def comp_rate(corpus):
    pool = set(t for t in corpus if len(t) >= 2)
    long_ = [t for t in corpus if len(t) >= 5]
    return float(np.mean([segmentable(t, pool) for t in long_])), len(long_)

rate, n_long = comp_rate(texts)
flat = [x for t in texts for x in t]
null = []
for _ in range(20):
    p = rng.permutation(flat); i = 0; sh = []
    for t in texts:
        sh.append(tuple(p[i:i + len(t)])); i += len(t)
    null.append(comp_rate(sh)[0])
out["1_long_texts_made_of_standalone_pieces"] = dict(n_texts_5plus=n_long, observed=rate, shuffled_mean=float(np.mean(null)))

# 2. positions
pos = defaultdict(lambda: [0, 0, 0])
for t in texts:
    if len(t) >= 2:
        for i, x in enumerate(t):
            pos[x][0 if i == 0 else (2 if i == len(t) - 1 else 1)] += 1
P = pd.DataFrame([(s, *v, sum(v)) for s, v in pos.items()], columns=["sign", "start", "mid", "end", "n"])
P = P[P.n >= 25].copy()
P["start_frac"] = P.start / P.n; P["end_frac"] = P.end / P.n
P.sort_values("end_frac", ascending=False).to_csv(ROOT / "results" / "positions.csv", index=False)
out["2_positions"] = dict(most_end_locked=P.sort_values("end_frac", ascending=False).head(5)[["sign", "n", "end_frac"]].to_dict("records"),
                          most_start_locked=P.sort_values("start_frac", ascending=False).head(5)[["sign", "n", "start_frac"]].to_dict("records"))

# 3. complementary distribution
ctx = defaultdict(Counter); co = Counter()
for t in texts:
    tt = ("^",) + t + ("$",)
    for i in range(1, len(tt) - 1):
        ctx[tt[i]][("L", tt[i - 1])] += 1; ctx[tt[i]][("R", tt[i + 1])] += 1
    u = sorted(set(t))
    for i in range(len(u)):
        for j in range(i + 1, len(u)):
            co[(u[i], u[j])] += 1
common = [s for s in freq if freq[s] >= 20]
def cos(a, b):
    ks = set(ctx[a]) | set(ctx[b])
    va = np.array([ctx[a][k] for k in ks], float); vb = np.array([ctx[b][k] for k in ks], float)
    return float(va @ vb / np.linalg.norm(va) / np.linalg.norm(vb))
rows = []
ntext = {s: sum(s in t for t in texts) for s in common}
for i, a in enumerate(common):
    for b in common[i + 1:]:
        c = cos(a, b)
        if c > 0.5:
            rows.append(dict(a=a, b=b, context_similarity=round(c, 3), texts_with_both=co[(min(a, b), max(a, b))],
                             expected_if_independent=round(ntext[a] * ntext[b] / len(texts), 1)))
Q = pd.DataFrame(rows).sort_values("context_similarity", ascending=False)
Q.to_csv(ROOT / "results" / "context_pairs.csv", index=False)
out["3_context_pairs"] = Q.head(10).to_dict("records")
json.dump(out, open(ROOT / "results" / "probes.json", "w"), indent=1, default=float)
print(json.dumps(out, indent=1, default=float))
