"""
The idea is to make a generic ggplot-ish engine. Then, you can run "to_mpl()", "to_plotly()", etc. to
generate the graphic.

The goal is to provide a flexible plotting framework.
>>> from uplot import *
>>> plot(x, y)
"""

# https://altair-viz.github.io/getting_started/overview.html

from IPython import get_ipython
from IPython.display import display, SVG
from copy import deepcopy
import os.path
import pandas as pd
import sys
from tempfile import NamedTemporaryFile
from typelike import ArrayLike
import yaml

# Include directory
include_dir = os.path.abspath(os.path.join(__file__, '..', '_include'))

# TODO lazy load this please
with open(os.path.join(include_dir, 'markers_mpl.yml'), 'r') as stream:
    markers_mpl = yaml.safe_load(stream.read())


# Style defaults
def set_mpl_theme():
    import matplotlib.pyplot as plt
    # plt.style.use('default')
    # plt.style.use('seaborn')
    # font_size = 18
    # plt.rcParams.update({
    #     'axes.labelsize': font_size,
    #     'axes.titlesize': font_size,
    #     'figure.titlesize': font_size,
    #     'font.size': font_size,
    #     'font.family': 'DejaVu Sans',
    #     'legend.fontsize': font_size,
    #     'legend.title_fontsize': font_size,
    #     'xtick.labelsize': font_size,
    #     'ytick.labelsize': font_size
    # })

    # set style
    plt.style.use('_classic_test')
    plt.rcParams.update({'axes.grid': True,
                         'axes.labelsize': 18,
                         'axes.titlesize': 18,
                         'figure.facecolor': 'white',
                         'font.size': 18,
                         'legend.fontsize': 18,
                         'xtick.labelsize': 18,
                         'ytick.labelsize': 18,
                         })
    plt.rc('text', usetex=True)


_style_defaults = {
    'background': 'white',
    'legend': False
}


# https://ggplot2-book.org/polishing.html
class Figure:
    def __init__(self, data=None, style=None):
        self._data = data
        self._style = style if style is not None else {}
        self._figure_objects = []

    # Add a new FigureObject
    def __add__(self, other):
        # Deepcopy self
        obj = deepcopy(self)

        # Type check
        if not isinstance(other, FigureObject):
            raise AttributeError('must be FigureObject instance')

        # Add FigureObject
        obj.add_figure_object(other)

        # Return
        return obj

    # Add FigureObject
    def add_figure_object(self, figure_object):
        """
        Add a child instance of FigureObject to the Figure in place.

        Parameters
        ----------
        figure_object : FigureObject
            Child instance of FigureObject.
        """

        # Make sure we have an instance of FigureObject
        if not isinstance(figure_object, FigureObject):
            raise AttributeError('must be child of FigureObject')

        # Tell the figure_object who owns it
        figure_object._figure = self

        # Add the figure object
        self._figure_objects.append(figure_object)

    # Get style from the dictionary
    def get_style(self, style, default=None, index=None):
        if style in self._style:
            result = self._style[style]
        else:
            result = _style_defaults.get(style, default)

        if isinstance(result, ArrayLike) and index is not None:
            result = result[index]
        return result

    # Convert figure to matplotlib
    # noinspection PyShadowingNames
    def to_mpl(self, show=False, save_as=None):
        # Make sure pyplot is loaded
        import matplotlib.pyplot as plt
        set_mpl_theme()

        # Create the figure and axis
        figure = plt.figure(figsize=self.get_style('figsize'))  # type: plt.Figure
        axis = figure.add_subplot()

        # Iterate through figure objects and draw
        for figure_object in self._figure_objects:
            figure_object._to_mpl(figure, axis)

        # Canvas
        figure.patch.set_facecolor(self.get_style('background'))

        # Set plot elements
        axis.set_xlabel(self.get_style('xtitle'))
        axis.set_ylabel(self.get_style('ytitle'))
        axis.set_xlim(self.get_style('xmin'), self.get_style('xmax'))
        axis.set_ylim(self.get_style('ymin'), self.get_style('ymax'))
        if self.get_style('legend'):
            axis.legend(bbox_to_anchor=(1., 0.5), loc='center left')

        # Should we save?
        if save_as is not None:
            # TODO there will have to be a way to include some arguments here
            figure.savefig(save_as)

        # Return
        if show:
            if get_ipython() and 'qtconsole' not in sys.modules:
                _display_svg(figure)
            else:
                figure.show()
            # plt.close()
        else:
            return figure

    def to_plotnine(self):
        pass

    def to_plotly(self):
        pass


class FigureObject(Figure):
    def __init__(self, data=None, style=None):
        super().__init__(data, style)
        self._figure = None

    def __add__(self, other):
        raise NotImplementedError

    def add_figure_object(self, figure_object):
        raise NotImplementedError

    # Get data from the FigureObject first, then its parent
    def _get_data(self):
        # Get data from the FigureObject first, then its parent
        data = self._data
        if data is None and isinstance(self._figure, Figure):
            data = self._figure._data

        # If there is still no data, throw an error
        if data is None:
            raise AttributeError('data does not exist')

        # If the data is not a DataFrame, throw an error
        if not isinstance(data, pd.DataFrame):
            raise AttributeError('data must be pandas DataFrame')

        # Return
        return data


