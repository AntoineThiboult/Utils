# -*- coding: utf-8 -*-
"""
Created on Mon Jan  8 15:42:31 2024

@author: ANTHI182
"""
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import numpy as np
import geopandas as gpd


def get_latlon_index(nc,lat,lon):
    id_lat = np.argmin(np.abs(nc.variables['lat'][:] - lat))
    id_lon = np.argmin(np.abs(nc.variables['lon'][:] - lon))
    return id_lat, id_lon


def print_variables(nc, sort_names=False):
    if sort_names:
        keys = sorted(nc.variables.keys())
    else:
        keys = nc.variables.keys()

    for v in keys:
        names = [s for s in nc[v].__dict__ if "name" in s]
        print(f'{nc[v]._getname()}')
        for n in names:
            print(f'\t {n}: {getattr(nc[v], n)}')


def print_dimensions(nc, sort_names):
    if sort_names:
        keys = sorted(nc.dimensions.keys())
    else:
        keys = nc.dimensions.keys()

    for v in keys:
        print(f'{v}: {nc.variables[v].shape}')


def print_variable_dimension(nc, dim_names=False, sort_names=False):
    if sort_names:
        keys = sorted(nc.variables.keys())
    else:
        keys = nc.variables.keys()

    for v in keys:
        if dim_names:
            print(f'{v}: {nc.variables[v]._getdims()} -> {nc.variables[v].shape}')
        else:
            print(f'{v}: {nc.variables[v].shape}')


def show_mask(var, title='', id_slice=[0]):
    nrows = len(id_slice) // np.sqrt(len(id_slice))
    ncols = np.ceil(len(id_slice) / nrows)
    fig, ax = plt.subplots(int(nrows),int(ncols))
    ax = np.ravel(ax)
    for i in range(0,len(ax)):
        ax[i].imshow(var[i,:,:].mask.astype(float))
    fig.suptitle(title)


def show_slice(var, title='', id_slice=[0]):
    if len(var.dimensions) < 3:
        print(f'Number of dimnesion different from 3 for {title}')
        return
    nrows = len(id_slice) // np.sqrt(len(id_slice))
    ncols = np.ceil(len(id_slice) / nrows)
    fig, ax = plt.subplots(int(nrows),int(ncols))
    ax = np.ravel(ax)
    for i in range(0,len(ax)):
        im = ax[i].imshow(var[id_slice[i],:,:])
        ax[i].set_title(f'Slice: {id_slice[i]}')
        fig.colorbar(im, ax=ax[i])
    fig.suptitle(f'{title}')


def show_all_var_slices(nc, id_slice=[0]):
    for v in nc.variables:
        show_slice(nc.variables[v], v, id_slice)


def show_2d_slice(var, lon, lat, ax, cmap='hot', cb=True):
    # Show a
    lon_interval = np.mean(np.diff(lon))/2
    lat_interval = np.mean(np.diff(lat))/2
    im = ax.imshow(var, cmap=cmap, extent=[
        lon.min()-lon_interval, lon.max()+lon_interval,
        lat.min()-lat_interval, lat.max()+lat_interval],
        aspect='equal', origin='lower')

    # Plot embellishment
    ax.set_xticks(ticks=lon, labels=[f'{t:0.1f}' for t in lon], rotation=75)
    ax.set_yticks(ticks=lat, labels=[f'{t:0.1f}' for t in lat])
    ax.grid()
    if cb:
        plt.colorbar(im)


def add_shapefile(shapefile, ax):
    shape = gpd.read_file(shapefile)
    shape.plot(ax=ax)


def hours_since_ref_date(date, reference_date = datetime(1900, 1, 1, 0, 0, 0)):
    """
    Compute the number of hours that passed between 1900-01-01 00:00:00 and
    input_date

    Parameters
    ----------
    date : datetime object
    reference_date : date time object that is used as reference. By default
        reference_date = 1900-01-01 00:00:00

    Returns
    -------
    hours_difference : float
        difference in hours between input date and 1900-01-01 00:00:00

    """

    # Calculate the difference in hours between input date and reference date
    hours_difference = (date - reference_date).total_seconds() / 3600

    return hours_difference


def date_from_hours_elapsed(hours):
    """
    Compute the date from the number of hours elapsed since 1900-01-01 00:00:00

    Parameters
    ----------
    hours : float
        Number of hours elapsed since 1900-01-01 00:00:00

    Returns
    -------
    target_date_str : datetime object
        DESCRIPTION.

    """
    # Define the reference date (1900-01-01 00:00:00.0)
    reference_date = datetime(1900, 1, 1, 0, 0, 0)

    # Calculate the timedelta corresponding to the given number of hours
    delta = timedelta(hours=hours)

    # Calculate the target date by adding the timedelta to the reference date
    date = reference_date + delta

    return date


def date_to_decimal_date(date):
    """
    Convert a datetime to a decimal date '%Y%m%d.fraction_of_day'

    Parameters
    ----------
    date : datetime object

    Returns
    -------
    result_date_decimal : String

    """

    # Extract the date part
    date_integral_part = date.strftime("%Y%m%d")

    # Calculate the fractional part of the day
    fraction_of_day = date.hour / 24.0 + date.minute / 1440.0 + date.second / 86400.0

    # Format the fractional part as ".fff"
    date_fractional_part = "{:.8f}".format(fraction_of_day)[1:]

    # Concatenate the date part and fractional part
    result_date_str = date_integral_part + date_fractional_part
    result_date_decimal = float(result_date_str)

    return result_date_decimal


def decimal_date_to_date(fractional_date):
    """
    Convert a string decimal date '%Y%m%d.fraction_of_day' to a datetime date

    Parameters
    ----------
    fractional_date : String
        Decimal date with format '%Y%m%d.fraction_of_day'

    Returns
    -------
    date : datetime object
    """

    # Split the input string into date and fractional part
    date_str, fraction_str = fractional_date.split('.')

    # Convert date part to datetime object
    date_part = datetime.strptime(date_str, "%Y%m%d")

    # Convert fractional part to seconds
    total_seconds = float("0." + fraction_str) * 86400  # Total seconds in a day

    # Convert seconds to hours, minutes, and seconds
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)

    # Combine date part and time part to get the final datetime object
    date = date_part + timedelta(hours=hours, minutes=minutes, seconds=seconds)

    return date