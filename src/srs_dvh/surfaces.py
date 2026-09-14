"""Explicit surfaces and a separate discrete dose-grid-centre DVH method.

This module does not infer a proprietary surface or DVH algorithm. Caller
affines map array indices to physical voxel centres; no hidden shifts apply.
"""
import numpy as np
from .core import DVH, DoseGrid, VoxelROI


class SurfaceROI:
    """Closed, consistently wound triangles; cavity shells face into cavities.

    Global inward winding is reversed as a whole, preserving the relationship
    between exterior and cavity shells. Self-intersecting surfaces are outside
    this adapter's supported input contract.
    """
    def __init__(self, vertices, faces):
        import vtk
        from vtk.util.numpy_support import numpy_to_vtk, numpy_to_vtkIdTypeArray
        self.vertices=np.asarray(vertices,float)
        faces=np.asarray(faces)
        if self.vertices.ndim!=2 or self.vertices.shape[1]!=3 or not np.isfinite(self.vertices).all():
            raise ValueError('Finite physical 3D vertices required')
        if faces.ndim!=2 or faces.shape[1]!=3 or not np.issubdtype(faces.dtype,np.integer) or not len(faces):
            raise ValueError('Nonempty integer triangle connectivity required')
        if faces.min()<0 or faces.max()>=len(self.vertices):raise ValueError('Triangle index outside vertices')
        faces=faces.astype(np.int64,copy=True)
        centered=self.vertices-self.vertices.mean(0)
        signed_volume=np.einsum('ij,ij->i',centered[faces[:,0]],np.cross(centered[faces[:,1]],centered[faces[:,2]])).sum()/6
        if signed_volume<0:faces=faces[:,::-1].copy()
        points=vtk.vtkPoints();points.SetData(numpy_to_vtk(self.vertices,deep=True))
        cells=vtk.vtkCellArray()
        cells.SetData(numpy_to_vtkIdTypeArray(np.arange(len(faces)+1,dtype=np.int64)*3,deep=True),
                      numpy_to_vtkIdTypeArray(faces.ravel(),deep=True))
        poly=vtk.vtkPolyData();poly.SetPoints(points);poly.SetPolys(cells)
        edges=vtk.vtkFeatureEdges();edges.SetInputData(poly)
        edges.BoundaryEdgesOn();edges.NonManifoldEdgesOn();edges.FeatureEdgesOff();edges.ManifoldEdgesOff();edges.Update()
        if edges.GetOutput().GetNumberOfCells():raise ValueError('A closed manifold triangle surface is required')
        normals=vtk.vtkPolyDataNormals();normals.SetInputData(poly)
        normals.SplittingOff();normals.AutoOrientNormalsOff();normals.ConsistencyOn();normals.Update()
        self.poly=normals.GetOutput()
        self._distance=vtk.vtkImplicitPolyDataDistance();self._distance.SetInput(self.poly)
        mass=vtk.vtkMassProperties();mass.SetInputData(self.poly);mass.Update()
        self.mesh_volume_mm3=float(mass.GetVolume())
        if self.mesh_volume_mm3<=0:raise ValueError('Nonzero enclosed surface volume required')

    @classmethod
    def from_voxels(cls, roi):
        """Unsmoothed Lewiner marching-cubes isosurface at binary level 0.5.

        Empty padding closes boundaries even for tightly cropped source masks.
        The resulting surface is a declared reconstruction, not the full union
        of source voxels and not a universally inferred native TPS surface.
        """
        from skimage.measure import marching_cubes
        if not isinstance(roi,VoxelROI):raise TypeError('VoxelROI required')
        vertices,faces,*_=marching_cubes(np.pad(roi.mask.astype(np.float32),1),.5)
        vertices=(vertices-1)@roi.affine[:3,:3].T+roi.affine[:3,3]
        return cls(vertices,faces)

    def signed_distance(self, points):
        points=np.asarray(points,float)
        if points.ndim!=2 or points.shape[1]!=3 or not np.isfinite(points).all():
            raise ValueError('Finite 3D query points required')
        return np.array([self._distance.EvaluateFunction(p) for p in points])

    def quadrature(self, step_mm, max_points=250000):
        """Full interior midpoint integration; independent of dose-grid centres."""
        import vtk
        from vtk.util.numpy_support import vtk_to_numpy
        if not np.isfinite(step_mm) or step_mm<=0:raise ValueError('Positive integration spacing required')
        lo=self.vertices.min(0);hi=self.vertices.max(0)
        n=np.ceil((hi-lo)/step_mm).astype(int)
        if np.any(n<1) or np.prod(n,dtype=float)>100_000_000:raise ValueError('Surface integration grid is empty or too large')
        spacing=(hi-lo)/n;origin=lo+spacing/2
        stencil=vtk.vtkPolyDataToImageStencil();stencil.SetInputData(self.poly)
        stencil.SetOutputOrigin(*origin);stencil.SetOutputSpacing(*spacing)
        stencil.SetOutputWholeExtent(0,int(n[0])-1,0,int(n[1])-1,0,int(n[2])-1)
        stencil.SetTolerance(0);stencil.Update()
        image=vtk.vtkImageStencilToImage();image.SetInputConnection(stencil.GetOutputPort())
        image.SetInsideValue(1);image.SetOutsideValue(0);image.SetOutputScalarTypeToUnsignedChar();image.Update()
        mask=vtk_to_numpy(image.GetOutput().GetPointData().GetScalars()).reshape(tuple(n[::-1]))
        indices=np.argwhere(mask)[:,::-1];weight=float(np.prod(spacing))
        for start in range(0,len(indices),max_points):
            points=indices[start:start+max_points]*spacing+origin
            yield points,np.full(len(points),weight)


