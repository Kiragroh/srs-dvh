"""Analytical SRS accuracy benchmark independent of all vendor DVHs."""
import argparse,json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from srs_dvh import DoseGrid,ImplicitROI,DVH,calculate

OUT=Path('results/analytical')

def body(volume,elongated,angle,center):
    radius=(3*volume/(4*np.pi))**(1/3)
    radii=radius*np.array([1.5,1.,2/3]) if elongated else np.full(3,radius)
    t=np.deg2rad(angle);rot=np.array([[np.cos(t),0,np.sin(t)],[0,1,0],[-np.sin(t),0,np.cos(t)]])
    inv=np.diag(1/radii)@rot.T
    rho=lambda points:np.sum(((points-center)@inv.T)**2,axis=1)
    extent=np.sqrt(np.sum((rot*radii[None,:])**2,axis=1))
    roi=ImplicitROI(lambda pts:rho(pts)<=1,center-extent,center+extent)
    return roi,lambda pts:np.maximum(28-8*rho(pts),0),extent

def dose_grid(field,center,extent,spacing):
    lo=np.floor((center-extent-2)/spacing)*spacing
    hi=np.ceil((center+extent+2)/spacing)*spacing
    n=np.rint((hi-lo)/spacing).astype(int)+1
    aff=np.diag([spacing,spacing,spacing,1.]);aff[:3,3]=lo
    ix=np.indices(n).reshape(3,-1).T;world=ix@aff[:3,:3].T+lo
    return DoseGrid(field(world).reshape(n),aff)

