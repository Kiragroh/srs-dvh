"""Show the volume-sampling error with an identical, known continuous dose.

The input is a subset of analytical_benchmark.py output. This is a numerical
accuracy demonstration, not a reconstruction of any manufacturer's DVH engine.
"""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input', type=Path, default=Path(__file__).parent/'data/sampling_accuracy.json')
    ap.add_argument('--output', type=Path, default=Path('docs/sampling_accuracy.png'))
    args = ap.parse_args()
    d = json.loads(args.input.read_text(encoding='utf-8'))
    plt.rcParams.update({'font.size': 11, 'axes.spines.top': False, 'axes.spines.right': False})
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.7), sharex=True, sharey=True)
    for ax, case, title in zip(axes, [2, 4], ['6.5 mm³ sphere · 2.32 mm equivalent diameter', '120 mm³ tilted ellipsoid · 6.12 mm equivalent diameter']):
        ax.plot(d['thresholds_Gy'], d['exact_volume_pct'], color='#354550', lw=3.8, label='Known exact DVH')
        for method, color, style, name in [
            ('CT planes only; exact dose', '#d97618', '-', '1-mm contour planes only'),
            ('Exact continuous dose', '#008e9b', '--', 'Complete 3D integration · 0.025 mm'),
        ]:
            c = next(r for r in d['curves'] if r['case'] == case and r['method'] == method)
            ax.plot(d['thresholds_Gy'], c['volume_pct'], color=color, ls=style, lw=2.2, label=name)
        ax.set(title=title, xlabel='Dose [Gy]', xlim=(19.5, 28.3), ylim=(0, 102))
        ax.grid(alpha=.15)
    axes[0].set_ylabel('Target volume [%]')
    fig.suptitle('Same shape. Same exact dose. Only volume sampling changes.', fontsize=16, y=.98)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower center', ncol=3, frameon=False, bbox_to_anchor=(.5, .045))
    fig.text(.5, .015, 'The dashed 3D curve follows the known reference. CT spacing is not dose-grid spacing.', ha='center', fontsize=10)
    fig.subplots_adjust(left=.065, right=.99, top=.81, bottom=.24, wspace=.15)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=170, facecolor='white')
    plt.close(fig)
    print(args.output)


if __name__ == '__main__':
    main()
