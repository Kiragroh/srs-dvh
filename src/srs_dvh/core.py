"""Volume-weighted DVH integration in physical millimetres and Gy.

Dose interpolation, ROI representation and integration spacing are independent.
Affines map array indices to voxel CENTRES. Geometry is never moved to match a
reference curve. Finer quadrature cannot recover a coarse input dose field.
"""
from dataclasses import dataclass
from typing import Callable
import itertools
import numpy as np
from scipy.ndimage import map_coordinates


def _affine(value):
    a=np.array(value,dtype=float,copy=True)
    if a.shape!=(4,4) or not np.isfinite(a).all() or not np.allclose(a[3],[0,0,0,1]):
        raise ValueError('A finite 4x4 physical-space affine is required')
    if abs(np.linalg.det(a[:3,:3]))<1e-12:raise ValueError('Singular affine')
    return a


@dataclass
class DoseGrid:
    values: np.ndarray
    affine: np.ndarray

    def __post_init__(self):
        self.values=np.asarray(self.values)
        self.affine=_affine(self.affine);self.inverse=np.linalg.inv(self.affine)
        if self.values.ndim!=3 or min(self.values.shape)<2 or not np.isfinite(self.values).all():
            raise ValueError('A finite three-dimensional dose grid is required')

    def sample(self,points):
        q=np.asarray(points)@self.inverse[:3,:3].T+self.inverse[:3,3]
        end=np.array(self.values.shape)-1
        if np.any(q < -1e-7) or np.any(q>end+1e-7):
            raise ValueError('ROI extends outside the supplied dose grid; no zero padding or extrapolation')
        q=np.clip(q,0,end)
        return map_coordinates(self.values.astype(float,copy=False),q.T,order=1,mode='constant',cval=np.nan,prefilter=False)


