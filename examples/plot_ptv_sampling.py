"""Illustrate plane-only volume weighting in two idealised spherical PTVs.

The sizes (30 and 600 mm3) bracket the approximate PTV range of the public
benchmark. They are synthetic illustrations, not selected clinical targets.
Both centres are halfway between fixed 1-mm planes; no grid phase is fitted.
Exact continuous dose D = 28 - 8 (r/R)^2 is shared by both sampling methods.
Companion DVHs are calculated and checked in the JSON; the figure focuses on
geometry because the example's dose curves add little to that explanation.
"""
import argparse
import gc
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, Rectangle
import numpy as np

from srs_dvh import calculate
from analytical_benchmark import body, plane_only

HERE = Path(__file__).resolve().parent
TEAL, ORANGE, GREY = '#008e9b', '#d97618', '#354550'


def compute():
    thresholds = np.linspace(15, 29, 281)
    exact = 100 * np.clip((28 - thresholds) / 8, 0, 1)**1.5
    result = {
        'scope': 'Illustrative synthetic PTVs; controlled volume-sampling test, not TPS agreement or clinical thresholds',
        'volumes_chosen_mm3': [30., 600.],
        'centre_mm': [0., 0., .5],
        'contour_planes_mm': 'integer z coordinates, spacing 1 mm',
        'dose': 'Exact continuous D(x) = 28 - 8 (r/R)^2 Gy inside each sphere; no dose-grid interpolation',
        'plane_rule': 'Exact sphere intersections on integer z planes; XY midpoint spacing at most 0.025 mm; each point weighted by XY area times 1 mm',
        'full3d_rule': 'srs_dvh.calculate on the exact spherical body, uniform 3D midpoint integration; plot 0.05-mm result',
        'geometry_panel': 'True mid-sagittal boundary overlaid with exact contour widths extruded by half the plane spacing on either side; equal physical scale',
        'dose_Gy': thresholds.tolist(),
        'exact_volume_pct': exact.tolist(),
        'cases': [],
        'generator_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    for volume in result['volumes_chosen_mm3']:
        roi, field, extent = body(volume, False, 0, np.array(result['centre_mm']))
        z = np.arange(np.ceil(roi.lower_mm[2]), np.floor(roi.upper_mm[2]) + 1)
        case = {'volume_mm3': volume, 'diameter_mm': float(2*extent[0]), 'plane_z_mm': z.tolist(), 'refinements': []}
        for step in [.1, .05]:
            dvh = calculate(roi, field, step)
            curve = dvh.volume_at_dose(thresholds)
            case['refinements'].append({**dvh.metrics(), 'max_curve_error_pp': float(np.max(abs(curve-exact)))})
            if step == .05:
                case['full3d_volume_pct'] = curve.tolist()
                case['full3d_max_curve_error_pp'] = case['refinements'][-1]['max_curve_error_pp']
            del dvh
            gc.collect()
        dvh = plane_only(roi, field)
        curve = dvh.volume_at_dose(thresholds)
        case['plane_metrics'] = dvh.metrics()
        case['plane_volume_pct'] = curve.tolist()
        case['plane_max_curve_error_pp'] = float(np.max(abs(curve-exact)))
        result['cases'].append(case)
    return result


def plot(data, output):
    plt.rcParams.update({'font.size': 11, 'axes.spines.top': False, 'axes.spines.right': False})
    fig = plt.figure(figsize=(12.5, 6.0))
    grid = fig.add_gridspec(1, 2, left=.085, right=.98, bottom=.15, top=.72,
                           wspace=.23)
    for col, case in enumerate(data['cases']):
        ax = fig.add_subplot(grid[0, col])
        radius = case['diameter_mm']/2
        centre_z = data['centre_mm'][2]
        for z in np.arange(-5, 7):
            ax.axhline(z, color='#cbd5db', lw=.8, zorder=0)
        for z in case['plane_z_mm']:
            width = np.sqrt(radius**2 - (z-centre_z)**2)
            ax.add_patch(Rectangle((-width, z-.5), 2*width, 1,
                                  facecolor=ORANGE, alpha=.13, linewidth=0))
            ax.plot([-width, width], [z, z], color=ORANGE, lw=1.5)
            ax.plot([-width, -width], [z-.5, z+.5], color=ORANGE, lw=1.2)
            ax.plot([width, width], [z-.5, z+.5], color=ORANGE, lw=1.2)
            ax.plot([-width, width], [z-.5, z-.5], color=ORANGE, lw=.65, alpha=.65)
            ax.plot([-width, width], [z+.5, z+.5], color=ORANGE, lw=.65, alpha=.65)
        ax.add_patch(Circle((0, centre_z), radius, facecolor='none', edgecolor=TEAL, lw=2.5, zorder=5))
        ax.set(xlim=(-6.2, 6.2), ylim=(-5.7, 6.7), aspect='equal',
               xticks=[-5, 0, 5], yticks=[-5, 0, 5], xlabel='x [mm]')
        ax.set_ylabel('z [mm]')
        title = 'Small PTV' if col == 0 else 'Larger PTV'
        ax.set_title(f"{title}: {case['volume_mm3']:g} mm³\nDiameter {case['diameter_mm']:.2f} mm · {len(case['plane_z_mm'])} contour planes", fontsize=12, pad=10)
    fig.suptitle('Why 1-mm contour spacing matters more for a small PTV', fontsize=17, y=.985)
    fig.text(.5, .919, 'Each slice represents a larger fraction of the small target. Both PTVs are shown at the same scale.', ha='center', fontsize=11)
    handles = [Line2D([], [], color=TEAL, lw=2.5, label='Full PTV boundary'),
               Line2D([], [], color=ORANGE, lw=2, label='1-mm contours / assigned slice volumes')]
    fig.legend(handles=handles, loc='upper center', ncol=2, frameon=False, bbox_to_anchor=(.5,.885))
    fig.text(.5, .030, 'Idealised spherical PTVs. Orange illustrates assigning a full 1-mm slice thickness to each contour.', ha='center', fontsize=10)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=170, facecolor='white')
    plt.close(fig)


