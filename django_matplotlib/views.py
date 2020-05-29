#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2020, Juan B Cabral & QuatroPe
# License: BSD-3-Clause
#   Full Text: https://github.com/quatrope/djmpl/blob/master/LICENSE

# =============================================================================
# DOCS
# =============================================================================
"""Generic views for django-matplotlib

"""

__all__ = ["MultiPlotMixin", "PlotMixin", "MultiPlotView", "PlotView"]

# =============================================================================
# IMPORTS
# =============================================================================

import re

from django.core.exceptions import ImproperlyConfigured
from django.views.generic.base import TemplateView

from . import core, settings


# =============================================================================
# VIEWS
# =============================================================================


class MultiPlotMixin:

    #: The name of the plots inside the templates
    context_plot_name = "plots"

    #: The format to render the plots in the html
    plot_format = settings.DJMPL_FORMAT

    #: The template engine where the plot will be rendered.
    template_engine = settings.DEFAULT_TEMPLATE_ENGINE

    #: Parameters to be passed when the ``matplotlib.pyplot.subplots```
    #: functions is called.
    subplots_kwargs = None

    #: If this is True the plot/plots are tighten.
    #: Tight_layout automatically adjusts subplot params so that the
    # subplot(s) fits in to the figure area.
    #: More info: https://matplotlib.org/3.2.1/tutorials/intermediate/tight_layout_guide.html # noqa
    tight_layout = False

    #: The plot methods must match whit this regex
    plot_method_regex = r"^plot_"

    def get_subplots_kwargs(self):
        """Retrieve the parameters for the ``matplotlib.pyplot.subplots`` or
        empty dict if it's the class variable ``subplot_kwargs`` is
        not defined.

        """
        return self.subplots_kwargs or {}

    def get_tight_layout(self):
        """Return true if all the figures by default are tighten.

        By default check the class variable ``tight_layout``.

        """
        return bool(self.tight_layout)

    def get_plot_format(self):
        """Retrieve the format to render the plots in the html.

        By default check the class variable ``plot_format``.

        """
        return self.plot_format

    def get_template_engine(self):
        """Retrieve the name template engine for this view.

        By default the first template engine configured in
        ``settings.TEMPLATES`` is returned.

        """
        return self.template_engine

    def get_draw_methods(self):
        """Retrieve all the method in-charge of plot the figures.

        This method iterates over all the contents of the class and
        retrieve only the callables that the name matches the regex
        defined in ``plot_method_regex``.

        """
        cls = type(self)
        methods = [
            method
            for method_name, method in vars(cls).items()
            if callable(method)
            and re.match(self.plot_method_regex, method_name)
        ]
        return methods

    def get_context_plot_name(self):
        """Get the name to use for the plots's template variable.

        By default check the class variable ``context_plot_name``.

        """

        return self.context_plot_name

    def get_plot_context(self):
        "Returns a dictionary to be passed to all the draw_methods"
        return {}

    def get_context_data(self, **kwargs):
        """Overridden version of `.TemplateResponseMixin` to inject the
        plot into the template's context.
        """
        context = super().get_context_data(**kwargs)

        # inject the context info into the kwargs
        plot_context = self.get_plot_context()
        kwargs.update(plot_context)

        # get the subplots_kwargs
        subplot_kwargs = self.get_subplots_kwargs()

        # auto tight_layout and formats
        tight_layout = self.get_tight_layout()
        plot_format = self.get_plot_format()
        template_engine = self.get_template_engine()

        # retrieve all the methods for plot
        draw_methods = self.get_plot_methods()

        plots = []
        for dm in draw_methods:
            plot = core.subplots(
                plot_format=plot_format,
                template_engine=template_engine,
                **subplot_kwargs,
            )

            fig, ax = plot.figaxes()
            dm(fig=fig, ax=ax, **kwargs)

            if tight_layout:
                fig.tight_layout()

            plots.append(plot)

        if not plots:
            raise ImproperlyConfigured("No plot method provided")

        # retrieve the template plot name
        context_plot_name = self.get_context_plot_name()

        context[context_plot_name] = plots
        return context


class PlotMixin(MultiPlotMixin):

    #: The name of the plots inside the templates
    context_plot_name = "plot"

    #: The plot methods must match whit this regex
    plot_method_regex = r"^plot$"

    def get_context_data(self, **kwargs):
        """Overridden version of `MultiPlotMixin` to inject the
        plot into the template's context.
        """
        context = super().get_context_data(**kwargs)

        context_plot_name = self.get_context_plot_name()
        context[context_plot_name] = context.pop(context_plot_name)[0]

        return context


# =============================================================================
# THE VIEWS
# =============================================================================


class MultiPlotView(MultiPlotMixin, TemplateView):
    pass


class PlotView(PlotMixin, TemplateView):
    pass
