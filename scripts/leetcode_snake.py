#!/usr/bin/env python3
"""Builds assets/leetcode-snake.svg: a snake that lights up one cell per solved LeetCode problem.

Usage:
  python scripts/leetcode_snake.py --repo ../leetcodes          # read problem folders from a clone
  python scripts/leetcode_snake.py                              # use the built-in list below
"""
import argparse, os, re

FALLBACK = [5,11,26,88,101,104,151,199,206,236,238,268,283,328,334,345,392,394,437,443,448,547,605,643,649,700,724,735,841,872,933,1004,1071,1161,1207,1372,1431,1448,1456,1464,1493,1657,1679,1732,1768,1846,1926,1967,2095,2130,2215,2352,2390,3020,3620,3700,3737,3739]

COLS, PITCH, CELL = 20, 38, 30
X0, Y0 = 35, 84
LEN = 7            # snake length in cells
DT = 0.16          # seconds per step
HOLD = 2.5         # seconds to show the finished board
DIM, LIT, FLASH = "#171b30", "#ffa116", "#ffe2b0"   # LeetCode orange
TXT_DIM, TXT_LIT = "#3b4170", "#2b1700"

def read_problems(repo):
    if not repo:
        return FALLBACK
    nums = sorted(int(m.group(1)) for d in os.listdir(repo)
                  if os.path.isdir(os.path.join(repo, d)) and (m := re.match(r"(\d{4})-", d)))
    return nums or FALLBACK

def build(problems):
    n = len(problems)
    rows = -(-n // COLS)
    grid = []                              # visiting order of (col,row)
    for r in range(rows):
        cols = range(COLS) if r % 2 == 0 else range(COLS - 1, -1, -1)
        grid += [(c, r) for c in cols][: max(0, min(COLS, n - r * COLS))]
    first, last = grid[0], grid[-1]
    dx_in = 1 if first[0] == 0 else -1
    dx_out = 1 if last[0] > COLS // 2 else -1
    entry = [(first[0] - dx_in * k, first[1]) for k in range(LEN + 1, 0, -1)]
    exit_ = [(last[0] + dx_out * k, last[1]) for k in range(1, LEN + 2)]
    path = entry + grid + exit_
    off = len(entry)                       # index of grid[0] inside path
    steps = len(path) + LEN
    run = steps * DT
    D = run + HOLD
    px = lambda c: X0 + c * PITCH
    py = lambda r: Y0 + r * PITCH
    H = Y0 + rows * PITCH + 52

    def kt(vals):
        return ";".join(f"{v:.4f}" for v in vals)

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 830 {H}" width="830" height="{H}" role="img" aria-label="Snake lighting up {n} solved LeetCode problems">',
           f'<rect width="830" height="{H}" rx="14" fill="#090b16"/><rect x=".5" y=".5" width="829" height="{H-1}" rx="14" fill="none" stroke="#242a4d"/>',
           '<g font-family="\'Segoe UI\',\'Helvetica Neue\',Arial,sans-serif">',
           f'<text x="35" y="44" font-size="22" font-weight="700" fill="#eef0ff">LeetCode</text>',
           f'<text x="150" y="44" font-size="16" fill="#ffa116">{n} problems solved</text>',
           '<text x="795" y="44" font-size="13" fill="#6f78b4" text-anchor="end">arrays · strings · trees · graphs · sliding window</text>',
           f'<text x="35" y="{H-20}" font-size="12" fill="#4d5488">One cell per problem folder in srikanth97318/leetcodes</text></g>']

    # cells
    reset = (run + 0.1) / D
    for i, ((c, r), num) in enumerate(zip(grid, problems)):
        a = (off + i) * DT / D
        times = [0, a, a + 0.25 * DT / D, a + 0.9 * DT / D, 0.985, 1]
        fills = [DIM, DIM, FLASH, LIT, LIT, DIM]
        tfill = [TXT_DIM, TXT_DIM, TXT_LIT, TXT_LIT, TXT_LIT, TXT_DIM]
        out.append(f'<rect x="{px(c)}" y="{py(r)}" width="{CELL}" height="{CELL}" rx="7" fill="{DIM}">'
                   f'<animate attributeName="fill" values="{";".join(fills)}" keyTimes="{kt(times)}" dur="{D:.2f}s" repeatCount="indefinite"/></rect>')
        out.append(f'<text x="{px(c)+CELL/2}" y="{py(r)+CELL/2+3.5}" font-size="10" font-weight="600" text-anchor="middle" '
                   f'font-family="\'Segoe UI\',Arial,sans-serif" fill="{TXT_DIM}">{num}'
                   f'<animate attributeName="fill" values="{";".join(tfill)}" keyTimes="{kt(times)}" dur="{D:.2f}s" repeatCount="indefinite"/></text>')

    # snake: tail drawn first so the head sits on top
    for j in range(LEN - 1, -1, -1):
        size = CELL - 7 if j else CELL
        pad = (CELL - size) / 2
        pts = []
        for t in range(steps + 1):
            c, r = path[min(max(t - j, 0), len(path) - 1)]
            pts.append((px(c) + pad, py(r) + pad))
        keys = [t * DT / D for t in range(steps + 1)]
        pts.append(pts[-1]); keys.append(1.0)
        op = 1.0 if j == 0 else max(0.25, 0.85 - j * 0.1)
        fill = "#ffffff" if j == 0 else "#d9dcff"
        glow = ' style="filter:drop-shadow(0 0 6px #aab2ff)"' if j == 0 else ""
        out.append(f'<rect width="{size}" height="{size}" rx="{9 if j==0 else 8}" fill="{fill}" opacity="{op:.2f}"{glow}>'
                   f'<animateTransform attributeName="transform" type="translate" values="{";".join(f"{x:.0f} {y:.0f}" for x,y in pts)}" '
                   f'keyTimes="{kt(keys)}" dur="{D:.2f}s" repeatCount="indefinite"/></rect>')
    out.append("</svg>")
    return "\n".join(out)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", help="path to a clone of the leetcodes repo")
    ap.add_argument("--out", default="assets/leetcode-snake.svg")
    a = ap.parse_args()
    probs = read_problems(a.repo)
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    open(a.out, "w").write(build(probs))
    print(f"wrote {a.out} with {len(probs)} problems")
