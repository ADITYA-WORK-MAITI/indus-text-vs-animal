# Indus seals: does the text depend on the animal?

A statistical test of one open question about the undeciphered Indus script. Most Indus seals carry a short inscription above a carved animal. Is the inscription related to the animal?

**Result: no measurable relation.** A model that sees only the signs cannot tell whether a seal shows a unicorn or another animal (held-out AUC 0.51, chance 0.50, p = 0.36 against shuffled labels). No single sign is tied to an animal after correcting for multiple tests. The same test would detect a sign that appears on only 20 to 30% of one animal's seals. So the inscription is not a caption or a description of the animal.

All numbers below come from the scripts in `src/` and can be rerun with one command.

## Data

- [Koskenniemi & Parpola 1979, *Corpus of Texts in the Indus Script*](https://github.com/koskenni/indus), machine-read into TSV files. 4,066 inscriptions. The digitization has been spot-checked but not fully proofread.
- [CISI digitization by mayig](https://github.com/mayig/indus-valley-script-corpus) (MIT/Apache), used only to confirm which motif code means "unicorn".

Neither corpus is stored in this repository. `setup.sh` downloads them into `data/`.

## Run it

```
./setup.sh      # clones the two corpora, installs Python packages
./run_all.sh    # about 10 minutes; writes results/ and figures/
```

Python 3.10 or later.

## What each script does

| Script | Question | Output |
|---|---|---|
| `src/corpus.py` | Loads and cleans the corpus (shared by all scripts) | |
| `src/match_cisi.py` | Confirms motif code 40 = unicorn by matching texts against CISI | `results/icon_code_vs_cisi_description.csv` |
| `src/icon_test.py` | The main test, parts A to D (`main` or `all` codes) | `results/icon_test.json`, `icon_test_all_codes.json`, `sign_association*.csv`, `confusion_matrix*.csv` |
| `src/power_check.py` | How strong an association the test could detect | `results/power_check.json` |
| `src/chart.py` | Figure | `figures/signs_vs_animal.png` |
| `src/probes.py` | Three structural probes, unrelated to the animal question | `results/probes.json`, `positions.csv`, `context_pairs.csv` |
| `src/numerals.py` | How the stroke signs behave | `results/numerals.json` |

## Method

Seals only (type code 11). Each inscription is reduced to the set of signs it contains. Signs 395 to 401 are auxiliary marks and are dropped. Duplicate (text, motif) pairs are collapsed.

The key to the motif codes is in the 1973 concordance, which is not online. Code 40 is the unicorn, confirmed by 27 of 28 exact text matches against CISI. Code 99 means no motif (1,216 of its 1,249 uses are on uninscribed or non-seal objects). The other codes are used as unnamed categories. The main run uses codes 40 to 89 (1,156 seals, 77% unicorns). A sensitivity run adds codes 90 to 98 (1,362 seals), in case any of those are animals too.

- **A.** Logistic regression on sign presence, 5-fold cross-validation, unicorn vs any other code. Compared with 200 runs on shuffled labels.
- **B.** Fisher's exact test per sign (signs on 8 or more seals), Benjamini-Hochberg FDR.
- **C.** Multi-class prediction of the motif code among codes with 15 or more seals; balanced accuracy among the non-unicorn seals against shuffled labels, and the same with text length as the only feature.
- **D.** Total mutual information between sign presence and motif code, against 300 shuffles.

## Results

| Test | Main run (codes 40-89) | Sensitivity run (codes 40-98) |
|---|---|---|
| A. AUC, unicorn vs other, from signs | 0.51, p = 0.36 (shuffled: mean 0.50, max 0.60) | 0.53, p = 0.09 |
| A. AUC from text length alone | 0.56 | 0.60 |
| B. Signs significant at FDR 5% | 0 of 109 (smallest q = 0.22) | 0 of 115 |
| C. Which code, non-unicorn seals, balanced accuracy from signs | 0.22 (chance 0.17), p = 0.08 | 0.16 (chance 0.11), p = 0.005 |
| C. Same, from text length only | 0.20 | 0.16 |
| D. Mutual information, all codes, p | 0.06 | 0.06 |
| D. Mutual information, non-unicorn seals only, p | 0.01 | 0.01 |

Power check: planting one sign on 10 / 20 / 30% of the non-unicorn seals (and 5% of unicorn seals) raises the AUC to 0.52 / 0.57 / 0.62. A sign that named the animal would appear on most of that animal's seals and would be detected easily.

What signal there is comes from text length, not from which signs are used. In test C, length alone reaches almost the same balanced accuracy as the full sign set (0.20 of 0.22; 0.16 of 0.16). Unicorn seals tend to carry slightly longer texts, and the codes 90 to 98 added in the sensitivity run carry shorter ones, which fits damaged or unclear objects. Test D finds a faint excess over chance among the non-unicorn seals (p = 0.01). It is too weak to predict anything and is consistent with the same length effect, or with site or period effects.

### Structural probes (exploratory)

These use the 1,535 distinct inscriptions with no line break and no uncertain sign.

- 5.6% of inscriptions with 5 or more signs can be split entirely into shorter inscriptions that occur on their own. Shuffled texts: 0.03%.
- Some signs are strongly position-locked. Sign 217 ends a text in 84% of its 127 uses. Sign 98 ends a text in 80% of 127 uses.
- Signs 324, 325 and 326 occur in near-identical contexts (cosine similarity 0.98) but rarely together: 324 and 325 co-occur in 31 texts against 88 expected if independent. This fits variant forms of one sign or ending.
- Stroke signs: counting the separately filed two-stroke form (rank 119) as "two", the counts for 1 to 7 strokes are 259, 397, 114, 31, 30, 18, 45. "Seven" is over-represented relative to 4 to 6, as Farmer noted earlier.

None of these probes produced a new finding. They are included for completeness.

## Limits

- The 1979 corpus misses everything excavated since then.
- The key to the motif codes is in a 1973 volume not available online. Only code 40 (unicorn) is confirmed. The other codes are unnamed categories; the sensitivity run shows the result does not depend on where the line between "animal" and "other" codes is drawn.
- The digitized corpus was machine-read and is not fully proofread.
- Sign identities (except the numerals, read from the 1979 sign list) are not interpreted here.
- Whether this exact test has been published before was not established.

## License

Code: MIT. The corpora have their own terms; see their repositories.
