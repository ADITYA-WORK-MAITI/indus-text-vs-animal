"""How the stroke ('numeral') signs behave. Sign-list ranks of the short vertical strokes
(121..130 = 1..10 strokes) and the long strokes (144,145,147,150,151 = 1..5 strokes) were read off
the 1979 sign list (PDF pp. 20-21). Rank 119 is the common two-short-stroke form filed separately.
Writes results/numerals.json."""
import json
from collections import Counter, defaultdict
from corpus import load_inscriptions, unbroken_text, ROOT

SHORT = {121: 1, 122: 2, 123: 3, 124: 4, 125: 5, 126: 6, 127: 7, 128: 8, 129: 9, 130: 10}
LONG = {144: 1, 145: 2, 147: 3, 150: 4, 151: 5}
d = load_inscriptions()
texts = list(dict.fromkeys(t for t in d.text.apply(unbroken_text) if t))
out = {}
for name, S in [("short_strokes", SHORT), ("short_strokes_with_119_as_2", {**SHORT, 119: 2}), ("long_strokes", LONG)]:
    cnt = Counter(); nxt = defaultdict(Counter); posn = Counter()
    for t in texts:
        for i, x in enumerate(t):
            if x in S:
                v = S[x]; cnt[v] += 1
                nxt[v][t[i + 1] if i + 1 < len(t) else "END"] += 1
                posn["start" if i == 0 else ("end" if i == len(t) - 1 else "mid")] += 1
    out[name] = dict(count_by_value={str(k): v for k, v in sorted(cnt.items())}, position=dict(posn),
                     next_sign_top3={str(v): nxt[v].most_common(3) for v in sorted(cnt)})
json.dump(out, open(ROOT / "results" / "numerals.json", "w"), indent=1)
for k, v in out.items():
    print(k, v["count_by_value"], v["position"])
