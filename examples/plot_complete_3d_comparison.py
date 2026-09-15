"""Plot matched-dose source preservation using public synthetic benchmark curves."""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group',type=int,choices=[1,2],default=1)
    parser.add_argument('--margin',type=int,choices=[0,1,2],default=0)
    parser.add_argument('--roi',choices=['GTV','PTV'],default='GTV')
    parser.add_argument('--output',type=Path,default=Path('docs/complete_3d_comparison.png'))
    args=parser.parse_args()
    data=json.loads((Path(__file__).parent/'data/complete_3d_comparison.json').read_text(encoding='utf-8'))
    rows=[r for r in data['rows'] if r['margin_mm']==args.margin and r['target'].startswith(args.roi) and (args.group-1)*12<int(r['target'][3:])<=args.group*12]
    if len(rows)!=12:raise ValueError('This plan/ROI combination has no twelve-target group')
    colors=['#1764ab','#e87818','#168350','#c72c7e','#7844a7','#008e98','#aa493c','#6a721b','#536984','#d44910','#8478ac','#059a6e']
    fig,axes=plt.subplots(1,2,figsize=(15,6),sharex=True,sharey=True)
    for ax,key,title in zip(axes,['hdss','ordinary_contours'],['HDSS recovers the source readout','CT-plane contours can change the readout']):
        for r,color in zip(rows,colors):
            ax.plot(data['dose_Gy'],r['source']['curve_pct'],color=color,lw=1.6,label=r['target'])
            ax.plot(data['dose_Gy'],r[key]['curve_pct'],color=color,lw=1.6,ls=(0,(4,3)))
        ax.set(xlim=(15,30),ylim=(0,102),xlabel='Dose [Gy]',title=title)
        ax.grid(alpha=.18);ax.spines[['top','right']].set_visible(False)
    axes[0].set_ylabel('Target volume [%]')
    fig.suptitle('Same fine dose and complete 3D evaluator; change only the structure input',fontsize=17)
    handles,labels=axes[0].get_legend_handles_labels()
    fig.legend(handles,labels,loc='lower center',ncol=6,bbox_to_anchor=(.5,.06),frameon=False)
    fig.text(.5,.025,'Solid: original source. Dashed: returned structure. Colours identify targets. This compares geometry preservation, not native TPS algorithms.',ha='center',fontsize=10)
    fig.tight_layout(rect=(0,.16,1,.94))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(args.output,dpi=160);plt.close(fig)
    print(args.output)


if __name__=='__main__':main()
