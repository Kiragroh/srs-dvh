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
    parser.add_argument('--method',choices=['full','surface'],default='surface')
    args=parser.parse_args()
    data=json.loads((Path(__file__).parent/'data/hdss_forward_comparison.json').read_text(encoding='utf-8'))
    rows=data['targets'][(args.group-1)*12:args.group*12]
    method='full voxel-volume integration'
    if args.method=='surface':
        candidates=json.loads((Path(__file__).parent/'data/surface_grid_comparison.json').read_text(encoding='utf-8'))['rows']
        keyed={r['target']:r for r in candidates if r['plan']=='M00_Original'}
        for r in rows:
            s=keyed[r['target']]
            r.update(dose_Gy=s['dose_Gy'],original_3d_pct=s['surface_grid_pct'],recovered_hdss_pct=s['recovered_hdss_pct'],
                     comparison_dose_Gy=s['display_dose_Gy'],comparison_pct=s['display_volume_pct'])
        method='surface + dose-grid points'
    plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(1,2,figsize=(15,6.4),sharex=True,sharey=True)
    for r,color in zip(rows,COLORS):
        axes[0].plot(r['dose_Gy'],r['original_3d_pct'],color=color,lw=3.4,alpha=.42)
        axes[0].plot(r['dose_Gy'],r['recovered_hdss_pct'],color=color,lw=1.5,ls='--')
        axes[1].plot(r['stored_dose_Gy'],r['stored_volume_pct'],color=color,lw=1.8)
        axes[1].plot(r.get('comparison_dose_Gy',r['dose_Gy']),r.get('comparison_pct',r['recovered_hdss_pct']),color=color,lw=1.6,ls='--')
    titles=['A. Does HDSS retain the original target?\nSame dose and same selected method',
            'B. Does our DVH match the native TPS?\nDifferent evaluation methods, not import routes']
    labels=[('Original target: selected method','Target recovered from HDSS: same method'),
            ('DVH stored by the native TPS','HDSS target: '+method)]
    for ax,title,pair in zip(axes,titles,labels):
        ax.set(title=title,xlabel='Dose [Gy]',xlim=(15,30),ylim=(0,101))
        ax.grid(alpha=.15)
        ax.legend([Line2D([],[],color='#435363',lw=2),Line2D([],[],color='#435363',lw=2,ls='--')],pair,fontsize=9,loc='lower left',framealpha=.95)
    axes[0].set_ylabel('Evaluated ROI volume [%]')
    fig.suptitle('HDSS evaluation: '+method,fontsize=17,y=.99)
    fig.text(.29,.14,'A: the source is preserved and the curves overlap.',ha='center',fontsize=11,color='#176649')
    fig.text(.77,.14,'B: '+('same 0.2-Gy bins; remaining method differences stay visible.' if args.method=='surface' else 'the remaining native-method difference stays visible.'),ha='center',fontsize=10,color='#435363')
    fig.legend([Line2D([],[],color=c,lw=2) for c in COLORS],[r['target'] for r in rows],ncol=12,loc='lower center',bbox_to_anchor=(.5,.065),frameon=False,fontsize=10)
    fig.text(.5,.025,'12 consecutive synthetic targets; colour identifies the target. The gap in B alone proves neither TPS error nor HDSS loss.',ha='center',fontsize=10)
    fig.subplots_adjust(left=.065,right=.99,top=.80,bottom=.26,wspace=.14)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(args.output,dpi=160,facecolor='white');plt.close(fig)
    print(args.output)


if __name__=='__main__':main()
