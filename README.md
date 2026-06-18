# GSMG.IO 5 BTC Puzzle — SalPhaseIon Decode Notes

> **Status:** working notes / partial decode  
> **Scope:** SalPhaseIon text segmentation, confirmed decodes, and unresolved sections.  
> **Safety:** this document is intended for public GitHub presentation and does **not** claim to contain the final private key.

---

## 1. Purpose

This document reorganizes the current `Salphaseion decode.txt` working file into a clearer GitHub-style report.

Main goals:

- preserve the raw material separately;
- separate **confirmed decodes** from **hypotheses**;
- clearly mark unresolved sections;
- make the chain of operations reproducible;
- avoid mixing notes, guesses, and final-looking outputs in the same block.

Raw source is kept here:

```text
raw/Salphaseion_decode_raw.txt
```

---

## 2. Current decode status overview

| Part | Input / clue | Current status | Output / interpretation |
|---:|---|---|---|
| 1 | `dbbibfbhccbeg` | Partial / method clue | Points to **Bifid cipher / Part4 decode**; exact final plaintext still not fully documented. |
| 2 | `bihabebeih...` | **Unresolved** | No strong plaintext yet. Needs focused analysis. |
| 3 | `abba...` binary section | Confirmed | `matrixsumlist` |
| 4 | long `faed...` section | Partially decoded | Produces `btcseed...` intermediate; odd/even substreams unresolved. |
| 5 | `z ... z ...` a-i-o sections | Confirmed | `lastwordsbeforearchichoice`, `thispassword` |
| 6 | `shabef` | Confirmed | `sha256` |
| 7 | `ourfirsthintisyourlastcommand` | Confirmed | `our first hint is your last command` |
| 8 | AES blob + `enter` token | Confirmed | AES blob decrypted with constructed password. |
| 9 | `shabef` | Confirmed | `sha256` repeated clue. |
| 10 | `anstoo` | High-confidence hypothesis | `ans too` → `answer two` → `secondanswer` |

---

## 3. Normalization

Original text contains spaces between symbols. A normalized no-space version is useful for segmentation.

Recommended workflow:

1. Preserve the original spaced text in `raw/`.
2. Create a no-space working stream.
3. Segment into parts using known delimiters:
   - binary-like `abba...` chunks;
   - `z` separators;
   - literal text fragments such as `shabef`, `ourfirsthintisyourlastcommand`;
   - AES `U2FsdGVk...` blocks.

---

## 4. Confirmed decodes

### 4.1 Part 3 — binary `abba...` → `matrixsumlist`

Input pattern:

```text
abbabbababbaaaababbbabaaabbbaabaabbabaababbbbaaaabbbaabbabbbabababbabbababbabbaaabbabaababbbaabbabbbabaa
```

Method:

```text
a = 0
b = 1
binary -> ASCII
```

Output:

```text
matrixsumlist
```

---

### 4.2 Part 5 — a-i-o alphabet → hex/plaintext

Observation:

Characters are mainly:

```text
a b c d e f g h i o
```

Interpretation:

```text
a-i = 1-9
o   = 0
```

Then convert the numeric stream through base/hex into ASCII.

Confirmed outputs:

```text
agdafaoaheiecggchgicbbhcgbehcfcoabicfdhhcdbbcagbdaiobbgbeadedde
-> lastwordsbeforearchichoice

cfobfdhgdobdgooiigdocdaoofidh
-> thispassword
```

---

### 4.3 Part 6 / Part 9 — `shabef` → `sha256`

Known mapping:

```text
shabef -> sha256
```

Interpretation:

```text
sha = literal prefix
b = 2
e = 5
f = 6
```

Output:

```text
sha256
```

---

### 4.4 Part 7 — literal command phrase

Input:

```text
ourfirsthintisyourlastcommand
```

Output:

```text
our first hint is your last command
```

This is an instruction, not merely decorative plaintext.

---

### 4.5 Part 8 — AES blob reconstruction

Part 8 contains:

1. AES blob prefix beginning with `U2FsdGVk...`;
2. an `abba...` section decoding to `enter`;
3. AES blob continuation;
4. command tokens already decoded earlier.

Confirmed `enter` token:

```text
abbaabababbabbbaabbbabaaabbaabababbbaaba
-> enter
```

Constructed password pattern:

```text
matrixsumlist + enter + lastwordsbeforearchichoice + thispassword + matrixsumlist
```

OpenSSL command form:

```bash
openssl enc -aes-256-cbc -d -a -md md5 \
  -in aesblob.txt \
  -pass pass:<constructed-password>
```

> Note: exact long decrypted hex values are kept in the raw notes, not repeated here.

---

