#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2020, Juan B Cabral & QuatroPe
# License: BSD-3-Clause
#   Full Text: https://github.com/quatrope/djmpl/blob/master/LICENSE

# =============================================================================
# DOCS
# =============================================================================

"""Settings for djmatplotlib

"""

# =============================================================================
# IMPORTS
# =============================================================================

from django.conf import settings
from django.utils.safestring import mark_safe

import jinja2


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
    "django.template.backends.django.DjangoTemplates": mark_safe,
    "django.template.backends.jinja2.Jinja2": jinja2.Markup,
    "str": str,
}

#: Map the template engine name to a function that make "safe" to render
#: the image into the final HTML.
TEMPLATE_ALIAS = {
    "django": "django.template.backends.django.DjangoTemplates",
    "jinja2": "django.template.backends.jinja2.Jinja2",
    "str": "str",
}

#: Default template engine for render the plots. By default uses the
#: same as the default engine in ``settings.TEMPLATES```, this can
#: be changed by ``settings.DJMPL_TEMPLATE_ENGINE``` variable.
DJMPL_TEMPLATE_ENGINE: str = getattr(
    settings, "DJMPL_TEMPLATE_ENGINE", DEFAULT_TEMPLATE_ENGINE
)
