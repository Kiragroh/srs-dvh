"""Plot measured forward-reconstruction results, with native residuals visible.

This script plots the supplied numerical evidence. It is not a standalone
recalculation of the source benchmark's dose or of a proprietary TPS histogram.
"""
from pathlib import Path
import argparse,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

COLORS=['#2478c6','#e87913','#219b55','#d43687','#8854bc','#009cb2',
        '#c34c3b','#8b8a1e','#587ba6','#ee4937','#ab64ac','#008e73']


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=Path('docs/hdss_forward_validation.png'))
    parser.add_argument('--group',type=int,choices=[1,2],default=1)
    args=parser.parse_args()
    data=json.loads((Path(__file__).parent/'data/hdss_forward_comparison.json').read_text(encoding='utf-8'))
    rows=data['targets'][(args.group-1)*12:args.group*12]
    plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(1,3,figsize=(18,6.2),sharex=True,sharey=True)
    for r,color in zip(rows,COLORS):
        axes[0].plot(r['stored_dose_Gy'],r['stored_volume_pct'],color=color,lw=1.8)
        axes[0].plot(r['dose_Gy'],r['regular_dose_pct'],color=color,lw=1.6,ls='--')
        axes[1].plot(r['dose_Gy'],r['original_3d_pct'],color=color,lw=3.4,alpha=.42)
        axes[1].plot(r['dose_Gy'],r['recovered_hdss_pct'],color=color,lw=1.5,ls='--')
        axes[2].plot(r['stored_dose_Gy'],r['stored_volume_pct'],color=color,lw=1.8)
        axes[2].plot(r['dose_Gy'],r['recovered_hdss_pct'],color=color,lw=1.6,ls='--')
    titles=['1  The initial problem','2  HDSS preserves the source readout','3  Native-reference agreement remains separate']
    labels=[('Stored native DVH','Original body + regular 1-mm dose'),
            ('Original binary body + fine dose','Recovered HDSS body + same fine dose'),
            ('Stored native DVH','Recovered HDSS body + fine dose')]
    for ax,title,pair in zip(axes,titles,labels):
        ax.set(title=title,xlabel='Dose [Gy]',xlim=(15,30),ylim=(0,101))
        ax.grid(alpha=.15)
        ax.legend([Line2D([],[],color='#435363',lw=2),Line2D([],[],color='#435363',lw=2,ls='--')],pair,fontsize=9,loc='lower left',framealpha=.95)
    axes[0].set_ylabel('Evaluated ROI volume [%]')
    fig.suptitle('High-definition DVH evaluation: demonstrate preservation, then verify the reference',fontsize=17,y=.99)
    fig.legend([Line2D([],[],color=c,lw=2) for c in COLORS],[r['target'] for r in rows],ncol=12,loc='lower center',bbox_to_anchor=(.5,.07),frameon=False,fontsize=10)
    fig.text(.5,.025,'Twelve consecutive synthetic targets. Full 3D integration: 0.05 mm. No curve fitting. '
             'The middle-panel agreement does not establish native TPS equivalence.',ha='center',fontsize=10)
    fig.subplots_adjust(left=.055,right=.99,top=.85,bottom=.23,wspace=.13)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(args.output,dpi=160,facecolor='white');plt.close(fig)
    print(args.output)


if __name__=='__main__':main()
