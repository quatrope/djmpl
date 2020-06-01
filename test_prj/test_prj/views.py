#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2020, Juan B Cabral & QuatroPe
# License: BSD-3-Clause
#   Full Text: https://github.com/quatrope/djmpl/blob/master/LICENSE

# =============================================================================
# DOCS
# =============================================================================

# =============================================================================
# IMPORTS
# =============================================================================


import django_matplotlib as djmpl
from django.views.generic.base import TemplateView

# =============================================================================
# THE VIEWS
# =============================================================================


class PlotMixinTestView(djmpl.PlotMixin, TemplateView):

    plot_data = [1, 2, 3]
    template_name = "test_djmpl/SinglePlot.html"

    def plot(self, data, fig, ax):
        ax.plot(data)