class Style:
    def __init__(self, **kwargs):
        pass


class Bar(FigureObject):
    def __init__(self, data=None, style=None):
        super().__init__(data, style)

    # noinspection PyShadowingNames
    def _to_mpl(self, figure, axis):
        # Get data
        data = self._get_data()
        x = data.index.values

        # Loop over all columns
        for i, column in enumerate(self._data.columns):
            # Get y for column
            y = self._data[column].values
            ylabel = self.get_style('ylabel', default=column, index=i)
            axis.bar(x, y, label=ylabel)


class Line(FigureObject):
    def __init__(self, data=None, style=None):
        super().__init__(data, style)

    # noinspection PyShadowingNames
    def _to_mpl(self, figure, axis):
        # Get data
        data = self._get_data()
        x = data.index.values

        # Loop over all columns
        for i, column in enumerate(self._data.columns):
            # Get y for column
            y = self._data[column].values
            ylabel = self.get_style('ylabel', default=column, index=i)
            marker = self.get_style('marker', index=i)
            if marker is not None:
                marker = markers_mpl[marker]
            axis.plot(x, y, label=ylabel, marker=marker)


#
# class Point(FigureObject):
#     def __init__(self, data=None, style=None):
#         super().__init__(data, style)
#
#     # noinspection PyShadowingNames
#     def to_mpl(self, figure, axis):
#         x = self._data.index.values
#         for column in self._data.columns:
#             y = self._data[column].values
#             # TODO label override from style
#             axis.plot(x, y, 'o', label=column)


def figure(data=None, x=None, y=None, style=None):
    """
    Create a figure.

    Parameters
    ----------
    data : pandas.DataFrame
        If provided, uses the data in `data` for the figure.
    x : str or ArrayLike
        If provided, and `data` is not set, this is the independent variable.
    y : str or ArrayLike
        If provided, and `data` is not set, this is the dependent variable.
    style : dict
        If provided, list of style elements.

    Returns
    -------
    Figure
        Instance of Figure object.
    """

    # Coerce data
    data = _coerce_data_x_y(data, x, y)

    # Create Figure
    element = Figure(data, style)

    # Set figure attributes
    # ...

    # Return
    return element


def bar(x=None, y=None, style=None):
    data = _coerce_data_x_y(None, x, y)
    style = _coerce_style(style, defaults={'linestyle': 'solid'})
    element = Bar(data, style)
    return element


def line(x=None, y=None, style=None):
    data = _coerce_data_x_y(None, x, y)
    style = _coerce_style(style, defaults={'linestyle': 'solid'})
    element = Line(data, style)
    return element


def point(x=None, y=None, style=None):
    data = _coerce_data_x_y(None, x, y)
    style = _coerce_style(style, defaults={'marker': 'circle'})
    element = Line(data, style=style)
    return element


# Extract label from pandas if possible
def _get_label(x, default='x'):
    label = default
    if isinstance(x, pd.Series):
        label = x.name
    return label


# Coerce data and x and y into expected types and formats
def _coerce_data_x_y(data, x, y):
    # If data is not set
    if data is None:
        # If both of x and y are arrays, build DataFrame
        if isinstance(x, ArrayLike) and isinstance(y, ArrayLike):
            # Make sure y is an array of arrays (for simplicity)
            if not isinstance(y[0], ArrayLike):
                y = [y]

            # Build DataFrame
            x_label = _get_label(x, default='x')
            data = pd.DataFrame({x_label: x}).set_index(x_label)
            len_y = len(y)
            for i, yi in enumerate(y):
                if len_y == 1:
                    y_label_default = 'y'
                else:
                    y_label_default = 'y' + str(i)
                y_label = _get_label(y, default=y_label_default)
                data[y_label] = yi

        # If data is not set, and x and y are not arrays, we don't know what we're doing
        elif x is not None or y is not None:
            raise AttributeError('must pass data or x and y arrays')

    # Otherwise, if data is a DataFrame, extract out x and y columns
    elif isinstance(data, pd.DataFrame):
        data = data.set_index(x)[y].copy()

    # Otherwise, if data is a Series, convert to DataFrame
    elif isinstance(data, pd.Series):
        data = data.to_frame()

    # Else
    else:
        raise AttributeError('cannot process input')

    # Return the DataFrame
    return data


def _coerce_style(style, defaults=None):
    if style is None:
        style = {}
    style = {key.lower(): value for key, value in style.items()}
    if defaults is not None:
        for key in defaults:
            if key not in style:
                style[key] = defaults[key]
    return style

#
# (
#     figure(style={'xtitle': '$x$', 'ytitle': '$y$', 'legend': True})
#     + line([1, 2, 3], [4, 5, 6], style={'marker': 'circle', 'ylabel': 'y1'})
#     + line([1, 2, 3], [6, 5, 4], style={'marker': 'circle', 'ylabel': 'y2'})
# ).to_mpl(show=True)


# Display SVG in IPython
def _display_svg(figure):
    with NamedTemporaryFile(delete=False) as tempfile:
        filename = str(tempfile.name) + '.svg'
    figure.savefig(filename=filename, transparent=True)
    display(SVG(filename))
    os.remove(filename)
