"""Reproduce paper-concept figures and tables from the included numeric extracts.

Run: python build_figures.py
Requires numpy and matplotlib. No image data, network or commercial TPS required.
"""
from pathlib import Path
import csv, json, gzip
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT=Path(__file__).resolve().parent
FIG=ROOT/'figures'; TABLE=ROOT/'tables'
BLUE, PURPLE, INK='#008AC9','#8064A2','#243357'
ROUTES=['STD','HDSS','01_Eclipse_STD_Low','02_Eclipse_STD_High','03_Eclipse_HDSS_Low','04_Eclipse_HDSS_High','Monaco']
LABELS=['Standard','HDSS recovery','Eclipse STD L','Eclipse STD H','Eclipse HDSS L','Eclipse HDSS H','Monaco STD']
COLORS=['#DB851B','#008AC9','#A8A4AD','#8064A2','#B67C9A','#AB365A','#28745C']

def load(name):
    with (ROOT/'data'/name).open(encoding='utf-8-sig') as f:return list(csv.DictReader(f))
def read(name):
    if name=='native_curves.json':return json.loads(gzip.decompress((ROOT/'data'/(name+'.gz')).read_bytes()))
    return json.loads((ROOT/'data'/name).read_text(encoding='utf-8'))
def write(name,rows):
    with (TABLE/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def finish(fig,name):
    fig.savefig(FIG/(name+'.png'),dpi=160,facecolor='white')
    fig.savefig(FIG/(name+'.pdf'),metadata={'Author':'','Creator':'Reproducible numeric figure'},facecolor='white')
    fig.savefig(FIG/(name+'.svg'),metadata={'Creator':'Reproducible numeric figure'},facecolor='white')
    plt.close(fig)
def clean(ax):
    ax.spines[['top','right']].set_visible(False);ax.grid(alpha=.14);ax.set_axisbelow(True)
def subset(rows,m,route):return [r for r in rows if r['arm']==f'M0{m}_{route}']

def main():
    FIG.mkdir(exist_ok=True);TABLE.mkdir(exist_ok=True)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.labelcolor':INK,'text.color':INK,'axes.titlesize':12,'svg.fonttype':'none'})
    rows=load('fixed_dose.csv'); design=load('target_design.csv'); positions=load('target_positions.csv')
    assert len(rows)==480 and len(design)==24
    # Figure 1: one geometry panel, one experimental decomposition.
    fig=plt.figure(figsize=(12,4.7));ax=fig.add_subplot(121,projection='3d')
    for vol,col in [(6.5,BLUE),(30,PURPLE),(120,'#DB851B')]:
        ids={r['id'] for r in design if float(r['analytic_volume_mm3'])==vol}
        rr=[r for r in positions if r['margin_mm']=='0' and r['target'] in ids]
        ax.scatter(*[[float(r[k]) for r in rr] for k in ['x_mm','y_mm','z_mm']],s=vol**(2/3)*8,c=col,label=f'{vol:g} mm³ (n={len(rr)})',depthshade=False,edgecolors='white')
    ax.set(xlabel='x (mm)',ylabel='y (mm)',zlabel='z (mm)',title='A  24 synthetic targets, one anatomy')
    ax.set_box_aspect((1,1,1));ax.legend(loc='upper center',bbox_to_anchor=(.5,-.04),ncol=1,frameon=False,fontsize=9)
    ax=fig.add_subplot(122);ax.axis('off');ax.set(xlim=(0,10),ylim=(0,8))
    for y,title,txt,c in [(6,'1  Structure transfer','Same target, changed representation',BLUE),(3.9,'2  DVH evaluation','Same dose: common versus native readout',PURPLE),(1.8,'3  Replanning','New dose, evaluated on original target',INK)]:
        ax.add_patch(FancyBboxPatch((.3,y-1.2),9.4,1.55,boxstyle='round,pad=.1',fc='#F3F5FA',ec=c,lw=1.8))
        ax.text(.65,y-.05,title,fontsize=13,fontweight='bold',color=c)
        ax.text(.65,y-.65,txt,fontsize=10)
        if y>2:ax.add_patch(FancyArrowPatch((5,y-1.3),(5,y-1.65),arrowstyle='-|>',mutation_scale=15,color=INK))
    ax.set_title('B  Separate three effects',loc='left');fig.subplots_adjust(left=.03,right=.98,top=.90,bottom=.16,wspace=.18)
    finish(fig,'figure_1_design')
    # Figure 2: contour-body overlap. Do not equate this representation with recovered-grid DVH.
    fig,axes=plt.subplots(1,3,figsize=(12,4),sharey=True)
    for m,ax in enumerate(axes):
        for route,label,c in zip(ROUTES,LABELS,COLORS):
            rr=subset(rows,m,route)
            ax.scatter([float(r['geometry_reference_volume_mm3']) for r in rr],[float(r['contour_body_dice']) for r in rr],s=22,alpha=.8,color=c,label='HDSS contours' if route=='HDSS' else label,edgecolors='none')
        ax.set_xscale('log');ax.set(title=['GTV-only','1-mm PTV','2-mm PTV'][m],xlabel='Native binary volume (mm³)',ylim=(.55,1.015));clean(ax)
    axes[0].set_ylabel('Binary / contour-slab Dice')
    fig.legend(*axes[0].get_legend_handles_labels(),loc='lower center',ncol=4,frameon=False,fontsize=9)
    fig.subplots_adjust(left=.065,right=.985,top=.88,bottom=.26,wspace=.15);finish(fig,'figure_2_geometry')
    # Figure 3: every observed target, n and thresholds explicit.
    fig,axes=plt.subplots(1,3,figsize=(12,4.8),sharey=True)
    for m,ax in enumerate(axes):
        for j,(route,c) in enumerate(zip(ROUTES,COLORS)):
            rr=sorted(subset(rows,m,route),key=lambda r:r['target']);v=[float(r['delta_D98_Gy']) for r in rr]
            ax.scatter(j+np.linspace(-.16,.16,len(v)),v,s=15,color=c,zorder=3)
            ax.plot([j-.24,j+.24],[np.median(v)]*2,c=INK,lw=2)
            ax.text(j,2.0,str(len(v)),ha='center',fontsize=8)
        for y in [-1,-.5,0,.5,1]:ax.axhline(y,c='#64748B',lw=.7,ls='-' if y==0 else '--',alpha=.55)
        ymin=min(-3.3,min(float(r['delta_D98_Gy']) for r in rows)-.2)
        ax.set(xticks=range(7),xticklabels=LABELS,title=['GTV-only dose','1-mm plan dose','2-mm plan dose'][m],ylim=(ymin,2.2))
        ax.tick_params(axis='x',labelrotation=55,labelsize=8);clean(ax)
    axes[0].set_ylabel('Transferred − original D98 (Gy)')
    fig.subplots_adjust(left=.065,right=.985,top=.88,bottom=.30,wspace=.14);finish(fig,'figure_3_fixed_dose')
    # Figure 4: native curves retain original export order and staircase points.
    native=read('native_curves.json');common=read('ptv13_common_curves.json')
    metrics=load('native_metrics.csv');fig,axes=plt.subplots(1,3,figsize=(12,4.6))
    for arm,label,c in [('ElementsOriginal','Elements original',BLUE),('RayStationStandard','RayStation standard','#DB851B'),('EclipseHDSSHigh','Eclipse HDSS High',PURPLE)]:
        r=next(r for r in native[arm] if r['target']=='PTV13');axes[0].plot(r['dose_Gy'],r['volume_pct'],label=label,c=c,lw=1.8)
    rr=common['rows'];original=next(r for r in rr if r['arm_id']=='M01_HDSS')
    axes[1].plot(common['dose_Gy'],original['original_fixed'],c=BLUE,label='Original / recovered HDSS')
    for arm,label,c in [('M01_STD','Standard body','#DB851B'),('M01_04_Eclipse_HDSS_High','Eclipse HDSS High body',PURPLE)]:
        r=next(r for r in rr if r['arm_id']==arm);axes[1].plot(common['dose_Gy'],r['transferred_fixed'],label=label,c=c)
    for ax,title in zip(axes[:2],['A  PTV13: native TPS curves','B  PTV13: common evaluator']):
        ax.set(xlim=(18,22),ylim=(90,100.3),xlabel='Dose (Gy)',ylabel='Volume (%)',title=title);clean(ax)
        ax.legend(loc='upper center',bbox_to_anchor=(.5,-.2),fontsize=8,frameon=False)
    for arm,route,c,label in [('RayStationStandard','STD','#DB851B','RayStation standard'),('EclipseHDSSHigh','04_Eclipse_HDSS_High',PURPLE,'Eclipse HDSS High')]:
        for r in subset(rows,1,route):
            v=next(x for x in metrics if x['arm']==arm and x['target']==r['target'])
            axes[2].scatter(float(v['delta_D98_from_export_Gy']),float(r['delta_D98_Gy']),c=c,s=65 if r['target']=='PTV13' else 20,marker='*' if r['target']=='PTV13' else 'o',label=label if r['target']=='PTV01' else None)
    axes[2].plot([-1.8,.6],[-1.8,.6],ls='--',c='#AAA');axes[2].axhline(0,c='#AAA',lw=.7);axes[2].axvline(0,c='#AAA',lw=.7)
    axes[2].set(xlabel='Native ΔD98 versus Elements (Gy)',ylabel='Common fixed-dose ΔD98 (Gy)',title='C  All 24 matched PTVs / route')
    axes[2].legend(loc='upper center',bbox_to_anchor=(.5,-.2),fontsize=8,frameon=False);clean(axes[2])
    fig.subplots_adjust(left=.055,right=.99,top=.87,bottom=.32,wspace=.35);finish(fig,'figure_4_native_common')
    # Figure 5: all replans performed in Elements, four plans / 24 coupled targets each.
    replans=load('replanning.csv');fig,axes=plt.subplots(1,4,figsize=(12,4),sharey=True)
    plans=['M01_Standard','M01_EclipseHDSSHigh','M02_Standard','M02_EclipseHDSSHigh']
    for ax,plan,title in zip(axes,plans,['1 mm · Standard','1 mm · Eclipse H','2 mm · Standard','2 mm · Eclipse H']):
        rr=[r for r in replans if r['plan']==plan]
        for r in rr:
            base=float(r['original_D98_Gy']);y=[float(r['new_dose_planning_roi_D98_Gy'])-base,float(r['new_dose_original_roi_D98_Gy'])-base]
            ax.plot([0,1],y,c='#C6CBD5',lw=.6,zorder=1);ax.scatter([0,1],y,c=['#DB851B',PURPLE],s=17,zorder=2)
        ax.axhline(0,c=INK,lw=1);ax.set(xticks=[0,1],xticklabels=['Planning ROI','Original ROI'],title=title,xlim=(-.3,1.3));ax.tick_params(axis='x',labelrotation=20,labelsize=9);clean(ax)
    axes[0].set_ylabel('New-plan D98 − original-plan D98 (Gy)')
    fig.subplots_adjust(left=.065,right=.99,top=.87,bottom=.22,wspace=.16);finish(fig,'figure_5_replanning')
    # Supplementary MR-to-CT experiment, never pooled as 72 independent geometries.
    mr=load('mr_ct.csv');fig,axes=plt.subplots(1,3,figsize=(11,3.6),sharey=True)
    for m,ax in enumerate(axes):
        rr=[r for r in mr if int(r['dose_plan_margin_mm'])==m]
        ax.scatter([int(r['target'][3:]) for r in rr],[float(r['delta_D98_Gy']) for r in rr],c=BLUE,s=25)
        ax.axhline(0,c='#777',lw=.8);ax.set(title=f'Original dose: margin {m} mm',xlabel='Synthetic GTV number',xticks=[1,6,12,18,24]);clean(ax)
    axes[0].set_ylabel('After MR→CT − before D98 (Gy)');fig.tight_layout();finish(fig,'figure_S1_mr_ct')
    summary=[]
    for m in range(3):
        for route,label in zip(ROUTES,LABELS):
            rr=subset(rows,m,route);v=np.array([float(r['delta_D98_Gy']) for r in rr]);dice=[float(r['contour_body_dice']) for r in rr]
            summary.append(dict(margin_mm=m,route=label,n=len(v),median_contour_dice=float(np.median(dice)),
                median_delta_D98_Gy=float(np.median(v)),minimum_delta_D98_Gy=float(v.min()),maximum_delta_D98_Gy=float(v.max()),
                abs_delta_ge_0_5_Gy=int(sum(abs(v)>=.5)),abs_delta_ge_1_Gy=int(sum(abs(v)>=1))))
    write('table_2_fixed_dose_summary.csv',summary)
    write('table_1_design.csv',[dict(group=f'{v:g} mm3 nominal GTV',n=sum(float(r['analytic_volume_mm3'])==v for r in design),sphere=sum(float(r['analytic_volume_mm3'])==v and r['shape']=='sphere' for r in design),ellipsoid=sum(float(r['analytic_volume_mm3'])==v and r['shape']=='ellipsoid' for r in design),irregular=sum(float(r['analytic_volume_mm3'])==v and r['shape'] not in ['sphere','ellipsoid'] for r in design)) for v in [6.5,30,120]])
    print('Created five main figures, one MR-to-CT supplement and two editable CSV tables.')

if __name__=='__main__':main()
