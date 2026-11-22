"""How strong an association would the test in icon_test.py detect?
Plant one extra sign on a fraction of the non-unicorn seals (and on 5% of unicorn seals)
and rerun the held-out AUC. Writes results/power_check.json."""
import json
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import roc_auc_score
from corpus import seals_with_animal, ROOT

rng = np.random.default_rng(1)
d = seals_with_animal()
signs = sorted({s for q in d.seq for s in q})
X = np.array([[int(s in set(q)) for s in signs] for q in d.seq]); y = d.unicorn.values

def auc(Xm, seed):
    skf = StratifiedKFold(5, shuffle=True, random_state=seed)
    p = cross_val_predict(LogisticRegression(C=0.5, max_iter=2000), Xm, y, cv=skf, method="predict_proba")[:, 1]
    return roc_auc_score(y, p)

def plant(frac):
    col = np.zeros(len(y), int)
    other, uni = np.where(y == 0)[0], np.where(y == 1)[0]
    col[rng.choice(other, int(frac * len(other)), replace=False)] = 1
    col[rng.choice(uni, int(0.05 * len(uni)), replace=False)] = 1
    return np.hstack([X, col[:, None]])

res = {}
for frac in [0.1, 0.2, 0.3]:
    a = [auc(plant(frac), i) for i in range(10)]
    res[f"sign_on_{int(frac*100)}pct_of_other_seals"] = dict(auc_mean=float(np.mean(a)), auc_sd=float(np.std(a)))
    print(frac, res[f"sign_on_{int(frac*100)}pct_of_other_seals"])
json.dump(res, open(ROOT / "results" / "power_check.json", "w"), indent=1)
