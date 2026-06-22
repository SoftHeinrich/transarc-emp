"""JabRef doc-to-code per-component F1: TransArc vs Artemis vs AAlinker (s20 union).

Whole gold-component list (no truncation), three systems side by side, ordered by
component size (share of gold link pairs). AAlinker is s_linker20_union on the GPT
backend, per-component F1 averaged over the available runs. Saved to a separate
analysis folder (transarc-emp/reports/figures), not the paper figure dir.
"""
import os
os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")
import sys
from pathlib import Path
from collections import defaultdict
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ARDOCO_HOME = Path(os.environ.get("ARDOCO_HOME", Path(__file__).resolve().parents[3]))
sys.path.insert(0, str(ARDOCO_HOME / "transarc-emp" / "src" / "bias"))
import component_suite as cs  # noqa: E402
from component_suite import (  # noqa: E402
    _code_inputs, SYSTEMS, calc_metrics, _read_pairs, _compose_sad_code,
    load_result_sam_code_standalone, load_code_model_files, load_model_element_names,
    enroll_gold_standard, load_gs_sam_code_raw, load_gs_sad_code_enrolled,
)

OUT = ARDOCO_HOME / "transarc-emp" / "reports" / "figures"
OUT.mkdir(parents=True, exist_ok=True)
S20 = ARDOCO_HOME / "llm-sad-sam-v45" / "results" / "v2.6.5_s20union_gpt_re_medium"
RUNS = [d.name for d in sorted(S20.iterdir()) if d.name.startswith("run")
        and (d / "jabref" / "s_linker20_union_jabref_links.csv").exists()]
KIT_GREEN, KIT_RED, KIT_BLUE = "#009682", "#A22223", "#4664AA"
PROJ = "jabref"


def short(c):
    return c.replace("Component: ", "").replace("Interface: ", "")


def s20_code(p, run):
    sadsam = _read_pairs(S20 / run / p / f"s_linker20_union_{p}_links.csv",
                         a_keys=("component_id", "modelElementID"), b_keys=("sentence",))
    return _compose_sad_code(sadsam, load_result_sam_code_standalone(p))


gold, collapse = _code_inputs(PROJ)
loaders = {k: cl for k, _, _, cl in SYSTEMS}
goldc = defaultdict(set)
for s, c in gold:
    goldc[c].add(s)


def percomp(res):
    r = defaultdict(set)
    for s, c in collapse(res):
        r[c].add(s)
    return {c: calc_metrics({(s, c) for s in goldc[c]},
                            {(s, c) for s in r.get(c, set())})[2] for c in goldc}


T = percomp(loaders["swattr_transarc"](PROJ))
A = percomp(loaders["artemis"](PROJ))
# AAlinker: mean per-component F1 over runs
runs = [percomp(s20_code(PROJ, run)) for run in RUNS]
S = {c: sum(rp[c] for rp in runs) / len(runs) for c in goldc}

# component size (share of gold link pairs) -> order largest first
code_model = load_code_model_files(PROJ)
names = load_model_element_names(PROJ)
file_to_comps = defaultdict(set)
for ae, fp in enroll_gold_standard(load_gs_sam_code_raw(PROJ), code_model):
    file_to_comps[fp].add(names.get(ae, ae))
size = defaultdict(int)
for s, f in load_gs_sad_code_enrolled(PROJ, code_model):
    for c in file_to_comps.get(f, ()):
        size[c] += 1
total = sum(size.values())
comps = sorted(goldc, key=lambda c: -size.get(c, 0))

x = range(len(comps))
w = 0.27
fig, ax = plt.subplots(figsize=(5.6, 3.0))
ax.bar([i - w for i in x], [T[c] for c in comps], w, color=KIT_GREEN, label="TransArc")
ax.bar([i for i in x], [A[c] for c in comps], w, color=KIT_RED, label="Artemis")
ax.bar([i + w for i in x], [S[c] for c in comps], w, color=KIT_BLUE, label="AAlinker")
ax.set_ylim(0, 1.08)
ax.set_yticks([0, 0.5, 1.0])
ax.set_ylabel("per-component F1", fontsize=9)
ax.set_xticks(list(x))
def pctlbl(c):
    pc = 100 * size.get(c, 0) / total
    return f"{short(c)}\n({pc:.1f}%)" if pc >= 0.1 else f"{short(c)}\n({pc:.2f}%)"


ax.set_xticklabels([pctlbl(c) for c in comps], fontsize=7.5)
ax.set_xlabel("gold components (with % of gold link pairs), largest first", fontsize=8.5)
ax.grid(axis="y", ls=":", alpha=0.5)
ax.legend(fontsize=8, ncol=3, loc="lower center", frameon=False)
ax.set_title(f"JabRef doc-to-code: per-component F1 across all {len(comps)} components "
             f"(AAlinker = s20 union, mean of {len(RUNS)} run{'s' if len(RUNS) != 1 else ''})",
             fontsize=8.5)
fig.tight_layout()
p = OUT / "jabref_3sys_percomp.png"
fig.savefig(p, dpi=150, bbox_inches="tight")
fig.savefig(p.with_suffix(".pdf"), bbox_inches="tight")
print("wrote", p)
for c in comps:
    print(f"  {short(c):12} T={T[c]:.2f} A={A[c]:.2f} AAlinker={S[c]:.2f}")