def verify(data):
    """Check full-body quadrature and plane quadrature against separate exact answers."""
    dose = np.array(data['dose_Gy'])
    exact = 100*np.clip((28-dose)/8, 0, 1)**1.5
    evidence = []
    for case in data['cases']:
        radius = case['diameter_mm']/2
        z = np.array(case['plane_z_mm']) - data['centre_mm'][2]
        plane_volume = np.pi*np.maximum(radius**2-z**2, 0).sum()
        dose_radius2 = radius**2*np.clip((28-dose)/8, 0, 1)
        plane_exact = 100*np.pi*np.maximum(dose_radius2[:, None]-z[None, :]**2, 0).sum(axis=1)/plane_volume
        full_error = float(np.max(abs(np.array(case['full3d_volume_pct'])-exact)))
        plane_error = float(np.max(abs(np.array(case['plane_volume_pct'])-plane_exact)))
        plane_volume_error = 100*(case['plane_metrics']['volume_mm3']/plane_volume-1)
        assert full_error < .35
        assert plane_error < .25 and abs(plane_volume_error) < .1
        assert case['refinements'][-1]['max_curve_error_pp'] < case['refinements'][0]['max_curve_error_pp']
        evidence.append({'volume_mm3': case['volume_mm3'],
                         'full3d_vs_exact_body_max_pp': full_error,
                         'plane_quadrature_vs_exact_planes_max_pp': plane_error,
                         'plane_quadrature_vs_exact_planes_volume_error_pct': plane_volume_error})
    return {'status': 'PASS', 'scope': 'Independent closed-form body and plane references at 281 dose thresholds', 'cases': evidence}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, default=HERE/'data/ptv_sampling.json')
    parser.add_argument('--output', type=Path, default=HERE.parent/'docs/ptv_sampling.png')
    parser.add_argument('--recalculate', action='store_true')
    args = parser.parse_args()
    if args.recalculate:
        data = compute()
        data['validation'] = verify(data)
        args.data.parent.mkdir(parents=True, exist_ok=True)
        args.data.write_text(json.dumps(data, indent=2), encoding='utf-8')
    else:
        data = json.loads(args.data.read_text(encoding='utf-8'))
        verify(data)
    plot(data, args.output)
    print(json.dumps([{k: c[k] for k in ['volume_mm3', 'diameter_mm', 'plane_max_curve_error_pp', 'full3d_max_curve_error_pp']} for c in data['cases']], indent=2))
    print(args.output)


if __name__ == '__main__':
    main()
