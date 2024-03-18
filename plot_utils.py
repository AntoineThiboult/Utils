# -*- coding: utf-8 -*-
"""
Created on Tue Dec 12 13:41:12 2023

@author: ANTHI182
"""
import numpy as np
import matplotlib.pyplot as plt

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

