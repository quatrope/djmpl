#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2020, Juan B Cabral & QuatroPe
# License: BSD-3-Clause
#   Full Text: https://github.com/quatrope/djmpl/blob/master/LICENSE


# =============================================================================
# DOCS
# =============================================================================

"""Tests for django_matplotlib.core

"""

# =============================================================================
# IMPORTS
# =============================================================================

import pytest

from django.utils.safestring import SafeString

from pyquery import PyQuery as pq

import jinja2

import django_matplotlib as djmpl
from django_matplotlib import core


# =============================================================================
# TESTS
# =============================================================================

@pytest.mark.parametrize(
    "engine, safe_type",
    [("django", SafeString), ("jinja2", jinja2.Markup), ("str", str)]
)
def test_png(engine, safe_type):
    plot = djmpl.subplots(
        plot_format="png",
        template_engine=engine)
    html = plot.to_html()
    assert isinstance(html, safe_type)

    div = pq(html)

    assert len(div) == 1
    assert div[0].tag == "div"
    assert div.has_class("djmpl")
    assert div.has_class("djmpl-png")

    children = div[0].getchildren()
    assert len(children) == 1

    img = children[0]
    assert img.tag == "img"
    assert img.attrib["src"].split(",", 1)[0] == "data:image/png;base64"


@pytest.mark.parametrize(
    "engine, safe_type",
    [("django", SafeString), ("jinja2", jinja2.Markup), ("str", str)]
)
def test_svg(engine, safe_type):
    plot = djmpl.subplots(
        plot_format="svg",
        template_engine=engine)
    html = plot.to_html()
    assert isinstance(html, safe_type)

    div = pq(html)

    assert len(div) == 1
    assert div[0].tag == "div"
    assert div.has_class("djmpl")
    assert div.has_class("djmpl-svg")

    children = div[0].getchildren()
    assert len(children) == 3

    img = children[-1]
    assert img.tag == "svg"


@pytest.mark.parametrize(
    "engine, safe_type",
    [("django", SafeString), ("jinja2", jinja2.Markup), ("str", str)]
)
def test_mpld3(engine, safe_type):
    plot = djmpl.subplots(
        plot_format="mpld3", template_engine=engine)
    html = plot.to_html()
    assert isinstance(html, safe_type)

    div = pq(html)

    assert len(div) == 1
    assert div[0].tag == "div"
    assert div.has_class("djmpl")
    assert div.has_class("djmpl-mpld3")

    children = div[0].getchildren()
    assert len(children) == 3

    img = children[-1]
    assert img.tag == "script"


@pytest.mark.parametrize("fmt", core.AVAILABLE_FORMATS)
@pytest.mark.parametrize(
    "engine", list(core.TEMPLATES_FORMATERS) + list(core.TEMPLATE_ALIAS))
def test_valid_engine_and_format(fmt, engine):
    plt = djmpl.subplots(plot_format=fmt, template_engine=engine)
    assert plt.plot_format == fmt
    assert plt.template_engine == core.template_by_alias(engine)


@pytest.mark.parametrize(
    "engine", list(core.TEMPLATES_FORMATERS) + list(core.TEMPLATE_ALIAS))
def test_invalid_and_format(engine):
    with pytest.raises(ValueError):
        djmpl.subplots(plot_format="%NOT-EXISTS%", template_engine=engine)


@pytest.mark.parametrize("fmt", core.AVAILABLE_FORMATS)
def test_invalid_engine(fmt):
    with pytest.raises(core.EngineNotSupported):
        djmpl.subplots(plot_format=fmt, template_engine="%NOT-EXISTS%")
