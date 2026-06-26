import h5py
import numpy as np
import rasterio
from rasterio.transform import from_bounds
import xarray as xr
import glob

def hdf_to_geotiff(hdf_path, output_path, layer="DNB_NTL_ClimAdj"):
    with h5py.File(hdf_path, 'r') as f:
        data = f[f'HDFEOS/GRIDS/VNP_Grid_DNB/{layer}'][:]

        # Apply scale factor and fill value mask
        scale = f[f'HDFEOS/GRIDS/VNP_Grid_DNB/{layer}'].attrs.get('scale_factor', 1.0)
        fill = f[f'HDFEOS/GRIDS/VNP_Grid_DNB/{layer}'].attrs.get('_FillValue', 65535)

        data = data.astype(float)
        data[data == fill] = np.nan
        data = data * scale

    # Write GeoTIFF (approximate — extract precise bbox from HDF metadata)
    with rasterio.open(output_path, 'w', driver='GTiff',
                       height=data.shape[0], width=data.shape[1],
                       count=1, dtype='float32', crs='EPSG:4326') as dst:
        dst.write(data.astype('float32'), 1)

def apply_quality_mask(ntl_array, qf_array):
    # Apply QF_DNB quality flag layer to mask cloud-contaminated pixels
    # QF = 0 or 1 → valid; QF ≥ 2 → mask
    masked = ntl_array.copy()
    masked[qf_array >= 2] = np.nan
    return masked

def create_annual_median_composite(input_dir="data/processed/ntl_rasters/*.tif", output_path="data/processed/ntl_annual_median.tif"):
    # Stack monthly GeoTIFFs and compute annual median (robust to seasonal noise)
    tifs = sorted(glob.glob(input_dir))
    if not tifs:
        return
    arrays = [rasterio.open(f).read(1) for f in tifs]
    annual_median = np.nanmedian(np.stack(arrays), axis=0)

    # write it out
    with rasterio.open(tifs[0]) as src:
        meta = src.meta
    with rasterio.open(output_path, 'w', **meta) as dst:
        dst.write(annual_median.astype('float32'), 1)
