import h5py
import numpy as np
import rasterio
import glob
import os
import earthaccess
from typing import Optional, List

def authenticate_earthdata(strategy: str = "netrc") -> bool:
    """
    Authenticates with NASA Earthdata.

    Args:
        strategy: Authentication strategy (default: 'netrc')

    Returns:
        bool: True if authenticated successfully, False otherwise.
    """
    try:
        earthaccess.login(strategy=strategy)
        return True
    except Exception as e:
        print(f"Earthdata authentication failed: {e}")
        return False

def download_ntl_data(start_date: str, end_date: str, output_dir: str, bounding_box: tuple = (-180, -90, 180, 90)) -> None:
    """
    Downloads VNP46A3 data using earthaccess. Returns gracefully without synthetic data if auth fails.

    Args:
        start_date: Start date e.g. "2019-01"
        end_date: End date e.g. "2023-12"
        output_dir: Directory to save downloaded files.
        bounding_box: Tuple of (min_lon, min_lat, max_lon, max_lat).
    """
    if not authenticate_earthdata():
        print("Skipping download due to missing credentials.")
        return

    try:
        results = earthaccess.search_data(
            short_name="VNP46A3",
            version="2",
            temporal=(start_date, end_date),
            bounding_box=bounding_box
        )
        earthaccess.download(results, local_path=output_dir)
    except Exception as e:
        print(f"Error downloading data: {e}")

def hdf_to_geotiff(hdf_path: str, output_path: str, layer: str = "DNB_NTL_ClimAdj") -> None:
    """
    Converts a single HDF-EOS5 file to GeoTIFF format.

    Args:
        hdf_path: Input path to HDF5 file.
        output_path: Output path for GeoTIFF.
        layer: NTL layer to extract.
    """
    if not os.path.exists(hdf_path):
        print(f"File {hdf_path} not found.")
        return

    try:
        with h5py.File(hdf_path, 'r') as f:
            data = f[f'HDFEOS/GRIDS/VNP_Grid_DNB/{layer}'][:]

            scale = f[f'HDFEOS/GRIDS/VNP_Grid_DNB/{layer}'].attrs.get('scale_factor', 1.0)
            fill = f[f'HDFEOS/GRIDS/VNP_Grid_DNB/{layer}'].attrs.get('_FillValue', 65535)

            data = data.astype(float)
            data[data == fill] = np.nan
            data = data * scale

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with rasterio.open(output_path, 'w', driver='GTiff',
                           height=data.shape[0], width=data.shape[1],
                           count=1, dtype='float32', crs='EPSG:4326') as dst:
            dst.write(data.astype('float32'), 1)
    except Exception as e:
        print(f"Failed to convert {hdf_path}: {e}")

def apply_quality_mask(ntl_array: np.ndarray, qf_array: np.ndarray) -> np.ndarray:
    """
    Applies quality flag mask to NTL data.

    Args:
        ntl_array: NTL radiance array.
        qf_array: Quality flag array.

    Returns:
        np.ndarray: Masked NTL array.
    """
    masked = ntl_array.copy()
    masked[qf_array >= 2] = np.nan
    return masked

def create_annual_median(tif_dir: str, output_path: str) -> Optional[np.ndarray]:
    """
    Creates an annual median composite from monthly GeoTIFFs.

    Args:
        tif_dir: Directory containing input GeoTIFFs.
        output_path: Output path for the composite GeoTIFF.

    Returns:
        Optional[np.ndarray]: Annual median array, or None if no input files.
    """
    tifs = sorted(glob.glob(os.path.join(tif_dir, "*.tif")))
    if not tifs:
        print(f"No GeoTIFFs found in {tif_dir}.")
        return None

    try:
        arrays = []
        profile = None
        for f in tifs:
            with rasterio.open(f) as src:
                arrays.append(src.read(1))
                if profile is None:
                    profile = src.profile

        annual_median = np.nanmedian(np.stack(arrays), axis=0)

        if profile is not None:
            with rasterio.open(output_path, 'w', **profile) as dst:
                dst.write(annual_median.astype(profile['dtype']), 1)

        return annual_median
    except Exception as e:
        print(f"Failed to create annual median: {e}")
        return None
