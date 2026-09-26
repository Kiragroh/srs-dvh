"""An anatomy-free control: same sphere and linear dose, different dose sampling.

python synthetic_example.py
This is an analytical sampling experiment, not a model assigned to a vendor.
"""
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent

def experiment(volume,phase,h):
    radius=(3*volume/(4*np.pi))**(1/3)
    x=np.arange(-radius+h/2,radius,h)
    # Integrate an identical spherical mask for both dose methods.
    yz=x[:,None]**2+x[None,:]**2
    counts=np.array([np.count_nonzero(yz+xx*xx<=radius*radius) for xx in x],dtype=float)
    physical=x+phase
    exact=20+physical
    coarse=20+np.floor(physical+.5)
    def quantile(doses):
        order=np.argsort(doses);cum=np.cumsum(counts[order]);return float(doses[order][np.searchsorted(cum,.02*cum[-1])])
    # For a uniform sphere, P(X/r <= t)=1/2 + 3t/4 - t^3/4.
    lo,hi=-1.,1.
    for _ in range(70):
        mid=(lo+hi)/2
        if .5+.75*mid-.25*mid**3<.02:lo=mid
        else:hi=mid
    truth=20+phase+radius*(lo+hi)/2
    thresholds=np.linspace(16,24,801)
    curve=lambda d:[float(counts[d>=q].sum()/counts.sum()*100) for q in thresholds]
    return dict(volume_mm3=volume,diameter_mm=2*radius,phase_mm=phase,step_mm=h,analytic_D98_Gy=truth,
        linear_D98_Gy=quantile(exact),discrete_D98_Gy=quantile(coarse),
        linear_error_Gy=quantile(exact)-truth,discrete_error_Gy=quantile(coarse)-truth),thresholds,curve(exact),curve(coarse)

def main():
    results=[];fig,axes=plt.subplots(1,3,figsize=(11,3.5),sharey=True)
    for v,ax in zip([6.5,30,120],axes):
        for phase in [0,.5]:
            for h in [.08,.04]:
                row,q,fine,coarse=experiment(v,phase,h);results.append(row)
                assert abs(row['linear_error_Gy']) < 2*h
                if phase==.5 and h==.04:
                    ax.plot(q,fine,c='#008AC9',label='Linear dose at volume samples')
                    ax.plot(q,coarse,c='#8064A2',label='1-mm dose-cell values')
        ax.set(title=f'{v:g} mm³ sphere',xlabel='Dose (Gy)',xlim=(16.5,24),ylim=(0,101));ax.grid(alpha=.15);ax.spines[['top','right']].set_visible(False)
    axes[0].set_ylabel('Volume (%)');fig.legend(*axes[0].get_legend_handles_labels(),loc='lower center',ncol=2,frameon=False)
    fig.subplots_adjust(bottom=.25,wspace=.2)
    out=ROOT/'figures';out.mkdir(exist_ok=True)
    for ext in ['png','svg','pdf']:fig.savefig(out/f'figure_S2_synthetic_sampling.{ext}',dpi=180)
    plt.close(fig)
    with (ROOT/'tables/table_S1_analytical_check.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(results[0]));w.writeheader();w.writerows(results)
    print('12 analytic controls passed; no patient images or contours used.')

if __name__=='__main__':main()
