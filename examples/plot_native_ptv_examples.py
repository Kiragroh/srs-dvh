"""Plot two matched PTVs from actual native TPS DVH exports of a synthetic plan.

No numerical DVH reconstruction, curve smoothing or rebinning is performed.
Repeated dose coordinates are retained. The inset enlarges coverage at 90–100%.
"""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

HERE = Path(__file__).resolve().parent
STYLES = [
    ('ElementsOriginal', '#354550', '--', 'Elements 4.5 (Brainlab)\nOriginal structures and native dose'),
    ('RayStationStandard', '#dc7818', '-', 'RayStation 2024B (RaySearch)\nElements 4.5 Export → import'),
    ('EclipseHDSSHigh', '#8a4baf', '-', 'Eclipse 18 (Varian)\nDirect HDSS → High import'),
]


def plot(data, output):
    plt.rcParams.update({'font.size': 11, 'axes.spines.top': False, 'axes.spines.right': False})
    fig, axes = plt.subplots(1, 2, figsize=(12.8, 6.1), sharex=True, sharey=True)
    for ax, example in zip(axes, data['examples']):
        zoom = ax.inset_axes([.07, .105, .43, .33])
        for key, color, style, label in STYLES:
            r = example['curves'][key]
            for target_ax in [ax, zoom]:
                target_ax.plot(r['dose_Gy'], r['volume_pct'], color=color, ls=style,
                               lw=2.3 if key=='ElementsOriginal' else 1.8)
        ax.set(xlim=(15, 28), ylim=(0, 102), xlabel='Dose [Gy]', ylabel='PTV volume [%]')
        ax.grid(alpha=.16)
        ax.axvline(20, color='#9ba6ae', lw=.8, ls=':', zorder=0)
        ax.set_title(f"{example['target']} · {example['source_displayed_volume_mm3']:g} mm³\nEquivalent diameter ≈ {example['equivalent_diameter_mm']:.2f} mm", fontsize=13, pad=10)
        zoom.set(xlim=(18, 21.7), ylim=(90, 100.4), xticks=[18, 20], yticks=[90, 98, 100])
        zoom.tick_params(labelsize=8)
        zoom.set_title('Coverage detail: 90–100%', fontsize=9)
        zoom.grid(alpha=.12)
        zoom.axhline(98, color='#7e8b94', ls=':', lw=.8, zorder=0)
        for key, color, style, label in STYLES:
            m = example['metrics'][key]
            zoom.scatter(m['D98_from_export_Gy'], 98, color=color, s=22, zorder=8)
        gap_rs = example['metrics']['RayStationStandard']['delta_D98_from_export_Gy']
        gap_ec = example['metrics']['EclipseHDSSHigh']['delta_D98_from_export_Gy']
        ax.text(.5, -.22, f"ΔD98 vs original: RayStation {gap_rs:+.2f} Gy · Eclipse {gap_ec:+.2f} Gy",
                transform=ax.transAxes, ha='center', fontsize=10)
    fig.suptitle('One original plan — two PTVs as displayed by the TPSs', fontsize=17, y=.985)
    handles = [Line2D([], [], color=c, ls=s, lw=2.2, label=l) for _, c, s, l in STYLES]
    fig.legend(handles=handles, loc='lower center', bbox_to_anchor=(.5, .025), ncol=3, frameon=False, fontsize=10)
    fig.text(.5, .005, 'Native exported points, unsmoothed. Source volumes are rounded TPS values; D98 is read from the curves.', ha='center', fontsize=9)
    fig.subplots_adjust(left=.065, right=.985, top=.82, bottom=.28, wspace=.20)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=175, facecolor='white')
    plt.close(fig)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input', type=Path, default=HERE/'data/native_ptv_examples.json')
    p.add_argument('--output', type=Path, default=HERE.parent/'docs/native_ptv_examples.png')
    args = p.parse_args()
    plot(json.loads(args.input.read_text(encoding='utf-8')), args.output)
    print(args.output)
