"""Algorithm implementations. Inputs and outputs are dictionaries (see CONTRACTS.md)."""
from collections import deque


def lcs(request):
    a = request.get("a", "")
    b = request.get("b", "")
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    i, j, res = n, m, []
    while i and j:
        if a[i - 1] == b[j - 1]:
            res.append(a[i - 1]); i -= 1; j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    return {"length": dp[n][m], "sequence": "".join(reversed(res))}


def merge(request):
    sizes = request.get("sizes", [])
    n = len(sizes)
    if n <= 1:
        return {"cost": 0, "plan": []}
    P = [0]
    for s in sizes:
        P.append(P[-1] + s)
    INF = float("inf")
    dp = [[0] * n for _ in range(n)]
    sp = [[-1] * n for _ in range(n)]
    for length in range(2, n + 1):
        for l in range(0, n - length + 1):
            r = l + length - 1
            best, bk = INF, -1
            tot = P[r + 1] - P[l]
            for k in range(l, r):
                c = dp[l][k] + dp[k + 1][r] + tot
                if c < best:
                    best, bk = c, k
            dp[l][r], sp[l][r] = best, bk
    plan, stack = [], [(0, n - 1, False)]
    while stack:
        l, r, done = stack.pop()
        if l == r:
            continue
        k = sp[l][r]
        if done:
            plan.append([l, k, r])
        else:
            stack.append((l, r, True))
            stack.append((k + 1, r, False))
            stack.append((l, k, False))
    return {"cost": dp[0][n - 1], "plan": plan}


def tree(request):
    w = list(request.get("weights", []))
    edges = request.get("edges", [])
    n = len(w)
    if n == 0:
        return {"weight": 0, "selected": []}
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v); adj[v].append(u)
    parent, order, seen = [-1] * n, [], [False] * n
    for root in range(n):
        if seen[root]:
            continue
        seen[root] = True
        stack = [root]
        while stack:
            v = stack.pop(); order.append(v)
            for c in adj[v]:
                if not seen[c]:
                    seen[c] = True; parent[c] = v; stack.append(c)
    take, skip = w[:], [0] * n
    for v in reversed(order):
        p = parent[v]
        if p >= 0:
            take[p] += skip[v]
            skip[p] += max(take[v], skip[v])
    chosen = [False] * n
    total = 0
    for v in order:
        p = parent[v]
        if p < 0:
            total += max(take[v], skip[v])
        chosen[v] = (p < 0 or not chosen[p]) and take[v] > skip[v]
    return {"weight": total, "selected": [v for v in range(n) if chosen[v]]}


def naive(request):
    t = request.get("text", "")
    p = request.get("pattern", "")
    n, m = len(t), len(p)
    res = []
    for s in range(n - m + 1):
        j = 0
        while j < m and t[s + j] == p[j]:
            j += 1
        if j == m:
            res.append(s)
    return {"positions": res}


def kmp(request):
    t = request.get("text", "")
    p = request.get("pattern", "")
    n, m = len(t), len(p)
    if m == 0:
        return {"positions": list(range(n + 1))}
    pi, k = [0] * m, 0
    for i in range(1, m):
        while k and p[i] != p[k]:
            k = pi[k - 1]
        if p[i] == p[k]:
            k += 1
        pi[i] = k
    res, k = [], 0
    for i in range(n):
        while k and t[i] != p[k]:
            k = pi[k - 1]
        if t[i] == p[k]:
            k += 1
        if k == m:
            res.append(i - m + 1)
            k = pi[k - 1]
    return {"positions": res}


def rk(request):
    t = request.get("text", "")
    p = request.get("pattern", "")
    n, m = len(t), len(p)
    B, M = 31, 101
    if m > n:
        return {"positions": []}
    if m == 0:
        return {"positions": list(range(n + 1))}
    high = 1
    for _ in range(m - 1):
        high = high * B % M
    hp = ht = 0
    for i in range(m):
        hp = (hp * B + ord(p[i])) % M
        ht = (ht * B + ord(t[i])) % M
    res = []
    for s in range(n - m + 1):
        if hp == ht:
            j = 0
            while j < m and t[s + j] == p[j]:
                j += 1
            if j == m:
                res.append(s)
        if s + m < n:
            ht = ((ht - ord(t[s]) * high % M + M) * B + ord(t[s + m])) % M
    return {"positions": res}


def suffix(request):
    s = request.get("text", "")
    n = len(s)
    if n == 0:
        return {"sa": [], "lcp": [], "repeated": ""}
    sa = list(range(n))
    rank = [ord(c) for c in s]
    k = 1
    while True:
        def key(i, rank=rank, k=k):
            return (rank[i], rank[i + k] if i + k < n else -1)
        sa.sort(key=key)
        tmp = [0] * n
        for i in range(1, n):
            tmp[sa[i]] = tmp[sa[i - 1]] + (key(sa[i - 1]) < key(sa[i]))
        rank = tmp
        if rank[sa[-1]] == n - 1 or k >= n:
            break
        k <<= 1
    pos = [0] * n
    for i, x in enumerate(sa):
        pos[x] = i
    lcp, h = [0] * n, 0
    for i in range(n):
        if pos[i] > 0:
            j = sa[pos[i] - 1]
            while i + h < n and j + h < n and s[i + h] == s[j + h]:
                h += 1
            lcp[pos[i]] = h
            if h:
                h -= 1
        else:
            h = 0
    best = max(range(n), key=lambda i: lcp[i])
    rep = s[sa[best]:sa[best] + lcp[best]] if lcp[best] > 0 else ""
    return {"sa": sa, "lcp": lcp, "repeated": rep}


def aho(request):
    pats = request.get("patterns", [])
    texts = request.get("texts", [])
    go, fail, order_end = [{}], [0], []
    for p in pats:
        v = 0
        for c in p:
            if c not in go[v]:
                go[v][c] = len(go)
                go.append({}); fail.append(0)
            v = go[v][c]
        order_end.append(v)
    bfs, q = [], deque(go[0].values())
    while q:
        v = q.popleft(); bfs.append(v)
        for c, u in go[v].items():
            f = fail[v]
            while f and c not in go[f]:
                f = fail[f]
            fail[u] = go[f].get(c, 0)
            q.append(u)
    rows = []
    for t in texts:
        visits = [0] * len(go)
        v = 0
        for c in t:
            while v and c not in go[v]:
                v = fail[v]
            v = go[v].get(c, 0)
            visits[v] += 1
        for u in reversed(bfs):
            visits[fail[u]] += visits[u]
        rows.append([visits[end] for end in order_end])
    return {"counts": rows}