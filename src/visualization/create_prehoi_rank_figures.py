"""Generate schematic figures for the PreHOI-Rank manuscript.

The figures are intentionally diagrammatic and do not use HOT3D images.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Rectangle


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FIGURE_DIR = PROJECT_ROOT / "paper" / "figures"

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    }
)

COLORS = {
    "ink": "#1f2933",
    "muted": "#64748b",
    "blue": "#2563eb",
    "blue_light": "#dbeafe",
    "green": "#059669",
    "green_light": "#d1fae5",
    "orange": "#ea580c",
    "orange_light": "#ffedd5",
    "red": "#dc2626",
    "red_light": "#fee2e2",
    "gray": "#e5e7eb",
    "gray_light": "#f8fafc",
    "purple": "#7c3aed",
    "purple_light": "#ede9fe",
}


def setup_canvas(width: float = 12, height: float = 7, title: str | None = None):
    fig, ax = plt.subplots(figsize=(width, height), dpi=220)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    if title:
        ax.text(50, 96, title, ha="center", va="top", fontsize=15, weight="bold", color=COLORS["ink"])
    return fig, ax


def rounded_box(
    ax,
    x: float,
    y: float,
    w: float,
    h: float,
    text: str,
    fc: str = "white",
    ec: str = "#334155",
    fontsize: int = 10,
    weight: str = "normal",
    radius: float = 0.08,
):
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle=f"round,pad=0.45,rounding_size={radius * min(w, h)}",
        linewidth=1.5,
        facecolor=fc,
        edgecolor=ec,
    )
    ax.add_patch(patch)
    ax.text(
        x + w / 2,
        y + h / 2,
        text,
        ha="center",
        va="center",
        fontsize=fontsize,
        color=COLORS["ink"],
        weight=weight,
        linespacing=1.15,
    )
    return patch


def arrow(ax, start, end, color: str = "#334155", lw: float = 1.8, style: str = "-|>", rad: float = 0.0):
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle=style,
            mutation_scale=14,
            linewidth=lw,
            color=color,
            connectionstyle=f"arc3,rad={rad}",
        )
    )


def save(fig, filename: str):
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    stem = Path(filename).stem
    png_path = FIGURE_DIR / f"{stem}.png"
    pdf_path = FIGURE_DIR / f"{stem}.pdf"
    fig.savefig(png_path, dpi=300, bbox_inches="tight", facecolor="white")
    fig.savefig(pdf_path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"saved {png_path.relative_to(PROJECT_ROOT)}")
    print(f"saved {pdf_path.relative_to(PROJECT_ROOT)}")


def draw_frame_strip(ax, x0: float, y: float, count: int, label_prefix: str, highlight_last: bool = False):
    for i in range(count):
        x = x0 + i * 5.2
        fc = COLORS["blue_light"] if i < count - 1 or not highlight_last else COLORS["green_light"]
        ec = COLORS["blue"] if i < count - 1 or not highlight_last else COLORS["green"]
        ax.add_patch(Rectangle((x, y), 4.2, 7, facecolor=fc, edgecolor=ec, linewidth=1.2))
        ax.text(x + 2.1, y + 3.5, f"{label_prefix}{i}", ha="center", va="center", fontsize=7, color=COLORS["ink"])


def figure_1_problem_overview():
    fig, ax = setup_canvas(title="PreHOI-Rank: pre-contact candidate ranking")

    ax.text(8, 84, "Observation window", fontsize=12, weight="bold", color=COLORS["ink"])
    draw_frame_strip(ax, 8, 72, 7, "t", highlight_last=True)
    ax.text(8, 66, "Model input: observation frames only", fontsize=9, color=COLORS["muted"])

    rounded_box(ax, 52, 70, 18, 12, "Visible object\ncandidates", COLORS["orange_light"], COLORS["orange"], 10, "bold")
    for cx, cy, label in [(55, 58, "obj A"), (62, 54, "obj B"), (69, 58, "obj C")]:
        ax.add_patch(Circle((cx, cy), 3.2, facecolor=COLORS["orange_light"], edgecolor=COLORS["orange"], linewidth=1.2))
        ax.text(cx, cy, label, ha="center", va="center", fontsize=8, color=COLORS["ink"])

    rounded_box(ax, 78, 70, 17, 12, "Ranked target\ncandidates", COLORS["green_light"], COLORS["green"], 10, "bold")
    ax.text(84, 58.5, "1. obj B\n2. obj C\n3. obj A", ha="center", va="center", fontsize=9, color=COLORS["ink"])

    rounded_box(ax, 73, 29, 22, 13, "Future target\nproxy + hand pose", COLORS["purple_light"], COLORS["purple"], 9, "bold")
    rounded_box(ax, 43, 29, 22, 13, "Forecast frame\n(target construction only)", COLORS["red_light"], COLORS["red"], 8, "bold")
    ax.text(54, 22, "Forecast-frame annotations define targets, never inputs", ha="center", fontsize=9, color=COLORS["red"], weight="bold")

    arrow(ax, (45, 75.5), (52, 76), COLORS["blue"])
    arrow(ax, (70, 76), (78, 76), COLORS["orange"])
    arrow(ax, (92, 70), (92, 42), COLORS["green"])
    arrow(ax, (65, 35.5), (73, 35.5), COLORS["red"], lw=1.4)

    rounded_box(ax, 8, 29, 27, 13, "Pre-contact task\nrank visible objects before contact", COLORS["gray_light"], COLORS["muted"], 10)
    arrow(ax, (35, 35.5), (43, 35.5), COLORS["muted"], lw=1.4)

    save(fig, "fig1_problem_overview.png")


def figure_2_proxy_label_generation():
    fig, ax = setup_canvas(title="Derived target-object proxy generation")

    rounded_box(ax, 7, 70, 24, 13, "Forecast frame\nannotations", COLORS["red_light"], COLORS["red"], 11, "bold")
    ax.text(19, 62, "Used only to define target", ha="center", fontsize=9, color=COLORS["red"], weight="bold")

    ax.add_patch(Rectangle((12, 34), 18, 18, facecolor=COLORS["blue_light"], edgecolor=COLORS["blue"], linewidth=1.8))
    ax.text(21, 43, "hand\nunion box", ha="center", va="center", fontsize=9, color=COLORS["ink"])
    object_boxes = [
        (42, 55, 14, 11, "obj A", 0.28),
        (42, 32, 15, 13, "obj B", 0.86),
        (61, 43, 14, 12, "obj C", 0.41),
    ]
    for x, y, w, h, label, score in object_boxes:
        ax.add_patch(Rectangle((x, y), w, h, facecolor=COLORS["orange_light"], edgecolor=COLORS["orange"], linewidth=1.5))
        ax.text(x + w / 2, y + h / 2, f"{label}\nscore {score:.2f}", ha="center", va="center", fontsize=8, color=COLORS["ink"])

    arrow(ax, (30, 43), (43, 39), COLORS["muted"])
    arrow(ax, (30, 47), (43, 58), COLORS["muted"])
    arrow(ax, (30, 45), (64, 48), COLORS["muted"])

    rounded_box(ax, 78, 64, 17, 11, "Proximity\nscore", COLORS["gray_light"], COLORS["muted"], 10, "bold")
    ax.text(86.5, 58, "IoU + center\nproximity", ha="center", va="center", fontsize=8, color=COLORS["muted"])
    rounded_box(ax, 78, 36, 17, 12, "Selected proxy\nobj B", COLORS["green_light"], COLORS["green"], 10, "bold")
    arrow(ax, (86.5, 64), (86.5, 48), COLORS["green"])

    ax.text(
        50,
        17,
        "Derived proxy label, not human ground truth. Forecast-frame boxes are never model input.",
        ha="center",
        fontsize=10,
        color=COLORS["red"],
        weight="bold",
    )

    save(fig, "fig2_proxy_label_generation.png")


def figure_3_architecture():
    fig, ax = setup_canvas(title="PreHOI-Rank candidate-ranking architecture")

    rounded_box(ax, 5, 68, 23, 13, "Observation\nmetadata [T, 9]", COLORS["blue_light"], COLORS["blue"], 10, "bold")
    rounded_box(ax, 5, 40, 23, 13, "Object candidates\n[K, feature_dim]", COLORS["orange_light"], COLORS["orange"], 10, "bold")
    rounded_box(ax, 5, 22, 23, 9, "Candidate mask [K]", COLORS["gray_light"], COLORS["muted"], 9)

    rounded_box(ax, 36, 68, 21, 13, "Temporal\nencoder", COLORS["blue_light"], COLORS["blue"], 10, "bold")
    rounded_box(ax, 36, 40, 21, 13, "Candidate\nencoder", COLORS["orange_light"], COLORS["orange"], 10, "bold")
    rounded_box(ax, 64, 54, 17, 13, "Fusion", "white", COLORS["ink"], 11, "bold")
    rounded_box(ax, 86, 68, 12, 13, "Score\nhead", COLORS["green_light"], COLORS["green"], 9, "bold")
    rounded_box(ax, 86, 38, 12, 13, "Pose\nhead", COLORS["purple_light"], COLORS["purple"], 9, "bold")

    arrow(ax, (28, 74.5), (36, 74.5), COLORS["blue"])
    arrow(ax, (28, 46.5), (36, 46.5), COLORS["orange"])
    arrow(ax, (28, 26.5), (36, 43.5), COLORS["muted"], lw=1.2)
    arrow(ax, (57, 74.5), (64, 62.5), COLORS["blue"])
    arrow(ax, (57, 46.5), (64, 58), COLORS["orange"])
    arrow(ax, (81, 61), (86, 74.5), COLORS["green"])
    arrow(ax, (81, 58), (86, 44.5), COLORS["purple"])

    ax.text(92, 61, "rank visible\ncandidates", ha="center", fontsize=8, color=COLORS["green"])
    ax.text(92, 31, "future MANO\npose vector", ha="center", fontsize=8, color=COLORS["purple"])
    ax.text(50, 12, "Current strongest model: non-VL candidate ranker; vision-language kept as ablation.", ha="center", fontsize=9, color=COLORS["muted"])

    save(fig, "fig3_prehoi_rank_architecture.png")


def figure_4_protocol_safety():
    fig, ax = setup_canvas(title="Leakage and candidate-order safety protocol")

    rounded_box(ax, 7, 68, 25, 13, "Allowed input\nobservation window only", COLORS["green_light"], COLORS["green"], 10, "bold")
    rounded_box(ax, 7, 39, 25, 13, "Disallowed input\nforecast-frame features", COLORS["red_light"], COLORS["red"], 10, "bold")
    rounded_box(ax, 40, 68, 24, 13, "Candidate order\nstable_uid", COLORS["blue_light"], COLORS["blue"], 10, "bold")
    rounded_box(ax, 40, 39, 24, 13, "Excluded order\nas_is / proxy-score", COLORS["red_light"], COLORS["red"], 10, "bold")
    rounded_box(ax, 72, 68, 21, 13, "Clip-level\nsplit", COLORS["green_light"], COLORS["green"], 10, "bold")
    rounded_box(ax, 72, 39, 21, 13, "Report position\nbaselines", COLORS["orange_light"], COLORS["orange"], 10, "bold")

    checks = [
        (12, 23, "input_uses_forecast_frame = false"),
        (43, 23, "candidate-0 / first-3 / random"),
        (73, 23, "derived proxy != ground truth"),
    ]
    for x, y, text in checks:
        ax.add_patch(Circle((x, y), 2.2, facecolor=COLORS["green_light"], edgecolor=COLORS["green"], linewidth=1.3))
        ax.text(x + 3.2, y, text, va="center", fontsize=8.5, color=COLORS["ink"])

    arrow(ax, (32, 74.5), (40, 74.5), COLORS["muted"])
    arrow(ax, (64, 74.5), (72, 74.5), COLORS["muted"])
    arrow(ax, (32, 45.5), (40, 45.5), COLORS["red"])
    arrow(ax, (64, 45.5), (72, 45.5), COLORS["orange"])

    ax.text(50, 11, "Runs violating these rules are excluded from paper claims.", ha="center", fontsize=10, color=COLORS["red"], weight="bold")

    save(fig, "fig4_protocol_safety.png")


def figure_5_results():
    fig, ax = plt.subplots(figsize=(11.2, 6.4), dpi=220)
    metrics = ["Top-1", "MRR", "Pose MAE\n(lower better)"]
    vals_25 = [0.5624, 0.7502, 0.4412]
    vals_50 = [0.7499, 0.8605, 0.4102]
    vals_75 = [0.7115, 0.8340, 0.4676]
    err_25 = [0.0693, 0.0312, 0.0042]
    err_50 = [0.0450, 0.0221, 0.0051]
    err_75 = [0.0571, 0.0343, 0.0096]
    x = range(len(metrics))
    width = 0.24

    series = [
        ("25 clips pilot", vals_25, err_25, -width, COLORS["gray"], COLORS["muted"]),
        ("50 clips primary", vals_50, err_50, 0.0, COLORS["green_light"], COLORS["green"]),
        ("75 clips robustness", vals_75, err_75, width, COLORS["orange_light"], COLORS["orange"]),
    ]
    for label, values, errors, offset, face, edge in series:
        positions = [i + offset for i in x]
        ax.bar(
            positions,
            values,
            width=width,
            yerr=errors,
            capsize=4,
            label=label,
            color=face,
            edgecolor=edge,
            linewidth=1.2,
        )
        for position, value, error in zip(positions, values, errors):
            ax.text(
                position,
                value + error + 0.018,
                f"{value:.3f}",
                ha="center",
                fontsize=8,
                color=COLORS["ink"],
            )

    ax.set_title("PreHOI-Rank candidate-ranker diagnostics", fontsize=15, weight="bold")
    ax.set_ylabel("Metric value")
    ax.set_xticks(list(x))
    ax.set_xticklabels(metrics)
    ax.set_ylim(0, 1.05)
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False, loc="upper left")
    ax.text(
        0.5,
        -0.16,
        "Mean +/- std over repeated seeds. 50 clips is primary; 75 clips is a harder robustness split.",
        ha="center",
        va="top",
        transform=ax.transAxes,
        fontsize=9,
        color=COLORS["muted"],
    )
    fig.tight_layout()
    save(fig, "fig5_25clip_vs_50clip_results.png")


def main() -> None:
    figure_1_problem_overview()
    figure_2_proxy_label_generation()
    figure_3_architecture()
    figure_4_protocol_safety()
    figure_5_results()


if __name__ == "__main__":
    main()
