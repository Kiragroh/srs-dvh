import numpy as np
import pytest
from scipy.optimize import brentq
from srs_dvh import DoseGrid,VoxelROI,ImplicitROI,DVH,calculate,converge


def sphere(radius=1.2,center=np.array([.13,-.27,.49])):
    return ImplicitROI(lambda p:np.sum((p-center)**2,axis=1)<=radius**2,center-radius,center+radius)


def test_full_voxel_volume_oblique_affine_and_linear_dose():
    t=np.deg2rad(33);rot=np.array([[np.cos(t),-np.sin(t),0],[np.sin(t),np.cos(t),0],[0,0,1]])
    aff=np.eye(4);aff[:3,:3]=rot@np.diag([.4,.4,.8]);aff[:3,3]=[2.13,-3.17,.49]
    roi=VoxelROI(np.ones((3,4,2)),aff)
    center=aff[:3,:3]@np.array([1,1.5,.5])+aff[:3,3]
    for h in [.2,.1,.05]:
        dvh=calculate(roi,lambda x:23+x[:,0]-2*x[:,1],h)
        assert abs(dvh.volume_mm3-3*4*2*.4*.4*.8)<1e-9
        assert abs(dvh.metrics()['Dmean_Gy']-(23+center[0]-2*center[1]))<1e-9


@pytest.mark.parametrize('volume',[6.5,30.,120.])
def test_small_sphere_radial_srs_dose_against_exact_distribution(volume):
    r=(3*volume/(4*np.pi))**(1/3);center=np.array([.13,-.27,.49]);roi=sphere(r,center)
    dvh=calculate(roi,lambda p:28-8*np.sum((p-center)**2,axis=1)/r**2,.025)
    m=dvh.metrics()
    assert abs(m['volume_mm3']/volume-1)<.003
    assert abs(m['Dmean_Gy']-23.2)<.02
    assert abs(m['D98_Gy']-(28-8*.98**(2/3)))<.025
    thresholds=np.linspace(20,28,81)
    exact=100*((28-thresholds)/8)**1.5
    assert np.max(abs(dvh.volume_at_dose(thresholds)-exact))<.35


def test_sphere_linear_gradient_has_known_cap_volume():
    r=1.2;center=np.array([.13,-.27,.49]);roi=sphere(r,center)
    dvh=calculate(roi,lambda p:23+4*(p[:,0]-center[0])/r,.02)
    t=brentq(lambda t:.5+.75*t-.25*t**3-.02,-1,1)
    assert abs(dvh.metrics()['D98_Gy']-(23+4*t))<.04
    assert abs(dvh.metrics()['V20_pct']-100*(1-(.5+.75*(-.75)-.25*(-.75)**3)))<.25


def test_rotated_dose_grid_preserves_linear_field_at_subvoxel_points():
    t=np.deg2rad(31);a=np.eye(4);a[:3,:3]=np.array([[np.cos(t),0,np.sin(t)],[0,1,0],[-np.sin(t),0,np.cos(t)]])@np.diag([.3,.7,.4]);a[:3,3]=[-3,-2,-1]
    ix=np.indices((12,13,14)).reshape(3,-1).T;xyz=ix@a[:3,:3].T+a[:3,3]
    dose=DoseGrid((25+xyz@np.array([.2,.3,-.5])).reshape((12,13,14)),a)
    q=np.array([[.13,2.77,4.49],[10.2,7.3,9.4]])@a[:3,:3].T+a[:3,3]
    assert np.allclose(dose.sample(q),25+q@np.array([.2,.3,-.5]),atol=1e-12)


def test_no_outside_dose_zero_padding():
    dose=DoseGrid(np.full((4,4,4),20.),np.eye(4))
    with pytest.raises(ValueError,match='outside'):dose.sample(np.array([[-.1,1,1]]))


def test_convergence_evidence_requires_two_refinements():
    roi=VoxelROI(np.ones((2,2,2)),np.eye(4))
    dvh,evidence=converge(roi,lambda x:np.full(len(x),20),steps=(.2,.1,.05))
    assert evidence['converged'] and len(evidence['refinements'])==3
    assert dvh.metrics()['D98_Gy']==20


def test_binary_roi_does_not_silently_threshold_fractional_masks():
    with pytest.raises(ValueError,match='binary'):VoxelROI(np.full((3,3,3),.6),np.eye(4))


def test_unequal_volume_weights_preserve_discontinuous_dose_distribution():
    dvh=DVH(np.array([10.,30.]),np.array([90.,10.]),.1)
    assert dvh.dose_at_volume(50)==10
    assert dvh.dose_at_volume(10)==30
    assert dvh.dose_at_volume(100)==10 and dvh.dose_at_volume(0)==30
    assert np.allclose(dvh.volume_at_dose([10,20,30,31]),[100,10,10,0])

def test_convergence_curve_check_includes_low_doses_outside_report_plot_range():
    roi=sphere()
    _,evidence=converge(roi,lambda p:5+2*p[:,0],steps=(.8,.4,.2),
                       dose_tolerance_Gy=100,volume_tolerance_pct=100,dvh_tolerance_pp=.001)
    assert not evidence['converged']
    assert all(r['max_curve_change_pp']>.001 for r in evidence['refinements'][1:])

def test_exact_curve_difference_detects_narrow_interval_between_plot_nodes():
    a=DVH(np.array([0.,20.,20.,40.]),np.ones(4),.1)
    b=DVH(np.array([0.,20.001,20.001,40.]),np.ones(4),.05)
    plotting_nodes=np.linspace(0,40,601)
    assert np.max(abs(a.volume_at_dose(plotting_nodes)-b.volume_at_dose(plotting_nodes)))==0
    assert a.max_curve_difference(b)==50
    assert b.max_curve_difference(a,chunk_size=2)==50
    for invalid in [0,-1,.5]:
        with pytest.raises(ValueError,match='positive integer'):a.max_curve_difference(b,chunk_size=invalid)
