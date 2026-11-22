"""Does the text on a seal predict the animal carved below it?
A: held-out prediction of unicorn vs other animal from the signs (logistic regression, 5-fold).
B: per-sign Fisher tests, unicorn vs other, with Benjamini-Hochberg FDR.
C: multi-class prediction of the motif code among codes with >= 15 seals.
D: total mutual information between sign presence and motif code, against shuffled labels.
Usage: python3 src/icon_test.py [main|all]   ('all' also includes motif codes 90..98; see corpus.py)
Writes results/icon_test[_all_codes].json, results/sign_association[_all_codes].csv, results/confusion_matrix[_all_codes].csv."""
import json, sys
import numpy as np, pandas as pd
from scipy.stats import fisher_exact
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import roc_auc_score, log_loss, mutual_info_score, balanced_accuracy_score
from corpus import seals_with_animal, ROOT

rng = np.random.default_rng(0)
CODES = sys.argv[1] if len(sys.argv) > 1 else "main"
SUFFIX = "" if CODES == "main" else "_all_codes"
d = seals_with_animal(CODES)
signs = sorted({s for q in d.seq for s in q})
X = np.array([[int(s in set(q)) for s in signs] for q in d.seq])
y = d.unicorn.values
out = dict(motif_codes=CODES, n_seals_before_dedup=d.attrs["n_before_dedup"], n_seals=len(d),
           unicorn_share=float(y.mean()), n_signs=len(signs))


def cv_auc(X, y, seed=0, C=0.5):
    skf = StratifiedKFold(5, shuffle=True, random_state=seed)
    p = cross_val_predict(LogisticRegression(C=C, max_iter=2000), X, y, cv=skf, method="predict_proba")[:, 1]
    return roc_auc_score(y, p), log_loss(y, p)


# A
auc, ll = cv_auc(X, y)
perm = np.array([cv_auc(X, rng.permutation(y), seed=i)[0] for i in range(200)])
out["A_unicorn_vs_other"] = dict(auc=auc, log_loss=ll, base_log_loss=log_loss(y, np.full(len(y), y.mean())),
                                 auc_length_only=cv_auc(d.seq.str.len().values.reshape(-1, 1), y)[0],
                                 shuffled_auc_mean=float(perm.mean()), shuffled_auc_max=float(perm.max()),
                                 p_value=float((np.sum(perm >= auc) + 1) / (len(perm) + 1)))
print("A:", json.dumps(out["A_unicorn_vs_other"], indent=1))

# B
rows = []
for j, s in enumerate(signs):
    a = int(X[y == 0, j].sum()); b = int((y == 0).sum()) - a
    c = int(X[y == 1, j].sum()); e = int((y == 1).sum()) - c
    if a + c < 8:
        continue
    _, p = fisher_exact([[a, b], [c, e]])
    rows.append(dict(sign=s, seals_other=a, seals_unicorn=c, rate_other=a / (a + b), rate_unicorn=c / (c + e), p=p))
t = pd.DataFrame(rows).sort_values("p").reset_index(drop=True)
m = len(t)
t["q_fdr"] = (t.p * m / np.arange(1, m + 1))[::-1].cummin()[::-1].clip(upper=1)
t.to_csv(ROOT / "results" / f"sign_association{SUFFIX}.csv", index=False)
out["B_per_sign"] = dict(signs_tested=m, significant_at_fdr_05=int((t.q_fdr < 0.05).sum()),
                         smallest_q=float(t.q_fdr.min()))
print("B:", out["B_per_sign"])

# C
top = d.icon_code.value_counts()
keep = top[top >= 15].index
dd = d[d.icon_code.isin(keep)]
Xc = np.array([[int(s in set(q)) for s in signs] for q in dd.seq])
yc = np.asarray(dd.icon_code.astype(str).values, dtype=object)
skf = StratifiedKFold(5, shuffle=True, random_state=0)
pred = cross_val_predict(LogisticRegression(C=0.5, max_iter=3000), Xc, yc, cv=skf)
nu = yc != "40"
Lc = dd.seq.str.len().values.reshape(-1, 1).astype(float)
def bacc(lbl, feats, seed=0):
    skf = StratifiedKFold(5, shuffle=True, random_state=seed)
    pr = cross_val_predict(LogisticRegression(C=0.5, max_iter=3000, class_weight="balanced"), feats[nu], lbl, cv=skf)
    return balanced_accuracy_score(lbl, pr)
b_obs = bacc(yc[nu], Xc)
b_len = bacc(yc[nu], Lc)
b_perm = np.array([bacc(rng.permutation(yc[nu]), Xc, i) for i in range(200)])
out["C_which_animal"] = dict(codes={k: int(v) for k, v in top[keep].items()}, accuracy=float(np.mean(pred == yc)),
                             always_unicorn=float(np.mean(yc == "40")),
                             non_unicorn_balanced_accuracy=float(b_obs), non_unicorn_balanced_accuracy_length_only=float(b_len),
                             chance=1 / (len(keep) - 1),
                             shuffled_mean=float(b_perm.mean()), p_value=float((np.sum(b_perm >= b_obs) + 1) / 201))
pd.crosstab(pd.Series(yc, name="true"), pd.Series(pred, name="predicted")).to_csv(ROOT / "results" / f"confusion_matrix{SUFFIX}.csv")
print("C:", out["C_which_animal"])

# D
def total_mi(Xm, lbl):
    return sum(mutual_info_score(lbl, Xm[:, j]) for j in range(Xm.shape[1]) if Xm[:, j].sum() >= 5)
res = {}
for name, Xm, lbl in [("all_codes", Xc, yc), ("non_unicorn_only", Xc[nu], yc[nu])]:
    obs = total_mi(Xm, lbl)
    pm = np.array([total_mi(Xm, rng.permutation(lbl)) for _ in range(300)])
    res[name] = dict(n=len(lbl), observed=obs, shuffled_mean=float(pm.mean()), shuffled_sd=float(pm.std()),
                     z=float((obs - pm.mean()) / pm.std()), p_value=float((np.sum(pm >= obs) + 1) / 301))
out["D_mutual_information"] = res
print("D:", json.dumps(res, indent=1))
json.dump(out, open(ROOT / "results" / f"icon_test{SUFFIX}.json", "w"), indent=1)
