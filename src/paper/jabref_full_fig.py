"""JabRef FULL per-component F1 distribution (not just the worst tail).

JabRef has no false-positive components, so the gold-component set is the entire
universe: this figure shows every component for both tasks, plus the per-sentence
distribution, so nothing is hidden behind a tail summary. Values live from
component_suite.py.
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
from component_suite import _model_inputs, _code_inputs, SYSTEMS, calc_metrics  # noqa: E402

OUT = os.environ.get("TAIL_FIG_OUT", str(ARDOCO_HOME / "alinker-paper" / "figures"))
KIT_GREEN, KIT_RED = "#009682", "#A22223"
SYS = ["swattr_transarc", "artemis"]
LBL = {"swattr_transarc": "TransArc", "artemis": "Artemis"}


def short(n):
    n = n.replace("Component: ", "").replace("Interface: ", "")
    return "uuid" if n.startswith("_") else n


def per_component(inp, idx):
    gold, collapse = inp("jabref")
    loaders = {k: (m, c) for k, _, m, c in SYSTEMS}
    res = {}
    for sysk in SYS:
        r = defaultdict(set)
        g = defaultdict(set)
        for s, c in gold:
            g[c].add(s)
        for s, c in collapse(loaders[sysk][idx]("jabref")):
            r[c].add(s)
        res[sysk] = {c: calc_metrics({(s, c) for s in g[c]},
                                     {(s, c) for s in r.get(c, set())})[2] for c in g}
    return res


def per_sentence(inp, idx):
    gold, collapse = inp("jabref")
    loaders = {k: (m, c) for k, _, m, c in SYSTEMS}
    gs = defaultdict(set)
    for s, c in gold:
        gs[s].add(c)
    out = {}
    for sysk in SYS:
        rs = defaultdict(set)
        for s, c in collapse(loaders[sysk][idx]("jabref")):
            rs[s].add(c)
        out[sysk] = sorted(calc_metrics({(s, c) for c in gs[s]},
                                        {(s, c) for c in rs.get(s, set())})[2] for s in gs)
    return out


fig, axes = plt.subplots(1, 3, figsize=(11, 3.0))

# Panels 1-2: full per-component for both tasks (all components, labeled)
for ax, (title, inp, idx) in zip(axes[:2], [
        ("doc-to-model (all 5 components)", _model_inputs, 0),
        ("doc-to-code (all 6 components)", _code_inputs, 1)]):
    res = per_component(inp, idx)
    comps = sorted(res["swattr_transarc"],
                   key=lambda c: (min(res["swattr_transarc"][c], res["artemis"][c]),
                                  res["swattr_transarc"][c]))
    x = range(len(comps))
    ax.plot(x, [res["swattr_transarc"][c] for c in comps], "-o", color=KIT_GREEN, lw=2, ms=6, label="TransArc")
    ax.plot(x, [res["artemis"][c] for c in comps], "-s", color=KIT_RED, lw=2, ms=6, label="Artemis")
    ax.set_xticks(list(x))
    ax.set_xticklabels([short(c) for c in comps], rotation=30, ha="right", fontsize=7.5)
    ax.set_ylim(-0.05, 1.10)
    ax.set_yticks([0, 0.5, 1.0])
    ax.set_title(title, fontsize=9)
    ax.grid(axis="y", ls=":", alpha=0.5)
axes[0].set_ylabel("per-component F1", fontsize=9)
axes[0].legend(fontsize=8, loc="lower right", frameon=False)

# Panel 3: full per-sentence distribution (ECDF), doc-to-code
ps = per_sentence(_code_inputs, 1)
ax = axes[2]
for sysk, col in [("swattr_transarc", KIT_GREEN), ("artemis", KIT_RED)]:
    v = ps[sysk]
    n = len(v)
    ax.step([0] + v, [i / n for i in range(n + 1)], where="post", color=col, lw=2, label=LBL[sysk])
ax.set_xlabel("per-sentence F1", fontsize=9)
ax.set_ylabel("cumulative fraction of sentences", fontsize=8.5)
ax.set_title("doc-to-code (all 10 sentences)", fontsize=9)
ax.set_xlim(-0.03, 1.03)
ax.set_ylim(0, 1.02)
ax.grid(ls=":", alpha=0.5)
ax.legend(fontsize=8, loc="upper left", frameon=False)

fig.suptitle("JabRef: full per-component and per-sentence F1 distribution "
             "(no components hidden; 0 false-positive components)", fontsize=10)
fig.tight_layout()
p = f"{OUT}/jabref_full_dist.png"
fig.savefig(p, dpi=150, bbox_inches="tight")
fig.savefig(p.replace(".png", ".pdf"), bbox_inches="tight")
print("wrote", p)
