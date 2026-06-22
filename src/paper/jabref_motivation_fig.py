"""Motivation figure (JabRef doc-to-code): per-component F1 vs component size.

Two stacked, x-aligned panels over JabRef's gold components, ordered largest to
smallest by share of gold link pairs:
  top    -- component size (% of all gold sentence-file pairs), log scale
  bottom -- per-component F1 for TransArc and Artemis
The alignment makes the thesis visual: Artemis matches/beats TransArc on the three
large components that own 99.3% of the links (so its file-level F1 is near perfect),
yet drops the tiny `preferences` component (0.4% of links) to zero -- a failure the
volume-weighted ruler cannot see. Values pulled live from component_suite.py.
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
from component_suite import (  # noqa: E402
    _code_inputs, SYSTEMS, calc_metrics,
    load_code_model_files, load_model_element_names, enroll_gold_standard,
    load_gs_sam_code_raw, load_gs_sad_code_enrolled,
)
OUT = os.environ.get("TAIL_FIG_OUT", str(ARDOCO_HOME / "alinker-paper" / "figures"))
KIT_GREEN, KIT_RED, GREY = "#009682", "#A22223", "#9aa0a6"
PROJ = "jabref"


def short(c):
    return c.replace("Component: ", "").replace("Interface: ", "")


# component size = number of enrolled (sentence, file) gold link pairs
code_model = load_code_model_files(PROJ)
names = load_model_element_names(PROJ)
file_to_comps = defaultdict(set)
for ae, fp in enroll_gold_standard(load_gs_sam_code_raw(PROJ), code_model):
    file_to_comps[fp].add(names.get(ae, ae))
size = defaultdict(int)
for s, f in load_gs_sad_code_enrolled(PROJ, code_model):
    for c in file_to_comps.get(f, ()):
        size[c] += 1

gold, collapse = _code_inputs(PROJ)
loaders = {k: cl for k, _, _, cl in SYSTEMS}
f1 = {}
for sysk in ["swattr_transarc", "artemis"]:
    g, r = defaultdict(set), defaultdict(set)
    for s, c in gold:
        g[c].add(s)
    for s, c in collapse(loaders[sysk](PROJ)):
        r[c].add(s)
    f1[sysk] = {c: calc_metrics({(s, c) for s in g[c]},
                                {(s, c) for s in r.get(c, set())})[2] for c in g}

total = sum(size.values())
comps = sorted(size, key=lambda c: -size[c])
x = range(len(comps))
pct = [100 * size[c] / total for c in comps]

drop = comps.index("Component: preferences") if "Component: preferences" in comps else None


def render(logscale, suffix):
    fig, (axt, axb) = plt.subplots(2, 1, figsize=(4.6, 3.8), sharex=True,
                                   gridspec_kw={"height_ratios": [1, 1.6]})

    # top: size bars (log or linear)
    axt.bar(x, pct, color=GREY, width=0.6)
    if logscale:
        axt.set_yscale("log")
        axt.set_ylim(0.01, 200)
        offy = lambda p: p * 1.5
    else:
        axt.set_ylim(0, 55)
        offy = lambda p: p + 1.5
    axt.set_ylabel("% of gold\nlink pairs", fontsize=8)
    axt.tick_params(labelsize=7)
    for xi, p in zip(x, pct):
        axt.text(xi, offy(p), (f"{p:.1f}" if p >= 0.1 else f"{p:.2f}"), ha="center",
                 fontsize=6.5, color="#444")
    axt.set_title("JabRef doc-to-code: large components own the links;\n"
                  "the dropped component is tiny", fontsize=8.5)

    # bottom: per-component F1
    axb.plot(x, [f1["swattr_transarc"][c] for c in comps], "-o", color=KIT_GREEN,
             lw=2, ms=6, label="TransArc")
    axb.plot(x, [f1["artemis"][c] for c in comps], "-s", color=KIT_RED,
             lw=2, ms=6, label="Artemis")
    axb.set_ylim(-0.05, 1.10)
    axb.set_yticks([0, 0.5, 1.0])
    axb.set_ylabel("per-component F1", fontsize=8.5)
    axb.set_xticks(list(x))
    axb.set_xticklabels([short(c) for c in comps], rotation=25, ha="right", fontsize=7.5)
    axb.grid(axis="y", ls=":", alpha=0.5)
    axb.legend(fontsize=8, loc="lower left", frameon=False)

    # highlight the dropped component across both panels
    if drop is not None:
        for ax in (axt, axb):
            ax.axvspan(drop - 0.45, drop + 0.45, color=KIT_RED, alpha=0.07, zorder=0)
        axb.annotate("entire component\nmissed (0.4% of links)", xy=(drop, 0.0),
                     xytext=(drop - 1.7, 0.33), fontsize=7, color=KIT_RED,
                     arrowprops=dict(arrowstyle="->", color=KIT_RED, lw=1))

    fig.tight_layout()
    p = f"{OUT}/jabref_motivation{suffix}.png"
    fig.savefig(p, dpi=150, bbox_inches="tight")
    fig.savefig(p.replace(".png", ".pdf"), bbox_inches="tight")
    print("wrote", p)
    plt.close(fig)


render(logscale=True, suffix="_log")
render(logscale=False, suffix="_linear")
