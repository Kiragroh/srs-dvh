"""Reproduce an optional-resampling coordinate check; no patient data.

Optional dependencies: dicompyler-core==0.5.6, pydicom, scikit-image.
This diagnostic documents the installed library, without patching it.
"""
import json
import numpy as np
import pydicom.dicomio
from scipy.ndimage import map_coordinates
if not hasattr(pydicom.dicomio, 'read_file'):
    pydicom.dicomio.read_file=pydicom.dcmread
import dicompylercore
from dicompylercore import dvhcalc

def main():
    class Ramp:
        ds=type('Dataset',(),dict(PixelSpacing=[1.,1.]))()
        def GetDoseGrid(self,z):
            y,x=np.indices((12,12));return 10.+x+2*y
    lut=dvhcalc.get_resampled_lut([2,2,9,9],[2,2,9,9],.125,[1.,1.])
    x,y=np.meshgrid(*lut)
    actual=dvhcalc.get_interpolated_dose(Ramp(),0,.125,[2,2,9,9])
    expected=10+x+2*y;inside=(x>3)&(x<8)&(y>3)&(y<8)
    direct=map_coordinates(Ramp().GetDoseGrid(0),np.vstack([y.ravel(),x.ravel()]),order=1).reshape(x.shape)
    assert abs(direct-expected).max()<1e-12
    result=dict(version=dicompylercore.__version__,requested_spacing_mm=.125,
        reported_spacing_mm=float(lut[0][1]-lut[0][0]),
        library_mean_error_Gy=float((actual-expected)[inside].mean()),
        library_max_abs_error_Gy=float(abs(actual-expected)[inside].max()),
        direct_max_abs_error_Gy=float(abs(direct-expected).max()))
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