def calculate_grid_centres(surface, dose, *, boundary_tolerance_mm=1e-6, coverage='require_surface'):
    """Count only dose-grid centres strictly inside a supplied closed surface.

    Each retained centre receives one full dose-cell volume. This is a discrete
    alternative to full-volume integration: boundary cells are not fractionally
    weighted. The returned volume is sampled volume, not mesh volume. No dose
    interpolation, target-specific fitting or coordinate adaptation occurs here.
    By default the dose grid must enclose the entire surface. The explicit
    `coverage='available_grid'` option evaluates only the supplied grid domain;
    it does not certify full-target coverage and does not extrapolate dose.
    """
    if not isinstance(surface,SurfaceROI) or not isinstance(dose,DoseGrid):
        raise TypeError('SurfaceROI and DoseGrid required')
    if not np.isfinite(boundary_tolerance_mm) or boundary_tolerance_mm<0:
        raise ValueError('Nonnegative boundary tolerance required')
    if coverage not in {'require_surface','available_grid'}:raise ValueError('Unknown coverage policy')
    q=surface.vertices@dose.inverse[:3,:3].T+dose.inverse[:3,3]
    end=np.array(dose.values.shape)-1
    if coverage=='require_surface' and (np.any(q<-1e-7) or np.any(q>end+1e-7)):
        raise ValueError('Surface extends outside supplied dose grid')
    lo=np.maximum(0,np.floor(q.min(0)-1)).astype(int)
    hi=np.minimum(dose.values.shape,np.ceil(q.max(0)+2)).astype(int)
    if np.any(hi<=lo):raise ValueError('No interior dose-grid centres resolved in this surface')
    count=int(np.prod(hi-lo));values=[]
    for start in range(0,count,250000):
        ix=np.column_stack(np.unravel_index(np.arange(start,min(start+250000,count)),hi-lo))+lo
        world=ix@dose.affine[:3,:3].T+dose.affine[:3,3]
        keep=surface.signed_distance(world)<-boundary_tolerance_mm
        if keep.any():values.append(dose.values[tuple(ix[keep].T)].astype(float))
    if not values:raise ValueError('No interior dose-grid centres resolved in this surface')
    values=np.concatenate(values);weight=float(abs(np.linalg.det(dose.affine[:3,:3])))
    return DVH(values,np.full(len(values),weight),float(np.linalg.norm(dose.affine[:3,:3],axis=0).max()))