def plane_only(roi,field,step=.025):
    lo=roi.lower_mm;hi=roi.upper_mm
    nx,ny=np.ceil((hi-lo)[:2]/step).astype(int);dx,dy=(hi-lo)[:2]/[nx,ny]
    x=lo[0]+(np.arange(nx)+.5)*dx;y=lo[1]+(np.arange(ny)+.5)*dy
    z=np.arange(np.ceil(lo[2]),np.floor(hi[2])+1)
    pts=np.stack(np.meshgrid(x,y,z,indexing='ij'),axis=-1).reshape(-1,3)
    pts=pts[roi.contains(pts)]
    return DVH(field(pts),np.full(len(pts),dx*dy*1.),step)

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    thresholds=np.linspace(15,29,281)
    exact_curve=100*np.clip((28-thresholds)/8,0,1)**1.5
    expected=dict(D98_Gy=float(28-8*.98**(2/3)),Dmean_Gy=23.2,V20_pct=100.)
    rows=[];curves=[]
    configs=[(6.5,False,0,[.13,-.27,.49]),(6.5,False,0,[.53,.13,.99]),(30.,True,30,[.13,-.27,.49]),(120.,True,30,[.13,-.27,.49])]
    for number,(volume,elongated,angle,center) in enumerate(configs,1):
        center=np.array(center);roi,field,extent=body(volume,elongated,angle,center)
        label=f'{volume:g} mm³ · '+('ellipsoid, 30°' if elongated else 'sphere')+f' · phase {number}'
        source_doses={'Exact continuous dose':field}
        source_doses.update({f'{spacing:g}-mm dose grid':dose_grid(field,center,extent,spacing) for spacing in [1.,.4,.1]})
        for name,dose in source_doses.items():
            for h in ([.1,.05,.025] if name=='Exact continuous dose' else [.05,.025]):
                result=calculate(roi,dose,h);m=result.metrics()
                row=dict(case=number,label=label,nominal_volume_mm3=volume,elongated=elongated,angle_deg=angle,method=name,**m,
                         volume_error_pct=100*(m['volume_mm3']/volume-1),D98_error_Gy=m['D98_Gy']-expected['D98_Gy'],
                         Dmean_error_Gy=m['Dmean_Gy']-expected['Dmean_Gy'],V20_error_pp=m['V20_pct']-100,
                         max_curve_error_pp=float(np.max(abs(result.volume_at_dose(thresholds)-exact_curve))))
                rows.append(row)
                if h==.025:curves.append(dict(case=number,method=name,volume_pct=result.volume_at_dose(thresholds).tolist()))
        result=plane_only(roi,field);m=result.metrics()
        rows.append(dict(case=number,label=label,nominal_volume_mm3=volume,elongated=elongated,angle_deg=angle,method='CT planes only; exact dose',**m,
                         volume_error_pct=100*(m['volume_mm3']/volume-1),D98_error_Gy=m['D98_Gy']-expected['D98_Gy'],
                         Dmean_error_Gy=m['Dmean_Gy']-expected['Dmean_Gy'],V20_error_pp=m['V20_pct']-100,
                         max_curve_error_pp=float(np.max(abs(result.volume_at_dose(thresholds)-exact_curve)))))
        curves.append(dict(case=number,method='CT planes only; exact dose',volume_pct=result.volume_at_dose(thresholds).tolist()))
        print(label,flush=True)
    exact=[r for r in rows if r['method']=='Exact continuous dose' and r['integration_step_mm']==.025]
    passed=all(abs(r['D98_error_Gy'])<.025 and abs(r['Dmean_error_Gy'])<.02 and abs(r['volume_error_pct'])<.3 and r['max_curve_error_pp']<.35 for r in exact)
    result=dict(status='PASS' if passed else 'FAIL',scope='Analytical shape and dose accuracy; not proof of TPS equivalence',
                expected=expected,thresholds_Gy=thresholds.tolist(),exact_volume_pct=exact_curve.tolist(),rows=rows,curves=curves)
    (OUT/'analytical_srs_validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    fig,axes=plt.subplots(1,2,figsize=(11.4,4.7),constrained_layout=True)
    colors={'Exact continuous dose':'#008e86','0.1-mm dose grid':'#1177cc','0.4-mm dose grid':'#b768a2','1-mm dose grid':'#ec831c'}
    for ax in axes:
        ax.plot(thresholds,exact_curve,color='#333',lw=2.3,label='Analytical truth',zorder=4)
        ax.set(xlim=(15,29),ylim=(0,102),xlabel='Dose [Gy]',ylabel='Target volume [%]')
        ax.grid(alpha=.18);ax.spines[['top','right']].set_visible(False)
    for case,color in [(1,'#af5593'),(2,'#ec831c')]:
        curve=next(x for x in curves if x['case']==case and x['method']=='CT planes only; exact dose')
        axes[0].plot(thresholds,curve['volume_pct'],color=color,lw=1.7,label=f'CT planes only · position {case}')
    for curve in [x for x in curves if x['case']==1 and x['method'] in ['Exact continuous dose','0.1-mm dose grid','1-mm dose grid']]:
        axes[1].plot(thresholds,curve['volume_pct'],color=colors[curve['method']],ls='--' if curve['method']=='Exact continuous dose' else '-',lw=1.8,label='3D · '+curve['method'])
    axes[0].set_title('A. Exact dose; change the volume sampling',fontsize=10)
    axes[1].set_title('B. Fine 3D integration; change the input dose grid',fontsize=10)
    for ax in axes:ax.legend(loc='lower left',frameon=False,fontsize=7.7)
    fig.suptitle('Known 6.5-mm³ sphere: separate volume sampling from dose-grid effects',fontsize=12)
    for suffix in ['svg','png','pdf']:fig.savefig(OUT/f'analytical_srs_dvh.{suffix}',dpi=160)
    plt.close(fig)
    print('Accuracy gate:',result['status'],flush=True)
    print('Exact field:',[(x['case'],x['D98_error_Gy'],x['max_curve_error_pp']) for x in exact],flush=True)
    for r in rows:
        if r['method']=='1-mm dose grid' and r['integration_step_mm']==.025:print('1 mm dose input',r['case'],'D98 error',r['D98_error_Gy'],'V20',r['V20_pct'],flush=True)
    if not passed:raise SystemExit(1)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,default=OUT)
    OUT=parser.parse_args().output_dir
    main()
