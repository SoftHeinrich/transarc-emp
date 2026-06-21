#!/usr/bin/env python3
"""Equivalence check: mini-src/metrics.py vs the canonical src/lib/metrics_api.py.

For every project and both tasks, score the same bundled result set with both
implementations and assert the primary-panel columns agree to 1e-9. The minimal
reimplementation is only trustworthy if it is a faithful *reduction* of the
canonical suite — this proves it.

    python3 mini-src/check.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))                       # mini-src
sys.path.insert(0, str(HERE.parent / "src" / "lib"))  # canonical metrics_api

import metrics as mini            # noqa: E402  (mini-src/metrics.py)
import metrics_api as canon       # noqa: E402  (src/lib/metrics_api.py)

# primary-panel keys (identical names in both implementations)
PANEL = {
    "sad-code": ["file_f1", "component_f1", "sentence_coverage", "noise_rate"],
    "sad-sam":  ["link_f1", "sentence_coverage", "noise_rate"],
}
COMPUTE = {
    "sad-code": (mini.compute_sad_code, canon.compute_sad_code_metrics),
    "sad-sam":  (mini.compute_sad_sam, canon.compute_sad_sam_metrics),
}

TOL = 1e-9
failures = 0
for task in ("sad-code", "sad-sam"):
    mini._TASK = task
    mini_fn, canon_fn = COMPUTE[task]
    for proj in mini.PROJECTS:
        path = mini.result_path(proj, None, None)
        res = mini.load_result(path, task)
        if not res:
            print(f"SKIP  {task:8} {proj:14} (no results at {path})")
            continue
        m, c = mini_fn(proj, res), canon_fn(proj, res)
        for key in PANEL[task]:
            mv, cv = m[key], c[key]
            ok = isinstance(cv, (int, float)) and abs(mv - cv) <= TOL
            if not ok:
                failures += 1
                print(f"FAIL  {task:8} {proj:14} {key:18} mini={mv} canon={cv}")
        print(f"OK    {task:8} {proj:14} "
              + "  ".join(f"{k}={m[k]:.4f}" for k in PANEL[task]))

print()
if failures:
    print(f"FAILED: {failures} mismatch(es)")
    sys.exit(1)
print("PASS: mini-src/metrics.py matches metrics_api on every panel cell.")
