"""Compare three declared body/sampling methods in the same synthetic dose."""
import numpy as np
from srs_dvh import DoseGrid,VoxelROI,SurfaceROI,calculate,calculate_grid_centres

source_affine=np.diag([.4,.4,.4,1.]);source_affine[:3,3]=-2
indices=np.indices((11,11,11)).reshape(3,-1).T
points=indices*.4-2
mask=(np.sum(points**2,axis=1)<=1.15**2).reshape(11,11,11)
source=VoxelROI(mask,source_affine);surface=SurfaceROI.from_voxels(source)
dose_affine=np.diag([.3,.3,.3,1.]);dose_affine[:3,3]=-3
q=np.indices((21,21,21)).reshape(3,-1).T*.3-3
values=np.maximum(0,28-8*np.sum(q**2,axis=1)/1.15**2).reshape(21,21,21)
dose=DoseGrid(values,dose_affine)
for label,dvh in [('Full source voxels',calculate(source,dose,.05)),
                  ('Full reconstructed surface',calculate(surface,dose,.05)),
                  ('Surface at dose-grid centres',calculate_grid_centres(surface,dose))]:
    print(f'{label}: {dvh.volume_mm3:.4f} mm3; D98={dvh.dose_at_volume(98):.3f} Gy')
print('The input dose is unchanged. These results use different body/sampling definitions.')
