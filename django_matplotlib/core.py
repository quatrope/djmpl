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


# =============================================================================
# IMPORTS
# =============================================================================

import io
import base64

import matplotlib.pyplot as plt

from django.conf import settings
from django.utils.html import format_html
from django.template.engine import Engine

import jinja2

import mpld3

import attr


# =============================================================================
# CONSTANTS
# =============================================================================

#: List of available plot formats.
AVAILABLE_FORMATS: list = ["mpld3", "svg", "png"]

#: Default plot format. This can be changed with a ``DJMPL``` setting variable.
DJMPL_FORMAT: str = getattr(settings, "DJMPL_FORMAT", AVAILABLE_FORMATS[0])


#: The first template engine configured in ``settings.template```
DEFAULT_TEMPLATE_ENGINE = settings.TEMPLATES[0]["BACKEND"]


#: Map the template engine name to a function that make "safe" to render
#: the image into the final HTML.
TEMPLATES_FORMATERS = {
    "django.template.backends.django.DjangoTemplates":  format_html,
    "jango.template.backends.jinja2.Jinja2": jinja2.Markup}


#: Default template engine for render the plots. By default uses the
#: same as the default entine in ``settings.TEMPLATES```, this can
#: be changed by ``settings.DJMPL_TEMPLATE_ENGINE``` variable.
DJMPL_TEMPLATE_ENGINE: str = getattr(
    settings, "DJMPL_TEMPLATE_ENGINE", DEFAULT_TEMPLATE_ENGINE)


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
        validator=attr.validators.in_(AVAILABLE_FORMATS))
    template_engine = attr.ib()

    def get_img_png(self) -> str:
        buf = io.BytesIO()
        self.fig.savefig(buf, format='png')
        png = buf.getvalue()
        buf.close()
        png = base64.b64encode(png).decode("ascii")
        return f"<img src='data:image/png;base64,{png}'>"

    def get_img_svg(self) -> str:
        buf = io.StringIO()
        self.fig.savefig(buf, format='svg')
        svg = buf.getvalue()
        buf.close()
        return svg

    def get_img_mpld3(self) -> str:
        return mpld3.fig_to_html(fig)

    def safe(self, img) -> object:
        formater = TEMPLATES_FORMATERS.get(template_engine, str)
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

def subplots(
    plot_format: str = DJMPL_FORMAT,
    template_engine = DJMPL_TEMPLATE_ENGINE,
    *args, **kwargs
) -> DjangoMatplotlibWrapper:
    """This functions tries to mimic the behavior of
    matplotlib.pyplot.subplots but return a DjangoMatplotlibWrapper instead
    figure and axes.

    Also this functions receive in which format you want to write your plot
    in the HTML page.

    """
    fig, axes = plt.subplots(*args, **kwargs)
    return DjangoMatplotlibWrapper(
        plot_format=plot_format, template_engine=template_engine,
        fig=fig, axes=axes)
