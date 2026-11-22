# Audit notes

What was checked before release, what was found, and what changed.

## Parsing of the corpus

- Read the digitized corpus README. Confirmed: the first token of `text` is the first sign in reading order; `/` marks a line or side boundary, or a wrap of the printed list line; `*` marks an uncertain reading; ranks 395 to 401 are auxiliary marks. The code drops ranks above 394. Checked that the sign list runs from 1 to 401.
- For single-line seals, `/` appears in only 65 of 3,351 inscriptions, so ignoring it for the sign-presence test is harmless. The positional probes now use only inscriptions with no `/` and no `*`. The earlier version split texts at `/`, which could create false starts and ends.
- Motif code 40 = unicorn: re-derived from scratch by exact sign-for-sign matching against the CISI corpus. 27 of 28 exact matches carry code 40; the one exception carries code 99 (no identified motif), probably a duplicate text on another object.

## Statistics

- The main AUC, p-value, FDR result and mutual-information test were rerun from the refactored code and reproduce the earlier numbers (AUC 0.511, p 0.36; 0 signs at FDR 5%; MI non-unicorn p 0.013, earlier 0.02 from a different random seed).
- The permutation p-values use (count + 1) / (runs + 1), which is the conservative form.
- Duplicate seals are collapsed on (text, motif). Collapsing on text alone would merge the same text on different animals; that choice is deliberate and documented.
- The power check plants one extra column. It measures detectability of a single sign-animal link, not of a diffuse signal.

## Second pass

- The 1979 volume states that the motif-code key is in the 1973 concordance (table IV), which is not online. The first pass described codes 40 to 89 as "identified motifs" as if from a key; that was an inference from the code distribution across object types. The README now says exactly what is and is not known, and a sensitivity run that adds codes 90 to 98 was added. The null result holds in both runs.
- Test C now also reports balanced accuracy from text length alone. Nearly all of the weak "which code" signal is length, so it is a property of the objects, not of the signs.
- Bug fixed in `probes.py`: co-occurrence counts were looked up with the pair in iteration order rather than sorted order, so pairs where the first sign number was larger read as 0. Only the "texts_with_both" column of `context_pairs.csv` was affected; the 324/325 pair quoted in the README was in sorted order and unchanged.

## Code changes made during the audit

- Replaced the earlier `exec(...)` hacks (scripts re-running each other's source) with a shared module `corpus.py`.
- Fixed a crash when writing results: numpy integers are now converted before JSON output.
- Every script now writes its results to `results/` instead of only printing them.
- Added the structural probes and numerals scripts, which were missing from the earlier bundle.

## Known weaknesses that remain

- Mutual-information test D shows a weak but nominally significant signal among non-unicorn seals (p = 0.013). It is reported, not hidden, and it is too weak to predict anything.
- The digitized corpus has 26 low-confidence sign readings; they are included.
- The C test random split can shift p between about 0.06 and 0.09 across seeds.
