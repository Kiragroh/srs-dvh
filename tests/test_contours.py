import numpy as np
import pytest
from shapely.geometry import Polygon,box
from srs_dvh import calculate
from srs_dvh.contours import PolygonSlabROI
import shapely

@pytest.mark.parametrize('angle',[0,30])
def test_oblique_subpixel_polygon_caps_keep_exact_volume_and_linear_mean(angle):
    a=np.deg2rad(angle);b=np.array([[1,0,0],[0,np.cos(a),-np.sin(a)],[0,np.sin(a),np.cos(a)]])
    polygons=[Polygon([(0,0),(1.27,0),(.03,.81)]),box(.101,.211,.106,.218)]
    intervals=np.array([[-.2,.2],[.2,.6]])
    roi=PolygonSlabROI(polygons,intervals,np.array([4,-3,2]),b)
    volume=sum(p.area*.4 for p in polygons)
    centroid=sum(p.area*.4*(np.array([p.centroid.x,p.centroid.y,z.mean()])@b.T+roi.origin_mm) for p,z in zip(polygons,intervals))/volume
    for h in [.2,.1,.05]:
        d=calculate(roi,lambda p:23+p@np.array([.3,-.2,.5]),h)
        assert abs(d.volume_mm3-volume)<1e-11
        assert abs(d.metrics()['Dmean_Gy']-(23+centroid@np.array([.3,-.2,.5])))<1e-11

def test_hole_is_not_filled_and_prism_dvh_converges_to_uniform_gradient():
    polygon=box(-1,-1,1,1).difference(box(-.4,-.4,.4,.4))
    roi=PolygonSlabROI([polygon],[[-.5,.5]],np.zeros(3),np.eye(3))
    d=calculate(roi,lambda p:20+8*p[:,2],.01)
    assert abs(d.volume_mm3-polygon.area)<1e-8
    assert abs(d.dose_at_volume(98)-16.16)<.041
    assert abs(d.metrics()['V20_pct']-50)<1e-8

def test_contour_intervals_cannot_overlap():
    with pytest.raises(ValueError,match='Overlapping'):
        PolygonSlabROI([box(0,0,1,1)]*2,[[0,1],[.5,1.5]],np.zeros(3),np.eye(3))

def test_coarse_cell_with_hole_keeps_all_positive_quadrature_points_inside():
    polygon=box(-1,-1,1,1).difference(box(-.9,-.9,.9,.9))
    roi=PolygonSlabROI([polygon],[[-.2,.2]],np.zeros(3),np.eye(3))
    volume=0
    for pts,w in roi.quadrature(4):
        assert shapely.covers(polygon,shapely.points(pts[:,:2])).all()
        assert (w>0).all();volume+=w.sum()
    assert abs(volume-polygon.area*.4)<1e-12

def test_oblique_annulus_quadratic_dose_agrees_with_known_dvh_and_refines():
    from shapely.geometry import Point
    a=.35;r=1.;angle=np.deg2rad(30)
    basis=np.array([[1,0,0],[0,np.cos(angle),-np.sin(angle)],[0,np.sin(angle),np.cos(angle)]])
    polygon=Point(0,0).buffer(r,quad_segs=1024).difference(Point(0,0).buffer(a,quad_segs=1024))
    origin=np.array([.13,-.27,.49]);roi=PolygonSlabROI([polygon],[[-.1,.1]],origin,basis)
    def dose(p):
        q=(p-origin)@basis
        return 28-8*(q[:,0]**2+q[:,1]**2-a*a)/(r*r-a*a)
    metrics=[]
    for h in [.08,.04,.02,.01,.005]:
        d=calculate(roi,dose,h);metrics.append(dict(**d.metrics(),V24_pct=float(d.volume_at_dose(24))))
    final=metrics[-1]
    assert abs(final['D98_Gy']-20.16)<.025
    assert abs(final['Dmean_Gy']-24)<.003
    assert abs(final['volume_mm3']-(np.pi*(r*r-a*a)*.2))<2e-6
    assert abs(final['V20_pct']-100)<1e-8
    assert abs(final['V24_pct']-50)<.1
    # Coarse midpoint quadrature is deliberately not accepted as converged.
    assert abs(metrics[0]['D98_Gy']-metrics[1]['D98_Gy'])>.025
    for prev,nxt in zip(metrics[-3:],metrics[-2:]):
        assert abs(prev['D98_Gy']-nxt['D98_Gy'])<.025
        assert abs(prev['Dmean_Gy']-nxt['Dmean_Gy'])<.025
        assert abs(prev['V20_pct']-nxt['V20_pct'])<.25
        assert abs(prev['V24_pct']-nxt['V24_pct'])<.25
