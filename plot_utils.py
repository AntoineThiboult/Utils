# -*- coding: utf-8 -*-
"""
Created on Tue Dec 12 13:41:12 2023

@author: ANTHI182
"""

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors
import numpy as np
from scipy.stats import gaussian_kde
import rasterio
import pickle

def draw_linear_reg(reg, ax=None , X=None, c='C0', verb=False):
    """
    Add a scikit learn linear regression to a matplotlib axes.
    Plots

    Parameters
    ----------
    reg : sklearn linear regression object
    ax : Matplotlib axes
    X : Numpy serie, optional
        x values where the regression is evaluated. If not specified, the
        current axes limit are used.
    c : String, optional
        Matplotlib color code to draw the linear regression. The default is 'C0'.
    verb : Boolean, optional
        Verbose. Print the regression coefficient in the terminal. The default is False.

    Returns
    -------
    h : Matplotlib line object

    """
    if X is not None:
        mask = ~np.isnan(X) & np.isfinite(X)
        if np.ndim(X)==1:
            X = X[mask,np.newaxis]
        else:
            X = X[mask,:]
    else:
        if ax:
            X = np.array(ax.get_xlim())
        else:
            X = np.array([-1,1])
        X = X[:,np.newaxis]

    y = reg.predict(X)
    if ax:
        h = ax.plot(X, y, color=c)
    else:
        h = plt.plot(X, y, color=c)
    return h


def add_text_rp(text, x_rp,y_rp,ax=None):
    """
    Add text at X, Y data relative position (in data coordinates)

    Parameters
    ----------
    ax : Pyplot AxesSubplot object
    x_rp : float (typically 0 < x_rp < 1)
        Relative position of the string on the x axis
    y_rp : float (typically 0 < y_rp < 1)
        Relative position of the string on the y axis

    Returns
    -------
    x_dc : float
        x position in data coordinates
    y_dc : float
        y position in data coordinates

    """
    if ax:
        x_dc = ax.get_xlim()[0] + (ax.get_xlim()[1]- ax.get_xlim()[0]) *x_rp
        y_dc = ax.get_ylim()[0] + (ax.get_ylim()[1]- ax.get_ylim()[0]) *y_rp
        h = ax.text(x_dc, y_dc, text)
    else:
        x_dc = x_rp
        y_dc = y_rp
        h = plt.text(x_dc, y_dc, text)
    return h


def draw_quantile_boundaries(x, y, n_bins=10, quantile=(5,95), ax=None, c='C0'):

    mask = (
        ~np.isnan(x) & np.isfinite(x) &
        ~np.isnan(y) & np.isfinite(y)
        )
    x, y = x[mask], y[mask]

    # Create histogram bins for 'x'
    bin_edges = np.quantile(x, np.linspace(0,1,n_bins+1))

    # Initialize arrays to store quantile values
    quantile_05_values = np.zeros(n_bins)
    quantile_95_values = np.zeros(n_bins)

    # Calculate quantile values for each bin
    for i in range(n_bins):
        indices_in_bin = np.where((x >= bin_edges[i]) & (x < bin_edges[i + 1]))
        quantile_05_values[i] = np.percentile(y[indices_in_bin], quantile[0])
        quantile_95_values[i] = np.percentile(y[indices_in_bin], quantile[1])

    # Calculate the bin centers
    bin_centers = [(bin_edges[i] + bin_edges[i + 1]) / 2 for i in range(len(bin_edges) - 1)]

    if not ax:
        fig, ax = plt.subplots()
    ax.plot(bin_centers, quantile_05_values, color=c)
    ax.plot(bin_centers, quantile_95_values, color=c)


def draw_identity_line(ax, color='k'):
    """
    Draw the identity line (the 1:1 line).

    Parameters
    ----------
    ax : matplotlib axes
    color : string, optional
        Color of the identity line. The default is 'k'.

    Returns
    -------
    l : Line2D object of matplotlib.lines module
        The identity line

    """
    l = ax.plot(ax.get_xlim(), ax.get_xlim(), c=color)
    return l


def density_scatter_plot(x, y, ax=None, s=50, cmap='viridis'):
    """
    Make a scatter plot that renders the density of the points with a color
    scheme.

    Parameters
    ----------
    x : Numpy array
        x data
    y : Numpy array
        y data
    ax : Matplotlib axis
        Matplotlib axis where the scatter plot will be displayed. If not
        specified, a new axis is created. The default is None.
    s : Int, optional
        Size of the markers. The default is 50.
    cmap : String, optional
        Matplotlib colormap. The default is 'viridis'.

    Returns
    -------
    h : Matplotlib scatter plot

    """
    # Cleaning the data
    mask = np.isfinite(x) & np.isfinite(y)
    x, y = x[mask], y[mask]

    # Calculate the point density
    xy = np.vstack([x,y])
    z = gaussian_kde(xy)(xy)

    # Sort the points by density, so that the densest points are plotted last
    idx = z.argsort()
    x, y, z = x[idx], y[idx], z[idx]

    if not ax:
        fig, ax = plt.subplots()
    h = ax.scatter(x, y, c=z, s=s, cmap=cmap)
    return h


def make_iterable_subplots(iterable, figsize=(6,4)):
    """
    Create a figure with an ideal number of subplots to represent each element
    of an iterable variable. It returns a set of axes for each subplot that
    is iterable in a simple loop.

    Parameters
    ----------
    iterable : Iterable object (list, array, etc)
    figsize : Tuple, optional
        Size of the figure. The default is (6,4).

    Returns
    -------
    fig : Matplotlib figure object
    ax : Matplotlib list of axes

    """
    nrows = len(iterable) // np.sqrt(len(iterable))
    ncols = np.ceil(len(iterable) / nrows)
    fig, ax = plt.subplots(int(nrows),int(ncols), figsize=figsize)
    ax = np.ravel(ax)
    return fig, ax


