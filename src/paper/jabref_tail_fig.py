"""Per-component F1 tail curves (doc-to-model): TransArc vs Artemis, all projects.

Renders one tail-profile figure per project (components sorted worst->best) plus
a 5-panel grid, to compare which project is the most convincing teaser for the
"standard micro F1 hides a tail failure" claim. Values pulled live from
component_suite.py so the figures cannot drift from the metric source.
"""
import os
os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")
import sys
from pathlib import Path
from collections import defaultdict
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Portable roots: default to the ardoco-home workspace (repo's parent), override
# via ARDOCO_HOME. Figure output dir overridable via TAIL_FIG_OUT.
ARDOCO_HOME = Path(os.environ.get("ARDOCO_HOME", Path(__file__).resolve().parents[3]))
sys.path.insert(0, str(ARDOCO_HOME / "transarc-emp" / "src" / "bias"))
from component_suite import _model_inputs, SYSTEMS, calc_metrics  # noqa: E402

OUT = os.environ.get("TAIL_FIG_OUT", str(ARDOCO_HOME / "alinker-paper" / "figures"))
PROJECTS = ["mediastore", "teastore", "teammates", "bigbluebutton", "jabref"]
KIT_GREEN = "#009682"
KIT_RED = "#A22223"


def short(name):
    n = name.replace("Component: ", "").replace("Interface: ", "")
    if n.startswith("_"):  # unnamed model-element UUID
        return "uuid"
    return n


def project_data(proj):
    gold, collapse = _model_inputs(proj)
    loaders = {k: ml for k, _, ml, _ in SYSTEMS}
    out, micro = {}, {}
    for sysk in ["swattr_transarc", "artemis"]:
        g, r = defaultdict(set), defaultdict(set)
        res = collapse(loaders[sysk](proj))
        for s, c in gold:
            g[c].add(s)
        for s, c in res:
            r[c].add(s)
        micro[sysk] = calc_metrics(set(gold), set(res))[2]
        out[sysk] = {c: calc_metrics({(s, c) for s in g[c]},
                                     {(s, c) for s in r.get(c, set())})[2] for c in g}
    comps = sorted(out["swattr_transarc"],
                   key=lambda c: (min(out["swattr_transarc"][c], out["artemis"][c]),
                                  out["swattr_transarc"][c]))
    return comps, out, micro


def draw(ax, proj):
    comps, out, micro = project_data(proj)
    x = list(range(len(comps)))
    tr = [out["swattr_transarc"][c] for c in comps]
    ar = [out["artemis"][c] for c in comps]
    ax.plot(x, tr, "-o", color=KIT_GREEN, lw=2, ms=5, label="TransArc")
    ax.plot(x, ar, "-s", color=KIT_RED, lw=2, ms=5, label="Artemis")
    ax.set_xticks(x)
    ax.set_xticklabels([short(c) for c in comps], rotation=35, ha="right", fontsize=7)
    ax.set_ylim(-0.05, 1.10)
    ax.set_yticks([0, 0.5, 1.0])
    ax.tick_params(labelsize=7)
    ax.grid(axis="y", ls=":", alpha=0.5)
    ax.set_title(f"{proj}: micro T={micro['swattr_transarc']:.2f} "
                 f"A={micro['artemis']:.2f}", fontsize=8.5)
    return micro


# individual figures
for proj in PROJECTS:
    fig, ax = plt.subplots(figsize=(4.4, 2.6))
    draw(ax, proj)
    ax.set_ylabel("per-component F1", fontsize=9)
    ax.legend(fontsize=8, loc="lower right", frameon=False)
    fig.tight_layout()
    p = f"{OUT}/tail_{proj}.png"
    fig.savefig(p, dpi=150, bbox_inches="tight")
    fig.savefig(p.replace(".png", ".pdf"), bbox_inches="tight")
    plt.close(fig)
    print("wrote", p)

# comparison grid
fig, axes = plt.subplots(2, 3, figsize=(11, 5.2))
for ax, proj in zip(axes.flat, PROJECTS):
    draw(ax, proj)
axes.flat[0].set_ylabel("per-component F1", fontsize=9)
axes.flat[3].set_ylabel("per-component F1", fontsize=9)
axes.flat[5].axis("off")
axes.flat[0].legend(fontsize=8, loc="lower right", frameon=False)
fig.suptitle("doc-to-model per-component F1 tail (worst$\\rightarrow$best)", fontsize=11)
fig.tight_layout()
fig.savefig(f"{OUT}/tail_grid.png", dpi=150, bbox_inches="tight")
print("wrote", f"{OUT}/tail_grid.png")
