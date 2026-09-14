"""Plot the measured native/plane/3D readouts; does not recalculate source dose."""
import argparse,json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

COLORS=['#2478c6','#e87913','#219b55','#d43687','#8854bc','#009cb2',
        '#c34c3b','#8b8a1e','#587ba6','#ee4937','#ab64ac','#008e73']

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--group',type=int,choices=[1,2],default=1)
    ap.add_argument('--output',type=Path,default=Path('docs/hdss_sampling_comparison.png'));args=ap.parse_args()
    data=json.loads((Path(__file__).parent/'data/hdss_sampling_comparison.json').read_text(encoding='utf-8'))
    rows=data['rows'][(args.group-1)*12:args.group*12]
    plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(1,2,figsize=(15,6.5),sharex=True,sharey=True)
    for ax,method,title in zip(axes,['plane','surface_grid'],['Coarse CT-plane evaluation','3D HDSS evaluation']):
        for r,color in zip(rows,COLORS):
            ax.plot(r['native_dose_Gy'],r['native_pct'],color=color,lw=2.1)
            ax.plot(r[method]['dose_Gy'],r[method]['volume_pct'],color=color,lw=1.7,ls='--')
        ax.set(title=title,xlabel='Dose [Gy]',xlim=(15,30),ylim=(0,101));ax.grid(alpha=.14)
        ax.legend([Line2D([],[],color='#405261',lw=2),Line2D([],[],color='#405261',lw=2,ls='--')],
                  ['Native TPS','Computed from HDSS geometry'],loc='lower left',fontsize=10)
    axes[0].set_ylabel('Evaluated target volume [%]')
    fig.suptitle('Same fine dose. Same HDSS geometry. Different DVH sampling.',fontsize=17,y=.985)
    s=data['summary'];left=s['plane']['mean_absolute_D98_Gy'];right=s['surface_grid']['mean_absolute_D98_Gy']
    fig.text(.5,.15,f'Across all 24 GTVs: mean absolute D98 difference from native TPS  {left:.3f} → {right:.3f} Gy',ha='center',fontsize=13,color='#176b67')
    fig.legend([Line2D([],[],color=c,lw=2) for c in COLORS],[r['target'] for r in rows],ncol=12,loc='lower center',bbox_to_anchor=(.5,.07),frameon=False,fontsize=10)
    fig.text(.5,.025,'12 consecutive targets per panel. Solid: native TPS. Dashed: calculated. Curves share 0.2-Gy bins; residual differences remain.',ha='center',fontsize=10)
    fig.subplots_adjust(left=.065,right=.99,top=.82,bottom=.27,wspace=.14)
    args.output.parent.mkdir(parents=True,exist_ok=True);fig.savefig(args.output,dpi=150,facecolor='white');plt.close(fig)
    print(args.output)

if __name__=='__main__':main()
