# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 11:26:13 2024

@author: ANTHI182
"""

import rasterio
import pyproj
import numpy as np

def get_raster_hist(raster_file, bins=10, band=1):
    """
    Create a histogram for a raster

    Parameters
    ----------
    raster_file : String or Pathlib path
        Path to the raster
    bins : Int or array of float
        Edges of the bins to construct the histogram.The default is 10.
    band : Int, optional
        Band of the raster that should be used. The default is 1.

    Returns
    -------
    bin_counts : array
        Number of occurence for the corresponding bin
    bin_egdes : array
        Edges of the histogram bins
    """

    src = rasterio.open(raster_file)
    data = src.read(band)
    bin_counts, bin_egdes = np.histogram(data, bins=bins)
    return bin_counts, bin_egdes


def wgs84_degrees_to_meter(latitude, longitude):
    """
    Convert decimal degrees or degrees-minute-seconds coordinates to meter
    coordinates.

    Parameters
    ----------
    latitude : float <degrees.decimal> or tuple <(degrees, minute, sec)>
    longitude : float <degrees.decimal> or tuple <(degrees, minute, sec)>

    Returns
    -------
    x_meter : float
        longitude in meters in WGS84 / World Mercator (EPSG:3395)
    y_meter : TYPE
        latitude in meters in WGS84 / World Mercator (EPSG:3395)
    """

    if isinstance(latitude, tuple):
        # Convert DMS to Decimal Degrees
        latitude = latitude[0] + latitude[1]/60 + latitude[2]/3600
        longitude = longitude[0] + longitude[1]/60 + longitude[2]/3600

    # Define WGS84 and Projected Coordinate System (e.g., WGS Transverse Mercator)
    wgs84 = pyproj.Proj(init='epsg:4326')  # WGS84 datum
    proj = pyproj.Proj(init='epsg:3395')  # WGS84 / World Mercator (EPSG:3395) for meters

    # Convert Decimal Degrees to Meters
    x_meter, y_meter = pyproj.transform(wgs84, proj, longitude, latitude)
    return x_meter, y_meter