#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2020, Juan B Cabral & QuatroPe
# License: BSD-3-Clause
#   Full Text: https://github.com/quatrope/djmpl/blob/master/LICENSE

# =============================================================================
# DOCS
# =============================================================================
"""Wrapper around the matplotlib functionalities to write plots into a
django templates.

"""

__all__ = ["EngineNotSupported", "subplots"]


# =============================================================================
# IMPORTS
# =============================================================================

import base64
import io

import attr

import matplotlib.pyplot as plt

import mpld3

from . import settings


# =============================================================================
# EXCEPTIONS
# =============================================================================


class EngineNotSupported(ValueError):
    """The engine is not supported for django-matplotlib"""


# =============================================================================
# CLASSES BASE
# =============================================================================


@attr.s(frozen=True)
class DjangoMatplotlibWrapper:
    """This class are in charge of contain a figure and axes and write it
    to an HTML format.

    Parameters
    ----------

    fig:
        Matplotlib figure class.
    axes:
        One or more matplotlib.Axes.
    plot_format: str (Default: mpld3)
        The format of the plot.
    template_engine:
        The template engine used to render the the html.

    """

    fig = attr.ib()
    axes = attr.ib()
    plot_format: str = attr.ib(
        validator=attr.validators.in_(settings.AVAILABLE_FORMATS)
    )
    template_engine = attr.ib(
        converter=lambda x: template_by_alias(x),
        validator=attr.validators.in_(settings.TEMPLATES_FORMATERS),
    )

    # PNG
    def get_img_png(self) -> str:
        buf = io.BytesIO()
        self.fig.savefig(buf, format="png")
        png = buf.getvalue()
        buf.close()
        png = base64.b64encode(png).decode("ascii")
        return (
            "<div class='djmpl djmpl-png'>"
            f"<img src='data:image/png;base64,{png}'"
            "</div>"
        )

    # SVG
    def get_img_svg(self) -> str:
        buf = io.StringIO()
        self.fig.savefig(buf, format="svg")
        svg = buf.getvalue()
        buf.close()
        return f"<div class='djmpl djmpl-svg'>{svg}</div>"

    # MPLD3
    def get_img_mpld3(self) -> str:
        html = mpld3.fig_to_html(self.fig)
        return f"<div class='djmpl djmpl-mpld3'>{html}</div>"

    def safe(self, img) -> object:
        formater = settings.TEMPLATES_FORMATERS[self.template_engine]
        return formater(img)

    def html_str(self) -> str:
        key = f"get_img_{self.plot_format}"
        method = getattr(self, key, None)
        if method is None:
            raise NotImplementedError(f"Format unknown {self.plot_format}")
        img = method()
        return img

    def to_html(self) -> str:
        img = self.html_str()
        return self.safe(img)

    def figaxes(self) -> tuple:
        return self.fig, self.axes


# =============================================================================
# FUNCTIONS
# =============================================================================


def template_by_alias(name_or_alias: str) -> str:
    """Retrieve the proper name for a template though the alias.

    If the name is not found the same name_or_alias is returned.

    """
    if name_or_alias in settings.TEMPLATES_FORMATERS:
        return name_or_alias
    try:
        return settings.TEMPLATE_ALIAS[name_or_alias.lower()]
    except KeyError as err:
        raise EngineNotSupported from err


def subplots(
    plot_format: str = settings.DJMPL_FORMAT,
    template_engine: str = settings.DJMPL_TEMPLATE_ENGINE,
    **kwargs,
) -> DjangoMatplotlibWrapper:
    """This functions tries to mimic the behavior of
    matplotlib.pyplot.subplots but return a DjangoMatplotlibWrapper instead
    figure and axes.

    Also this functions receive in which format you want to write your plot
    in the HTML page.

    """
    fig = plt.figure()

    fig, axes = plt.subplots(**kwargs)
    return DjangoMatplotlibWrapper(
        plot_format=plot_format,
        template_engine=template_engine,
        fig=fig,
        axes=axes,
    )
