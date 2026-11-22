"""Confirm what the icon codes mean by matching inscriptions against the CISI digitization,
whose records carry a free-text description (e.g. 'unicorn') and sign numbers in the same
1979 numbering. CISI stores graphemes in the opposite order, so sequences are reversed.
Writes results/cisi_matches.csv and results/icon_code_vs_cisi_description.csv."""
import glob, json, re
import numpy as np, pandas as pd
from corpus import load_inscriptions, tokens, CISI, ROOT

kp = load_inscriptions()
kp["seq"] = kp.text.apply(tokens)
by_len = {}
for seq, num, icon in zip(kp.seq, kp.number, kp.icon_code):
    by_len.setdefault(len(seq), []).append((seq, num, icon))

rows = []
for f in sorted(glob.glob(str(CISI / "*" / "*.json"))):
    for side in json.load(open(f)):
        g = tuple(int(x["id"][1:]) for x in side["graphemes"] if re.match(r"P\d+$", x["id"]))[::-1]
        if len(g) < 3:
            continue
        best = (np.inf, None, None)
        for seq, num, icon in by_len.get(len(g), []):
            dist = np.mean([abs(a - b) for a, b in zip(g, seq)])
            if dist < best[0]:
                best = (dist, num, icon)
        rows.append(dict(cisi=side["id"], description=side["description"], n_signs=len(g),
                         mean_sign_diff=best[0], kp_number=best[1], icon_code=best[2]))
r = pd.DataFrame(rows)
r.to_csv(ROOT / "results" / "cisi_matches.csv", index=False)
exact = r[r.mean_sign_diff == 0].copy()
exact["animal"] = exact.description.str.replace(r"\b[IVX]+\b", "", regex=True).str.strip()
ct = pd.crosstab(exact.animal, exact.icon_code)
ct.to_csv(ROOT / "results" / "icon_code_vs_cisi_description.csv")
print(f"CISI sides with 3+ signs: {len(r)}; exact sign-for-sign matches to the 1979 corpus: {len(exact)}")
print(ct.to_string())
