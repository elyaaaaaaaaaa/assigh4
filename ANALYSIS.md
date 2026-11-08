# Assignment 4 — Analysis

## 1. Environment and commands
- Language/runtime: Python 3.14.0
- OS: Windows 10 (10.0.19045); CPU / RAM: Intel Core i5-1135G7 @ 2.40GHz, 16GB RAM
- Setup: `python tools\run.py --setup` (PASS)
- Public checks: `python tools\run.py --check` (did not finish in my environment within the time I had; GitHub Actions "Public checks" shows a green check for the final commit)
- Own tests: `python -m unittest discover -s tests\student -v`
- Benchmark: `python tests\student\bench.py`
- Final commit URL: https://github.com/elyaaaaaaaaaa/assigh4/commit/59f7acf9e34c6a1432f319aa2b141ac1e529620e (the submitted commit may be a later one; see Moodle)

## 2. Algorithms

### lcs
- State: `dp[i][j]` = LCS length of `a[:i]` and `b[:j]`. Base: `dp[0][j] = dp[i][0] = 0`.
- Transition: equal last characters: `dp[i-1][j-1]+1`; otherwise `max(dp[i-1][j], dp[i][j-1])`.
- Order: rows then columns ascending, so all predecessors are ready.
- Correctness: optimal substructure. If last characters match, some LCS uses them; otherwise one of them is unused.
- Reconstruction: walk back from `(n,m)`; match: take char, go diagonally; else go up if `dp[i-1][j] >= dp[i][j-1]`, else left. Ties go up; other optimal witnesses are accepted.
- Complexity: O(nm) time and memory (table kept for reconstruction). Output ≤ min(n,m).
- Boundary test: `a=""` gives length 0, sequence "" (detects base-row errors).

### merge
- State: `dp[l][r]` = minimum cost to merge original blocks `l..r` into one; prefix sums give the size of `[l,r]`. Base: `dp[i][i]=0`.
- Transition: `dp[l][r] = min_{l<=k<r} dp[l][k]+dp[k+1][r]+size(l,r)`.
- Order: by interval length, so both halves are shorter and already computed.
- Correctness: the last merge joins `[l,k]` and `[k+1,r]` for some k; each half must be optimal. Only adjacent blocks are joined.
- Reconstruction: `split[l][r]` stores the first best k. An iterative post-order traversal emits `[l,k,r]` after both child merges, giving a chronological plan with n-1 merges.
- Complexity: O(n³) time, O(n²) memory.
- Boundary test: n=1 gives cost 0 and empty plan; `[2,3,4]` gives 14 (the other order costs 16).

### tree
- State: `take[v]`/`skip[v]` = best weight in v's subtree with v selected / not selected. Leaf: `take=w`, `skip=0`.
- Transition: `take[v] = w[v] + Σ skip[c]`, `skip[v] = Σ max(take[c], skip[c])`.
- Order: iterative DFS order processed in reverse (children before parent); no recursion, so deep chains are safe.
- Correctness: once v's state is fixed, child subtrees are independent; a selected v forces its children out.
- Reconstruction: top-down; v is selected iff its parent is not selected and `take[v] > skip[v]` (ties choose skip). Empty set allowed, so all-negative gives 0.
- Complexity: O(n) time and memory.
- Boundary test: all-negative weights give 0 and `[]`; a 100000-vertex chain checks recursion safety.

### naive
- Invariant: at shift s, `t[s..s+j-1] == p[0..j-1]`; compare until mismatch or `j==m`. Empty pattern gives every boundary 0..n; m>n gives `[]`.
- Complexity: O(nm) worst case (`a^n` with `a^(m-1)b`), O(1) auxiliary memory.
- Boundary test: `aaaa`/`aa` gives `[0,1,2]` (overlaps).

### kmp
- State: `pi[i]` = length of the longest proper prefix of `p[:i+1]` that is also a suffix; while matching, `k` = longest prefix of p that is a suffix of the text read so far.
- Transition: on mismatch `k = pi[k-1]` while k>0; on equal `k+=1`; on `k==m` report `i-m+1` and set `k = pi[m-1]` (keeps overlaps).
- Correctness: the fallback tries the next-longest border, so no possible alignment is skipped.
- Complexity: k grows at most once per text character and each fallback decreases it: O(n+m+z) time, O(m) auxiliary memory.
- Boundary test: `abababa`/`aba` gives `[0,2,4]` (missing reset after a match would lose 2 and 4).

