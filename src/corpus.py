"""Load the digitized Koskenniemi & Parpola (1979) corpus.

Conventions of the digitized corpus (see data/koskenni_indus/digitized/README.md):
- sign numbers are the 1979 sign-list ranks (1..401); 395..401 are auxiliary marks, not signs
- the first token of `text` is the first sign in reading order
- '/' is a line/side boundary or a wrap of the printed list line
- a '*' after a sign marks an uncertain (underlined) reading
"""
import re
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
KP = ROOT / "data" / "koskenni_indus" / "digitized" / "corpus_inscriptions.tsv"
CISI = ROOT / "data" / "mayig" / "corpus"
MAX_SIGN = 394          # ranks above this are auxiliary marks
SEAL = "11"             # type code of seals


def load_inscriptions():
    d = pd.read_csv(KP, sep="\t", dtype=str)
    d["text"] = d["text"].fillna("")
    return d


def tokens(text):
    """All sign tokens of an inscription, boundaries ignored. Uncertain readings kept."""
    out = []
    for tok in text.split():
        num = re.sub(r"\D", "", tok)
        if num and int(num) <= MAX_SIGN:
            out.append(int(num))
    return tuple(out)


def unbroken_text(text):
    """The sign sequence of an inscription that has no boundary and no uncertain sign,
    else None. Used for positional statistics, where boundaries and misreads matter."""
    if "/" in text or "*" in text:
        return None
    seq = tokens(text)
    return seq if seq else None


def seals_with_animal(codes="main"):
    """Seals (type 11) with a readable text and a motif code, one row per distinct (text, motif) pair.
    Returns a DataFrame with columns seq, icon_code, unicorn.

    The key to the motif codes is in the 1973 concordance (table IV), which is not online. Code 40 is
    the unicorn (confirmed against CISI, see match_cisi.py). Code 99 is used for objects with no motif
    (1,216 of its 1,249 uses are on non-seal objects). The other codes are unnamed categories here.
    codes="main": codes 40..89.   codes="all": codes 40..98 (adds 90..98, 308 seals, mostly code 91)."""
    d = load_inscriptions()
    d = d[d.type_code == SEAL].copy()
    d["seq"] = d.text.apply(tokens)
    d = d[d.seq.str.len() > 0]
    pattern = r"^[4-8]\d$" if codes == "main" else r"^(?:[4-8]\d|9[0-8])$"
    d = d[d.icon_code.fillna("").str.match(pattern)].copy()
    d["unicorn"] = (d.icon_code == "40").astype(int)
    n_before = len(d)
    d = d.drop_duplicates(["seq", "icon_code"]).reset_index(drop=True)
    d.attrs["n_before_dedup"] = n_before
    return d
