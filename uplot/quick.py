"""
quick.py
Written in Python3
author: C. Lockhart <chris@lockhartlab.org>
"""

from . import core

from typelike import ArrayLike


# Plot
def plot(x, y=None, xtitle=None, ytitle=None, legend=True, marker=None, show=True):
    """


    Parameters
    ----------
    x : pandas.DataFrame or ArrayLike
        DataFrame to plot, or the `x` dimension for plotting.
    y : ArrayLike or None
        If present, `y` dimension for plotting. If this is an array of arrays, every interior array will be treated
        as a dependent variable to `x`.
    xtitle : str or None
        Title of the `x` axis.
    ytitle : str or None
        Title of the `y` axis.
    legend : bool or ArrayLike
        If bool, yes or no if the legend should be display. If this is ArrayLike, then these are the legend titles.
    show : bool
        Should the figure be shown?

    Returns
    -------
    matplotlib.pyplot.figure.Figure or None
        Figure or nothing, depending on `show`.
    """

    # Create figure
    figure = core.figure(x=x, y=y, style={'xtitle': xtitle, 'ytitle': ytitle, 'legend': legend})

    # Start building the figure
    figure += core.line(style={'marker': marker})

    # Return
    if show:
        figure.to_mpl(show=show)
    else:
        return figure.to_mpl(show=False)