@dataclass
class VoxelROI:
    mask: np.ndarray
    affine: np.ndarray

    def __post_init__(self):
        self.mask=np.asarray(self.mask)
        self.affine=_affine(self.affine)
        if self.mask.ndim!=3 or not np.isin(self.mask,[0,1]).all():
            raise ValueError('Explicit binary ROI required; fractional masks need a specified model')
        self.mask=self.mask.astype(bool)
        self.volume_mm3=float(self.mask.sum()*abs(np.linalg.det(self.affine[:3,:3])))
        if self.volume_mm3<=0:raise ValueError('Empty ROI')

    def quadrature(self,step_mm,max_points=250000):
        """Subdivide complete occupied voxels, including their outer half-voxel."""
        if step_mm<=0:raise ValueError('Positive integration spacing required')
        n=np.maximum(1,np.ceil(np.linalg.norm(self.affine[:3,:3],axis=0)/step_mm-1e-7).astype(int))
        offsets=np.array(list(itertools.product(*[(np.arange(v)+.5)/v-.5 for v in n])))
        indices=np.argwhere(self.mask);block=max(1,max_points//len(offsets))
        weight=abs(np.linalg.det(self.affine[:3,:3]))/len(offsets)
        for start in range(0,len(indices),block):
            q=(indices[start:start+block,None,:]+offsets[None,:,:]).reshape(-1,3)
            points=q@self.affine[:3,:3].T+self.affine[:3,3]
            yield points,np.full(len(points),weight)


@dataclass
class ImplicitROI:
    contains: Callable
    lower_mm: np.ndarray
    upper_mm: np.ndarray

    def quadrature(self,step_mm,max_points=250000):
        """Independent midpoint quadrature for analytically specified test bodies."""
        lo=np.asarray(self.lower_mm,float);hi=np.asarray(self.upper_mm,float)
        if step_mm<=0 or lo.shape!=(3,) or hi.shape!=(3,) or not np.all(hi>lo):
            raise ValueError('Positive step and a nonempty 3D bounding box required')
        n=np.ceil((hi-lo)/step_mm).astype(int);delta=(hi-lo)/n
        axes=[lo[i]+(np.arange(n[i])+.5)*delta[i] for i in range(3)]
        yz=np.array(list(itertools.product(axes[1],axes[2])))
        block=max(1,max_points//len(yz));weight=float(np.prod(delta))
        for start in range(0,n[0],block):
            x=axes[0][start:start+block]
            pts=np.column_stack([np.repeat(x,len(yz)),np.tile(yz,(len(x),1))])
            keep=np.asarray(self.contains(pts),bool)
            if keep.shape!=(len(pts),):raise ValueError('ROI predicate must return one boolean per point')
            if keep.any():yield pts[keep],np.full(int(keep.sum()),weight)


@dataclass
class DVH:
    dose_Gy: np.ndarray
    weights_mm3: np.ndarray
    step_mm: float

    def __post_init__(self):
        d=np.asarray(self.dose_Gy,float);w=np.asarray(self.weights_mm3,float)
        if d.ndim!=1 or d.shape!=w.shape or not len(d) or not np.isfinite(d).all() or not np.isfinite(w).all() or np.any(w<=0):
            raise ValueError('Finite dose samples with strictly positive volume weights required')
        order=np.argsort(d);self.dose_Gy=d[order];self.weights_mm3=w[order]
        self.cumulative_mm3=np.cumsum(self.weights_mm3,dtype=float)
        self.volume_mm3=float(self.cumulative_mm3[-1])

    def dose_at_volume(self,volume_percent):
        if not 0<=volume_percent<=100:raise ValueError('Volume percentage outside 0..100')
        # Highest sampled dose received by at least the requested volume.
        # Do not interpolate across two unequal volume weights: doing so would
        # invent intermediate dose values and distort discontinuous fields.
        target=(1-volume_percent/100)*self.volume_mm3
        index=min(int(np.searchsorted(self.cumulative_mm3,target,side='right')),len(self.dose_Gy)-1)
        return float(self.dose_Gy[index])

    def volume_at_dose(self,thresholds_Gy):
        thresholds=np.asarray(thresholds_Gy)
        idx=np.searchsorted(self.dose_Gy,thresholds,side='left')
        below=np.where(idx>0,self.cumulative_mm3[np.maximum(idx-1,0)],0.)
        return np.clip(100*(1-below/self.volume_mm3),0,100)

    def max_curve_difference(self,other,chunk_size=250000):
        """Exact supremum between two empirical weighted cumulative DVHs.

        Every jump lies at an observed dose. Evaluating both sets of dose
        thresholds includes both sides of every constant interval, without
        missing narrow intervals between plotting nodes.
        """
        if not isinstance(chunk_size,(int,np.integer)) or chunk_size<1:
            raise ValueError('A positive integer chunk size is required')
        maximum=0.
        for source in [self,other]:
            for start in range(0,len(source.dose_Gy),chunk_size):
                thresholds=source.dose_Gy[start:start+chunk_size]
                difference=np.abs(self.volume_at_dose(thresholds)-other.volume_at_dose(thresholds))
                maximum=max(maximum,float(difference.max()))
        return maximum

    def metrics(self):
        return dict(volume_mm3=self.volume_mm3,D98_Gy=self.dose_at_volume(98),
                    D98_5_Gy=self.dose_at_volume(98.5),D95_Gy=self.dose_at_volume(95),
                    D2_Gy=self.dose_at_volume(2),Dmean_Gy=float(np.dot(self.dose_Gy,self.weights_mm3)/self.volume_mm3),
                    V20_pct=float(self.volume_at_dose(20)),samples=len(self.dose_Gy),integration_step_mm=self.step_mm)


def calculate(roi,dose,step_mm=.05):
    values=[];weights=[]
    sample=dose.sample if isinstance(dose,DoseGrid) else dose
    for points,w in roi.quadrature(step_mm):
        values.append(np.asarray(sample(points),float));weights.append(w)
    if not values:raise ValueError('No ROI volume resolved at this integration spacing')
    return DVH(np.concatenate(values),np.concatenate(weights),step_mm)


def converge(roi,dose,steps=(.2,.1,.05,.025),dose_tolerance_Gy=.02,volume_tolerance_pct=.2,dvh_tolerance_pp=.25):
    """Require two successive stable refinements; return evidence with the DVH.

    This tests integration stability on the supplied representations. It does
    not certify the accuracy of an input dose grid, segmentation or TPS match.
    """
    if len(steps)<3 or any(b>=a for a,b in zip(steps,steps[1:])):raise ValueError('At least three decreasing spacings required')
    records=[];previous=None;stable=0
    for h in steps:
        dvh=calculate(roi,dose,h);m=dvh.metrics();row=dict(m)
        if previous is not None:
            old=previous.metrics()
            dd=max(abs(m[k]-old[k]) for k in ['D98_Gy','D98_5_Gy','D95_Gy','D2_Gy','Dmean_Gy'])
            dv=100*abs(m['volume_mm3']/old['volume_mm3']-1)
            dc=dvh.max_curve_difference(previous)
            ok=dd<=dose_tolerance_Gy and dv<=volume_tolerance_pct and dc<=dvh_tolerance_pp
            stable=stable+1 if ok else 0
            row.update(max_metric_change_Gy=dd,volume_change_pct=dv,max_curve_change_pp=dc,step_stable=ok)
        records.append(row);previous=dvh
        if stable>=2:break
    return dvh,dict(converged=stable>=2,scope='Numerical integration on the supplied dose and geometry',
                    curve_scope='Exact empirical curve difference over the full sampled dose range',
                    dose_tolerance_Gy=dose_tolerance_Gy,volume_tolerance_pct=volume_tolerance_pct,
                    dvh_tolerance_pp=dvh_tolerance_pp,refinements=records)