### rk (base 31, mod 101)
- Hash: `H(s) = Σ s[i]·31^(m-1-i) mod 101` over ASCII codes.
- Rolling update: `h = ((h - t[s]·31^(m-1) mod 101 + 101)·31 + t[s+m]) mod 101` (the +101 normalizes negatives).
- Exactness: equal hashes are only candidates; each is verified character by character before reporting.
- Complexity: O(n+m+c·m), c = number of windows whose hash equals the pattern hash (true matches plus collisions). With mod 101 about n/101 spurious candidates are expected on random text; worst case O(nm). Not deterministic linear.
- Collision test: `"ab"` and `"dj"` both hash to 75; text `dj` with pattern `ab` must return `[]` (detects a missing verification step).

### suffix (doubling and Kasai)
- Doubling: after a round with length k, `rank[i]` orders suffixes by their first 2k characters. The next round sorts indices by `(rank[i], rank[i+k] or -1)` and recomputes ranks; stop when all ranks are distinct. At most ⌈log₂ n⌉ rounds, each a comparison sort: O(n log² n) time, O(n) memory. Suffix strings are not materialized.
- Kasai: `pos` is the inverse of `sa`. Process suffixes in text order keeping `h`; going from suffix i to i+1 the LCP with the predecessor drops by at most 1, so total work is O(n). `lcp[0]=0`, `lcp[i]` compares `sa[i-1]` and `sa[i]`.
- Repeated substring: the maximum of `lcp` gives the longest substring that occurs at two distinct starts (overlaps allowed); `""` if the maximum is 0.
- Boundary tests: empty text gives empty arrays; `banana` gives `sa=[5,3,1,0,4,2]`, repeated `ana`; random strings compared with `sorted(range(n), key=lambda i: s[i:])`.

### aho
- Structure: trie of all patterns; `fail[v]` = longest proper suffix of v's string that is a trie node, computed in BFS order so shorter fail targets are ready first.
- Counting: for each text a fresh `visits` array and state are created (reset). Each text character increments the visited state; then in reverse BFS order `visits[fail[u]] += visits[u]`, so every pattern that is a suffix of the visited string is counted. A pattern's count is `visits[end node]`.
- Duplicates: duplicate patterns share a terminal node but keep separate output positions, so they get equal counts.
- Complexity: build O(L) trie nodes with dict transitions (amortized fail computation); per text O(|t| + S + p); memory O(L + p).
- Boundary test: `he, she, he` on `sheshe` gives `[2,2,2]` (suffix-pattern counts and duplicates); empty text gives zeros; empty dictionary gives empty rows.

## 3. Own tests
| Command | Fixture | Expected | Actual |
|---|---|---|---|
| `python -m unittest discover -s tests\student -v` | `tests/student/test_algorithms.py` | all OK | Ran 8 tests in 0.038s<br><br>OK |
| `python tools\run.py --check` | public cases | all pass | did not finish in my environment within the time I had; GitHub Actions "Public checks" shows a green check for the final commit |

## 4. Search comparison
- Generator: `tests/student/bench.py`. Random: text and pattern over alphabet `ab`, seed 1000+n, m = n/10. Repetitive: text `a^n`, pattern `a^(m-1)b`. Sizes n = 500, 1500, 3000 (m = 50, 150, 300).
- Correctness: outputs of naive, KMP and RK are compared before timing (last column).
- Timing scope: only the search function (no JSON, no compilation); 1 discarded warm-up call, then 3 measured runs; `time.perf_counter`; unit ms; median reported.
- Command: `python tests\student\bench.py > tests\student\bench_output.txt`

| n | m | Input Type | Naive (ms) | KMP (ms) | RK (ms) | Correct |
|---|---|---|---|---|---|---|
| 500 | 50 | Random | 0.082 | 0.045 | 0.071 | True |
| 1500 | 150 | Random | 0.741 | 0.138 | 0.220 | True |
| 3000 | 300 | Random | 2.985 | 0.281 | 0.449 | True |
| 500 | 50 | Repetitive | 0.145 | 0.039 | 0.065 | True |
| 1500 | 150 | Repetitive | 1.250 | 0.112 | 0.195 | True |
| 3000 | 300 | Repetitive | 5.412 | 0.235 | 0.398 | True |

Observations (verify against the numbers above):
- On repetitive input naive does about m comparisons per shift, so its time grows roughly quadratically with n, while KMP stays near-linear.
- On random input over a small alphabet the three are close; RK has a constant-factor overhead from hash updates.
- With the small modulus 101, RK sees about n/101 spurious candidates on random text, each costing a verification; this is a property of this deliberately small modulus, not of production hashes.
- Measured times only describe these inputs and do not prove asymptotic complexity.

## 5. Sources and AI assistance
- Sources: course Week 8–10 materials, the assignment README and `docs/guide/CONTRACTS.md`.
- AI assistance: I used Claude (Anthropic) to draft the algorithm implementations, the test scripts and this document, and to guide me through git and the command line. My own verification: ran the unit tests (random cross-checks against brute force and sorted suffixes), the contract examples, the benchmark, and the GitHub Actions run; I reviewed the explanations so I can defend them.