def plot_histogram(bin_edges, bin_counts, ax = None, width=1, color='b', alpha=0.7, edgecolor='black'):
    """
    Plot histogram from bin_edges and bin_counts using matplotlib.pyplot.bar
    and avoid all (?) matplotlib.pyplot.hist traps.

    Parameters
    ----------
    bin_edges : array
        Edges of the bins to construct the histogram
    bin_counts : array
        Number of occurence for the corresponding bin
    ax : matplotlib axis, optional
        Axis on which histogram will be plot. If not specified, a new figure is created. The default is None.
    width : float, optional
        Relative width of the bars to the bin edges. The default is 1.
    color : string, optional
        Color of the bar. The default is 'b'.
    alpha : float, optional
        Transparency. The default is 0.7.
    edgecolor : float, optional
        Color of the edge of the bar. The default is 'black'.

    Returns
    -------
    fig : matplotlib figure
    ax : matplotlib axis
    """
    if not ax:
        fig, ax = plt.subplots()
    bin_centers = [(bin_edges[i] + bin_edges[i+1]) / 2 for i in range(len(bin_edges)-1)]
    ax.bar(bin_centers, bin_counts,
           width=(bin_edges[1]-bin_edges[0])*width,
           color=color, alpha=alpha, edgecolor=edgecolor)
    return fig, ax


def plot_footprint_over_map(footprint, background_map, coordinates,
                            show_heatmap=True, heatmap_colormap=cm.jet, normalize_colormap=False,
                            contour_line_width=0.5, contour_line_color = 'k',
                            iso_labels=False, iso_label_size=8):
    """
    Plot the footprint computed by the Kljun method over a georeferenced map.
    The map should be projected and have meters for units.
    For the footprint method, see:
    Kljun, N., P. Calanca, M.W. Rotach, H.P. Schmid, 2015:
    The simple two-dimensional parameterisation for Flux Footprint Predictions FFP.
    Geosci. Model Dev. 8, 3695-3713, doi:10.5194/gmd-8-3695-2015, for details.

    Parameters
    ----------
    footprint : Dictionary
        Dictionary as provided by the Kljun algorithm. Must contain the
        following fields:
            x_2d	    = x-grid of 2-dimensional footprint [m]
            y_2d	    = y-grid of 2-dimensional footprint [m]
            fclim_2d = Normalised footprint function values of footprint climatology [m-2]
            rs       = Percentage of footprint as in input, if provided
            fr       = Footprint value at rs, with rs the percentage of footprint as in inputif r is provided
    background_map : String or Pathlib Path
        Path to the map file
    coordinates : Tuple
        Coordinates (longitude, latitude) in meters in the map projection
        system of the center of the footprint (location of the station)

    show_heatmap : Bool, optional
    heatmap_colormap : Matplotlib.pyplot colormap, optional
        The default is cm.jet.
    normalize_colormap : String, optional
        Normalize the colors for the heatmap. Can be False, 'log', 'power'
        and 'boundaries'. The default is False.

    contour_line_width : Float, optional
        The default is 0.5.
    contour_line_color : String, optional
        The default is 'k'.

    iso_labels : Bool, optional
        Add labels for the iso contours. The default is False.
    iso_label_size : Float, optional
        Size of the iso contours labels. The default is 8.

    Returns
    -------
    fig : TYPE
        DESCRIPTION.
    ax : TYPE
        DESCRIPTION.

    """

    # Load footprint data
    with open(footprint, 'rb') as f:
        footprint_dict = pickle.load(f)

    x_2d = footprint_dict['x_2d'] + coordinates[0]
    y_2d = footprint_dict['y_2d'] + coordinates[1]
    fs = footprint_dict['fclim_2d']
    clevs = np.hstack((
        np.sort( np.array(footprint_dict['fr']) ),
        np.max(fs)
        ))

    # Read the GeoTIFF file
    with rasterio.open(background_map) as src:
        background = src.read()
        background = np.moveaxis(background, 0, -1)
        extent = [src.bounds.left, src.bounds.right, src.bounds.bottom, src.bounds.top]

    # Initialize figure
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.imshow(background,extent=extent)

    match normalize_colormap:
        case 'log':
            norm = colors.LogNorm(vmin=np.quantile(fs,0.5), vmax=fs.max())
        case 'power':
            norm = colors.PowerNorm(0.35)
        case 'boundary':
            norm = colors.BoundaryNorm(np.quantile(fs,np.arange(1,0,-0.1)),256)
        case _:
            norm = None

    if show_heatmap:
        ax.contourf(x_2d, y_2d, fs, clevs, alpha = 0.5, cmap = heatmap_colormap,
                           norm=norm)
    # Show contour
    ctr = ax.contour(x_2d, y_2d, fs, clevs, colors = contour_line_color, linewidths=contour_line_width)

    #Isopleth Labels
    if iso_labels:
        pers = [str(int(clev*100))+'%' for clev in footprint_dict['rs'][::-1]]
        fmt = {}
        for l,s in zip(ctr.levels, pers):
            fmt[l] = s
        plt.clabel(ctr, fmt=fmt, inline=True, fontsize=iso_label_size)
    plt.show()
    return fig, ax