## 5. Unresolved sections

## 5.1 Part 2 — unresolved

Input:

```text
bihabebeihbeggegebebbgehhebhhfbabfdhbeffcdbbfcccgbfbeeggecbedcibfbffgigbeeeabe
```

Known facts:

```text
length = 78
alphabet = a-i only
```

Controlled tests already tried:

- simple a1/a0 decimal conversion;
- large integer → hex → ASCII;
- Bifid 3×3 and 5×5 smoke tests;
- A1 group sums with lengths 2, 3, 6, 13;
- Caesar scan of group-sum outputs.

Notable weak structural result:

```text
A1 group-sum by 3 -> shposnitovermmjiolsjpjsroh
```

This is not accepted as plaintext yet.

### TODO for Part 2

- Check if this part is a keyed Bifid/Trifid/Nihilist-style pointer to Part 4.
- Test period/key combinations using confirmed keywords:

```text
matrixsumlist
lastwordsbeforearchichoice
thispassword
ourfirsthintisyourlastcommand
secondanswer
```

- Compare against known command vocabulary:

```text
matrix, sum, list, enter, last, words, before, archi, choice, password, command
```

---

## 5.2 Part 4 — unresolved subpart

Raw Part 4 begins with:

```text
faedggeedfcbdabhhggcadcfeddgfdgbgigaaedggiafaecghggcdaihehahbahigceifgbfgefgaifabifagaegeac...
```

Current intermediate decode begins with:

```text
btcseed...
```

After removing `btcseed`, the stream splits cleanly into two equal substreams:

```text
odd  length = 282, alphabet = b/c/d/e only
even length = 282, alphabet = broad lowercase letters
```

This strongly suggests:

```text
odd  = mask/key/control stream
even = data/ciphertext stream
```

Current known substreams from notes:

```text
odd/even split exists, but no accepted plaintext yet.
```

Controlled tests already tried:

- Vigenere / Beaufort on the even stream with known keys;
- Bacon-style binary mapping on odd stream;
- base4 mappings on odd stream;
- odd as small shift key for even;
- simple transposition checks.

No strong plaintext was found.

### TODO for Part 4

Priority hypotheses:

1. **Odd stream as instruction mask**  
   Since odd contains only `b/c/d/e`, it may encode 4 states:

   ```text
   b c d e -> 0/1/2/3 or direction/control symbols
   ```

2. **Even stream as routed text**  
   The even stream has natural-language-like IC but no immediate Caesar/Vigenere decode.

3. **Use confirmed prefix `btcseed`**  
   The prefix may be a direct instruction:

   ```text
   btc seed
   seed for BTC
   seed is password
   ```

4. **Test as route rather than ciphertext**  
   Odd/even may not decode to plaintext directly; it may select positions in the larger SalPhaseIon stream.

---

## 5.3 Part 10 — `anstoo`

Input:

```text
anstoo
```

Competing interpretations:

| Interpretation | Status |
|---|---|
| `ans2000` / external website | Weak / speculative |
| OEIS `A141920` | Interesting but unconfirmed |
| `ans too` → `answer two` | Strong semantic fit |
| `secondanswer` | Current best hypothesis |

Current preferred output:

```text
secondanswer
```

Reason:

```text
anstoo = ans too = answer too/two = second answer
```

This also matches known token style in the puzzle:

```text
secondanswer
```

---

## 6. Suggested GitHub file layout

```text
salphaseion/
├── README.md
├── raw/
│   └── Salphaseion_decode_raw.txt
├── scripts/
│   └── salphaseion_unresolved_probe.py
└── results/
    ├── salphaseion_unresolved_probe_summary.txt
    └── salphaseion_unresolved_probe_results.tsv
```

---

## 7. Reproducibility commands

Run the controlled unresolved-section probe:

```bash
python3 scripts/salphaseion_unresolved_probe.py
```

Expected current result:

```text
Part2: no accepted plaintext yet
Part4: btcseed split confirmed, subdecode unresolved
Part10: secondanswer high-confidence
```

---

## 8. Current open questions

1. What is the exact decode for Part 2?
2. Is Part 2 a pointer to Part 4, or an independent token?
3. How should the Part 4 `btcseed` odd/even streams be interpreted?
4. Does `btcseed` imply a seed phrase, a Bitcoin seed, or a route seed?
5. Is `secondanswer` needed as a token in the later Cosmic Duality / blob3 password construction?

---

## 9. Current best conclusions

```text
Part 2  -> unresolved
Part 4  -> partially decoded to btcseed...; odd/even substreams unresolved
Part 10 -> secondanswer
```

The safest next research focus is Part 4, because its `btcseed` prefix looks intentional and operational.
