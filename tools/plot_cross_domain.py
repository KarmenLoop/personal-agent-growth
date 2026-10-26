"""Plot retained complete-task measurements; no inferred cost or missing-value fill."""
import argparse
import hashlib
import json
import statistics
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("data", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    data = json.loads(args.data.read_text())
    def output_path(suffix):
        return args.output.parent / (args.output.name + "." + suffix)
    arms = ["baseline", "general", "domain", "composed"]
    samples = data["samples"]
    assert len(samples) == 24
    colors = ["#333333", "#0072B2", "#D55E00", "#007A59"]
    markers = ["o", "s", "^"]
    offsets = [-0.09, 0, 0.09]
    with plt.rc_context({"font.size": 11, "axes.titlesize": 13,
                         "svg.fonttype": "path", "figure.facecolor": "white",
                         "axes.spines.top": False, "axes.spines.right": False}):
        fig, axes = plt.subplots(2, 2, figsize=(12, 8), layout="constrained")
        fig.suptitle("Complete-task resource measurements", fontsize=18)
        for col, task in enumerate(["release", "climate"]):
            axes[0, col].set_title("Software release acceptance" if task == "release"
                                   else "NASA annual-data analysis")
            for row, metric in enumerate(["total_tokens", "elapsed_utc_seconds"]):
                ax = axes[row, col]
                scale = 1000 if row == 0 else 1
                for pos, arm in enumerate(arms):
                    group = sorted((s for s in samples if s["arm"] == arm and s["task"] == task),
                                   key=lambda s: s["rep"])
                    assert [s["rep"] for s in group] == [1, 2, 3]
                    values = [s[metric] / scale for s in group]
                    valid = row == 0 or all(s["time_sample_valid"] for s in group)
                    for n, (s, value) in enumerate(zip(group, values)):
                        x = pos + offsets[n]
                        anomaly = row == 1 and not s["time_sample_valid"]
                        ax.scatter(x, value, marker=markers[n], s=65,
                                   facecolor="white" if anomaly else colors[pos],
                                   edgecolor=colors[pos], linewidth=1.5, zorder=3)
                        if anomaly:
                            mono = s["elapsed_monotonic_seconds"]
                            ax.plot([x, x], [mono, value], color=colors[pos],
                                    linestyle=":", linewidth=1.2)
                            ax.scatter(x, mono, marker="x", color=colors[pos], s=65)
                            ax.annotate(f"UTC {value:.0f}s / monotonic {mono:.0f}s\nTiming guard unknown",
                                        xy=(x, value), xytext=(10, -8),
                                        textcoords="offset points", fontsize=9, va="top")
                    if valid:
                        median = statistics.median(values)
                        ax.plot([pos-.22, pos+.22], [median, median], color="black", linewidth=2.3)
                ax.set_xticks(range(4), ["Baseline", "General", "Domain", "Composed"])
                ax.set_xlim(-0.5, 3.6)
                ax.set_ylabel("Total tokens (thousands)" if row == 0 else "Elapsed time (seconds)")
                ax.grid(axis="y", alpha=0.2)
                ax.set_axisbelow(True)
        for row, metric in enumerate(["total_tokens", "elapsed_utc_seconds"]):
            maximum = max(s[metric] for s in samples) / (1000 if row == 0 else 1)
            for ax in axes[row]:
                ax.set_ylim(0, maximum * 1.15)
        handles = [Line2D([], [], marker=marker, linestyle="", color="black", label=f"Repeat {n+1}")
                   for n, marker in enumerate(markers)]
        handles.append(Line2D([], [], color="black", linewidth=2.3, label="Median (3 valid measurements)"))
        fig.legend(handles=handles, loc="outside lower center", ncol=4, frameon=False)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        for suffix in ["png", "svg"]:
            fig.savefig(output_path(suffix), dpi=180, facecolor="white")
        plt.close(fig)
    manifest = {
        "source_sha256": hashlib.sha256(args.data.read_bytes()).hexdigest(),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "matplotlib": matplotlib.__version__,
        "medium": "GitHub documentation, general web figure; no journal specification",
        "transformations": ["token counts divided by 1000 for display", "raw repetitions shown with fixed category offsets",
                            "median only when all three timing measurements are valid", "common zero-based axes for comparable panels"],
        "uncertainty": "No confidence intervals or significance claim; three complete task repetitions per arm and domain",
        "missing": "Conflicting UTC and monotonic time shown explicitly; no guard median for the affected group",
        "outputs": {suffix: hashlib.sha256(output_path(suffix).read_bytes()).hexdigest()
                    for suffix in ["png", "svg"]},
    }
    output_path("provenance.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
