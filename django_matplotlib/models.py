#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2020, Juan B Cabral & QuatroPe
# License: BSD-3-Clause
#   Full Text: https://github.com/quatrope/djmpl/blob/master/LICENSE


# =============================================================================
# DOCS
# =============================================================================

"""Models utilities to integrate matplolib plots into django models

"""

__all__ = ["MatplotlibManager"]


# =============================================================================
# IMPORTS
# =============================================================================

from django.db import models

from .core import subplots


# =============================================================================
# MANAGER
# =============================================================================

class MatplotlibManager(models.Manager):

    def get_draw_methods(self):
        draw_methods = self.draw_methods or ["draw_plot"]
        methods = [getattr(self, m) for m in draw_methods]
        return methods

    def get_plot(self, plot_format):
        """Return the plot to be injected in the context_data"""
        return subplots(plot_format=plot_format)

    def draw_plot(self, fig, ax):
        """Draw the plot"""
        raise NotImplementedError("Please implement the draw_plot method")

    def plot_all(self, plot_format="png", tight_layout=True):
        draw_methods = self.get_draw_methods()
        plots = []
        for dm in draw_methods:
            plot = self.get_plot(plot_format=plot_format)
            fig, ax = plot.figaxes()
            dm(fig=fig, ax=ax)
            if tight_layout:
                fig.tight_layout()
            plots.append(plot)
        return plots
