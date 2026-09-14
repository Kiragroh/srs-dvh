"""Analytic checks for surface reconstruction and discrete grid evaluation."""
import numpy as np
import pytest
from srs_dvh import DoseGrid, VoxelROI, calculate


def api():
    import srs_dvh
    assert hasattr(srs_dvh, 'SurfaceROI'), 'Missing explicit surface geometry adapter'
    assert hasattr(srs_dvh, 'calculate_grid_centres'), 'Missing discrete surface/grid evaluator'
    return srs_dvh.SurfaceROI, srs_dvh.calculate_grid_centres


def cube():
    vertices=np.array([[0,0,0],[2,0,0],[2,2,0],[0,2,0],[0,0,2],[2,0,2],[2,2,2],[0,2,2]],float)
    faces=np.array([[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,1,5],[0,5,4],
                    [1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]])
    return vertices,faces


def test_strict_grid_centres_differ_from_full_surface_volume():
    SurfaceROI,grid_dvh=api();surface=SurfaceROI(*cube())
    index=np.indices((5,5,5));dose=DoseGrid(index[0].astype(float),np.eye(4))
    discrete=grid_dvh(surface,dose)
    assert discrete.volume_mm3==1
    assert discrete.dose_at_volume(98)==1
    full=calculate(surface,dose,.1)
    assert full.volume_mm3==pytest.approx(8)
    assert full.metrics()['Dmean_Gy']==pytest.approx(1)


def test_grid_is_physical_and_has_no_hidden_half_voxel_shift():
    SurfaceROI,grid_dvh=api();vertices,faces=cube()
    angle=.41;rot=np.array([[np.cos(angle),-np.sin(angle),0],[np.sin(angle),np.cos(angle),0],[0,0,1]])
    affine=np.eye(4);affine[:3,:3]=rot;affine[:3,3]=[7,-8,12]
    surface=SurfaceROI(vertices@rot.T+affine[:3,3],faces)
    dose=DoseGrid(np.indices((5,5,5))[0].astype(float),affine)
    dvh=grid_dvh(surface,dose)
    assert dvh.volume_mm3==pytest.approx(1)
    assert dvh.dose_at_volume(98)==1


def test_single_voxel_surface_is_octahedron():
    SurfaceROI,_=api()
    mask=np.ones((1,1,1),bool);roi=VoxelROI(mask,np.eye(4))
    surface=SurfaceROI.from_voxels(roi)
    # Isosurface halfway to six exterior zero-valued neighbours.
    assert surface.mesh_volume_mm3==pytest.approx(1/6)
    assert surface.signed_distance(np.array([[0,0,0],[.6,0,0]])).tolist()==pytest.approx([-(1/12)**.5,.1])


def test_reject_open_surface_and_outside_grid():
    SurfaceROI,grid_dvh=api();vertices,faces=cube()
    with pytest.raises(ValueError,match='closed'):
        SurfaceROI(vertices,faces[:-1])
    surface=SurfaceROI(vertices-1,faces)
    with pytest.raises(ValueError,match='outside'):
        grid_dvh(surface,DoseGrid(np.zeros((5,5,5)),np.eye(4)))


def test_empty_discrete_support_is_explicit():
    SurfaceROI,grid_dvh=api();vertices,faces=cube()
    surface=SurfaceROI(vertices*.1+.2,faces)
    with pytest.raises(ValueError,match='No interior'):
        grid_dvh(surface,DoseGrid(np.zeros((5,5,5)),np.eye(4)))


def test_available_grid_requires_explicit_partial_coverage_choice():
    SurfaceROI,grid_dvh=api();vertices,faces=cube()
    surface=SurfaceROI(vertices-.25,faces)
    dose=DoseGrid(np.indices((3,3,3))[0].astype(float),np.eye(4))
    with pytest.raises(ValueError,match='outside'):grid_dvh(surface,dose)
    dvh=grid_dvh(surface,dose,coverage='available_grid')
    assert dvh.volume_mm3==8
    assert dvh.metrics()['Dmean_Gy']==.5


def test_nested_shell_keeps_the_cavity_empty():
    SurfaceROI,_=api();outer,faces=cube()
    inner=outer*.5+.5
    shell=SurfaceROI(np.vstack([outer,inner]),np.vstack([faces,faces[:,::-1]+8]))
    signs=shell.signed_distance(np.array([[1,1,1],[.25,1,1],[3,1,1]]))
    assert signs[0]>0 and signs[1]<0 and signs[2]>0
    assert shell.mesh_volume_mm3==pytest.approx(7)
    dose=DoseGrid(np.indices((5,5,5))[0].astype(float),np.eye(4))
    integrated=calculate(shell,dose,.1)
    assert integrated.volume_mm3==pytest.approx(7)
    assert integrated.metrics()['Dmean_Gy']==pytest.approx(1)
