"""Exact-area polygon prisms on parallel, possibly oblique source planes.

Each polygon occupies an explicitly supplied slab interval. No CT-plane
resampling or interpolation between successive contour shapes is implied.
"""
from dataclasses import dataclass
import numpy as np
import shapely

@dataclass
class PolygonSlabROI:
    polygons: list
    intervals_mm: np.ndarray
    origin_mm: np.ndarray
    basis: np.ndarray

    def __post_init__(self):
        self.intervals_mm=np.asarray(self.intervals_mm,float)
        self.origin_mm=np.asarray(self.origin_mm,float)
        self.basis=np.asarray(self.basis,float)
        if self.basis.shape!=(3,3) or not np.isfinite(self.basis).all() or not np.allclose(self.basis.T@self.basis,np.eye(3),atol=1e-8):
            raise ValueError('An orthonormal physical source-plane basis is required')
        if self.origin_mm.shape!=(3,) or not np.isfinite(self.origin_mm).all():raise ValueError('Finite physical origin required')
        n=len(self.polygons)
        if not n or self.intervals_mm.shape!=(n,2) or not np.isfinite(self.intervals_mm).all() or np.any(np.diff(self.intervals_mm,axis=1)<=0):
            raise ValueError('One finite positive slab interval per polygon required')
        order=np.argsort(self.intervals_mm[:,0]);ends=self.intervals_mm[order]
        if np.any(ends[1:,0]<ends[:-1,1]-1e-8):raise ValueError('Overlapping slab intervals are ambiguous')
        for poly in self.polygons:
            if poly.geom_type not in ('Polygon','MultiPolygon') or not poly.is_valid or poly.is_empty or poly.area<=0:
                raise ValueError('Valid nonempty polygon geometry required')
        self.volume_mm3=float(sum(poly.area*(b-a) for poly,(a,b) in zip(self.polygons,self.intervals_mm)))

    def quadrature(self,step_mm,max_points=250000):
        if step_mm<=0:raise ValueError('Positive integration spacing required')
        for poly,(z0,z1) in zip(self.polygons,self.intervals_mm):
            x0,y0,x1,y1=poly.bounds
            nx=max(1,int(np.ceil((x1-x0)/step_mm)));ny=max(1,int(np.ceil((y1-y0)/step_mm)))
            dx=(x1-x0)/nx;dy=(y1-y0)/ny
            x,y=np.meshgrid(x0+np.arange(nx)*dx,y0+np.arange(ny)*dy,indexing='ij')
            cells=shapely.box(x.ravel(),y.ravel(),x.ravel()+dx,y.ravel()+dy)
            clipped=shapely.intersection(cells,poly);areas=shapely.area(clipped)
            good=areas>1e-18;clipped=clipped[good];areas=areas[good];centers=shapely.centroid(clipped)
            # A cell containing a hole or disconnected fragments can have its
            # centroid outside the ROI. Preserve its area using constrained
            # triangles, whose positive-weight centroids remain inside it.
            inside=shapely.covers(clipped,centers)
            if not inside.all():
                triangles=shapely.get_parts(shapely.constrained_delaunay_triangles(clipped[~inside]))
                areas=np.r_[areas[inside],shapely.area(triangles)]
                centers=np.r_[centers[inside],shapely.centroid(triangles)]
            xy=np.column_stack([shapely.get_x(centers),shapely.get_y(centers)])
            nz=max(1,int(np.ceil((z1-z0)/step_mm)));dz=(z1-z0)/nz
            z=z0+(np.arange(nz)+.5)*dz
            block=max(1,max_points//nz)
            for i in range(0,len(xy),block):
                coords=xy[i:i+block];a=areas[i:i+block]
                q=np.column_stack([np.repeat(coords,nz,axis=0),np.tile(z,len(coords))])
                yield q@self.basis.T+self.origin_mm,np.repeat(a*dz,nz)
