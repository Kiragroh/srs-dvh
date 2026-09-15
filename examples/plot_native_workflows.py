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
        if r['fineplane_pct']:
            axes[0].plot(data['default_dose_Gy'],r['fineplane_pct'],color=color,lw=1.45,ls='--')
        else:missing.append(r['target'])
        axes[1].plot(data['dose_Gy'],r['hdss_pct'],color=color,lw=1.45,ls='--')
    for ax in axes:
        ax.set(xlim=(15,30),ylim=(0,102),xlabel='Dose [Gy]')
        ax.grid(alpha=.14);ax.spines[['top','right']].set_visible(False)
    axes[0].set_ylabel('GTV volume [%]')
    axes[0].set_title('CT-plane contours\nDose sampled on the supplied contour planes',loc='left',fontsize=12)
    axes[1].set_title('HDSS geometry\nDose sampled throughout the complete target volume',loc='left',fontsize=12)
    if missing:axes[0].text(.025,.05,'No sampled volume: '+', '.join(missing),transform=axes[0].transAxes,fontsize=9)
    fig.suptitle('Same fine dose in both panels · compare structure and volume sampling',fontsize=17)
    fig.legend([Line2D([0],[0],color=x,lw=2) for x in COLORS],[r['target'] for r in rows],ncol=6,loc='lower center',bbox_to_anchor=(.5,.095),frameon=False,fontsize=10)
    fig.text(.5,.02,'Solid: native TPS before conversion. Dashed: independent readout. One colour per target.\nContours can also be interpolated between planes; that estimates the missing shape rather than restoring the original.',ha='center',fontsize=10)
    fig.tight_layout(rect=[0,.20,1,.94])
    for ext in ['png','svg','pdf']:fig.savefig(ROOT/f'docs/native_workflow_comparison.{ext}',dpi=130,facecolor='white')
    svg=ROOT/'docs/native_workflow_comparison.svg'
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8',newline='\n')
    plt.close(fig)
    print('Same-dose comparison: 12 targets; missing plane curves:',len(missing))

if __name__=='__main__':main()
