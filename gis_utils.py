# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 11:26:13 2024

@author: ANTHI182
"""

import rasterio
import pyproj
import numpy as np
import geopandas as gpd

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


def dms_to_ddeg(coord):
    """
    Convert degree minute second to decimal degrees

    Parameters
    ----------
    coord : tuple <(degree,minute,second)>

    Returns
    -------
    dec_coord : Float
    """
    return coord[0] + coord[1]/60 + coord[2]/3600


def projected_meter_to_degrees(coord, projection):
    """
    Convert decimal degrees to meters in the specified projection system.
    Projection system can be either specified with the name (for example
    world_mercator, lambert_conformal_conic) or by their code (3395, 32198).

    Parameters
    ----------
    coord : tuple (x, y) or equivalently (longitude, latitude)
    projection : string or integer.
        projection system by name, or by code

    Returns
    -------
    x_meter : float
        longitude in meters in projected coordinate system
    y_meter : float
        latitude in meters in projected coordinate system
    """

    if isinstance(projection, str):
        match projection:
            case 'world_mercator':
                proj_code_str = 'epsg:3395'
            case 'lambert_conformal_conic':
                proj_code_str = 'epsg:32198'

    if isinstance(projection, int):
        proj_code_str = f'epsg:{projection}'

    # Define WGS84 and Projected Coordinate System
    wgs84 = pyproj.Proj(init='epsg:4326')  # WGS84 datum
    proj = pyproj.Proj(init=proj_code_str)  # WGS84 / World Mercator (EPSG:3395) for meters

    # Convert Decimal Degrees to Meters
    x_degrees, y_degrees = pyproj.transform(proj, wgs84, coord[0], coord[1])
    return x_degrees, y_degrees


def degrees_to_projected_meter(coord, projection):
    """
    Convert decimal degrees to meters in the specified projection system.
    Projection system can be either specified with the name (for example
    world_mercator, lambert_conformal_conic) or by their code (3395, 32198).

    Parameters
    ----------
    coord : tuple (x, y) or equivalently (longitude, latitude)
    projection : string or integer.
        projection system by name, or by code

    Returns
    -------
    x_meter : float
        longitude in meters in projected coordinate system
    y_meter : float
        latitude in meters in projected coordinate system
    """

    if isinstance(projection, str):
        match projection:
            case 'world_mercator':
                proj_code_str = 'epsg:3395'
            case 'lambert_conformal_conic':
                proj_code_str = 'epsg:32198'

    if isinstance(projection, int):
        proj_code_str = f'epsg:{projection}'

    # Define WGS84 and Projected Coordinate System
    wgs84 = pyproj.Proj(init='epsg:4326')  # WGS84 datum
    proj = pyproj.Proj(init=proj_code_str)  # WGS84 / World Mercator (EPSG:3395) for meters

    # Convert Decimal Degrees to Meters
    x_meter, y_meter = pyproj.transform(wgs84, proj, coord[0], coord[1])
    return x_meter, y_meter


def get_shapefile_extent(shapefile):
    """
    Get the bounding box of a shapefile

    Parameters
    ----------
    shapefile : String or Pathlib Path
        Path to the shapefile

    Returns
    -------
    minx, miny, maxx, maxy : bounding box in the shapefile coordinates

    """
    shape = gpd.read_file(shapefile)
    minx, miny, maxx, maxy = shape.geometry.total_bounds
    return minx, miny, maxx, maxy