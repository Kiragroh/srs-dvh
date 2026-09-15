"""Plot archived synthetic target curves against the pre-export native TPS DVH.

This is a workflow comparison, not a recalculation or an isolated algorithm test.
"""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

ROOT=Path(__file__).resolve().parents[1]
COLORS=['#1764c0','#df7100','#158653','#bd277c','#7b42bd','#13939b',
        '#a44b39','#788319','#3a5a80','#e2471b','#655195','#00a080']

def main():
    data=json.loads((ROOT/'examples/data/native_workflow_comparison.json').read_text(encoding='utf-8'))
    rows=[r for r in data['rows'] if r['plan']=='M00_Original' and int(r['target'][3:])<=12]
    assert len(rows)==12
    fig,axes=plt.subplots(1,2,figsize=(14.2,6.6),sharex=True,sharey=True)
    missing=[]
    for r,color in zip(rows,COLORS):
        for ax in axes:ax.plot(r['native_dose_Gy'],r['native_pct'],color=color,lw=1.6)
        if r['default_pct']:
            axes[0].plot(data['default_dose_Gy'],r['default_pct'],color=color,lw=1.45,ls='--')
        else:missing.append(r['target'])
        axes[1].plot(data['dose_Gy'],r['hdss_pct'],color=color,lw=1.45,ls='--')
    for ax in axes:
        ax.set(xlim=(15,30),ylim=(0,102),xlabel='Dose [Gy]')
        ax.grid(alpha=.14);ax.spines[['top','right']].set_visible(False)
    axes[0].set_ylabel('GTV volume [%]')
    axes[0].set_title('Ordinary DICOM workflow\nCT-plane contours + 1-mm dose · dicompyler-core defaults',loc='left',fontsize=12)
    axes[1].set_title('Our complete 3D workflow\nRecovered HDSS geometry + fine dose · volume integration',loc='left',fontsize=12)
    if missing:axes[0].text(.025,.05,'No sampled volume: '+', '.join(missing),transform=axes[0].transAxes,fontsize=9)
    fig.suptitle('Both workflows compared with the native TPS DVH before any export',fontsize=17)
    fig.legend([Line2D([0],[0],color=x,lw=2) for x in COLORS],[r['target'] for r in rows],ncol=6,loc='lower center',bbox_to_anchor=(.5,.095),frameon=False,fontsize=10)
    fig.text(.5,.02,'Solid: native TPS reference. Dashed: the specified workflow. One colour per target.\nThe inputs and evaluation differ; full 3D preserves fine information but does not exactly reproduce the TPS curve.',ha='center',fontsize=10)
    fig.tight_layout(rect=[0,.20,1,.94])
    for ext in ['png','svg','pdf']:fig.savefig(ROOT/f'docs/native_workflow_comparison.{ext}',dpi=130,facecolor='white')
    plt.close(fig)
    print('Native/workflow comparison: 12 targets; missing defaults:',len(missing))

if __name__=='__main__':main()
