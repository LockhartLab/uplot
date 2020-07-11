"""
viz.py
Written in Python3
author: C. Lockhart <chris@lockhartlab.org>
"""

from IPython import get_ipython
from IPython.display import display, SVG
import os
import numpy as np
import pandas as pd
import plotnine as p9
import sys
from tempfile import NamedTemporaryFile
from typelike import ArrayLike


# Plot
def plot(x, y=None, xlab=None, ylab=None, geom=('line', 'point'), na_rm=True, legend=True, figsize=None, output='auto',
         **kwargs):
    """
    https://matplotlib.org/tutorials/colors/colormaps.html
    https://github.com/rstudio/cheatsheets/blob/master/data-visualization-2.1.pdf

    Parameters
    ----------
    x : pd.DataFrame or ArrayLike
        DataFrame to plot, or the `x` dimension for plotting.
    y : ArrayLike or None
        If present, `y` dimension for plotting. If this is an array of arrays, every interior array will be treated
        as a dependent variable to `x`.
    xlab : str or None
        Title of the `x` axis.
    ylab : str or None
        Title of the `y` axis.
    geom : str or list
    na_rm : bool
        Should nulls or missing values be removed? (Default: True)
    legend : bool or ArrayLike
        If bool, yes or no if the legend should be display. If this is ArrayLike, then these are the legend titles.
    output : string

    Returns
    -------

    """

    # Process miscellaneous input arguments
    if xlab is None:
        xlab = ''
    if ylab is None:
        ylab = ''
    if isinstance(output, str):
        output = output.lower()

    # If x is a DataFrame, x is the index and y are columns
    if isinstance(x, pd.DataFrame):
        df = x
        x = df.index.names
        y = df.columns

    # Otherwise, construct a DataFrame
    else:
        # y must be ArrayLike
        if not isinstance(y, ArrayLike):
            raise AttributeError('y must be ArrayLike')

        # Dump everything into a DataFrame
        df = pd.DataFrame({'x': x}).set_index('x')
        if not isinstance(y[0], ArrayLike):
            df['y'] = y
        else:
            for i, y_i in enumerate(y):
                df['y' + str(i)] = y_i

    # Name df.index.name as x for convenience. Rename y columns for legend if necessary. Melt DataFrame.
    # TODO downside of this legend approach is that it's dependent on order of columns in DataFrame. Maybe remove?
    x = df.index.name
    if isinstance(legend, ArrayLike):
        df = df.rename(columns=dict(zip(df.columns, legend)))
    y = df.columns
    df = df.reset_index().melt(id_vars=x)

    # Make geom an array if it's not one already; convert all elements to lowercase
    geom = np.array(geom).reshape(-1)
    for i, geom_i in enumerate(geom):
        geom[i] = geom_i.lower()

    # Start building the figure
    fig = p9.ggplot(df, p9.aes(x=x, y='value', color='variable', group='variable'))
    if 'line' in geom:
        fig += p9.geom_line(na_rm=na_rm)
    if 'point' in geom:
        fig += p9.geom_point(na_rm=na_rm)
    fig += p9.labs(x=xlab, y=ylab)
    fig += p9.theme(axis_text_x=p9.element_text(rotation=45),
                    legend_title=p9.element_blank(), legend_key=p9.element_blank())

    if figsize is not None:
        fig += p9.theme(figure_size=figsize)

    if legend:
        fig += p9.scale_color_manual(values=[p9.scale_color_cmap('Set1').palette(i) for i in range(len(y))])
    else:
        fig += p9.theme(legend_position='none')

    # Return
    # TODO ipython might fail here
    if output in ['auto', 'ipython'] and get_ipython() and 'qtconsole' not in sys.modules:
        _display_svg(fig)
    else:
        return fig


# Display SVG in IPython
def _display_svg(fig):
    with NamedTemporaryFile(delete=False) as tempfile:
        filename = str(tempfile.name) + '.svg'
    fig.save(filename=filename, verbose=False)
    display(SVG(filename))
    os.remove(filename)
