"""Illustrate a defined alternative readout and its measured native agreement.

Plot stored results only; no native-curve fitting or numerical recalculation.
The native curve is an agreement reference, not a known continuous-dose truth.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input',type=Path,default=Path(__file__).parent/'data/hdss_sampling_comparison.json')
    ap.add_argument('--output',type=Path,default=Path('docs/boundary_grid_option.png'))
    args=ap.parse_args();data=json.loads(args.input.read_text(encoding='utf-8'))
    rows=data['rows'];assert len(rows)==24
    r=next(x for x in rows if x['target']=='GTV09')
    plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(1,2,figsize=(12.5,4.9),gridspec_kw={'width_ratios':[1.1,1]})
    ax=axes[0]
    ax.plot(r['native_dose_Gy'],r['native_pct'],color='#3e4c59',lw=3.5,ls='--',label='Stored native TPS DVH')
    for key,color,dash,label in [('plane','#d87718','-','CT-plane readout'),('surface_grid','#008c9e','-','Fine 3D boundary + dose samples')]:
        ax.plot(r[key]['dose_Gy'],r[key]['volume_pct'],color=color,ls=dash,lw=2.2,label=label)
    ax.set(title='A. GTV09: the additional option approaches the native curve',xlabel='Dose [Gy]',ylabel='Evaluated target volume [%]',xlim=(15,29),ylim=(0,101))
    ax.legend(loc='lower left',fontsize=9,frameon=False)
    ax=axes[1];xx=np.arange(1,25)
    a=np.array([abs(r['plane']['delta_D98_Gy']) for r in rows]);b=np.array([abs(r['surface_grid']['delta_D98_Gy']) for r in rows])
    for x,y,z in zip(xx,a,b):ax.plot([x-.13,x+.13],[y,z],color='#c7d1d8',lw=1,zorder=1)
    ax.scatter(xx-.13,a,color='#d87718',s=28,label='CT-plane readout',zorder=3)
    ax.scatter(xx+.13,b,color='#008c9e',s=28,marker='D',label='Fine 3D boundary + dose samples',zorder=3)
    ax.set(title='B. All 24 GTVs: residual differences remain',xlabel='GTV number',ylabel='Absolute D98 difference from native [Gy]',xlim=(.2,24.8),ylim=(-.04,2.12),xticks=[1,4,8,12,16,20,24])
    ax.axhline(0,color='#627480',lw=.8)
    ax.text(.03,.995,f'Mean ± SD: {a.mean():.3f} ± {a.std(ddof=1):.3f} → {b.mean():.3f} ± {b.std(ddof=1):.3f} Gy',transform=ax.transAxes,va='top',fontsize=10)
    for ax in axes:ax.grid(alpha=.16)
    fig.suptitle('An additional HDSS-compatible option: sample dose-grid points inside the fine 3D boundary',fontsize=14,y=.98)
    fig.text(.5,.022,'Both readouts use the same recovered HDSS surface and fine input dose. This tests native agreement, not analytical accuracy.',ha='center',fontsize=10)
    fig.subplots_adjust(left=.065,right=.985,top=.80,bottom=.16,wspace=.25)
    args.output.parent.mkdir(parents=True,exist_ok=True);fig.savefig(args.output,dpi=170,facecolor='white');plt.close(fig)
    print(args.output)


if __name__=='__main__':main()
