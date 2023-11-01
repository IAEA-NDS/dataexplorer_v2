####################################################################
#
# This file is part of libraries-2023 dataexplorer, https://nds.iaea.org/dataexplorer/.
# Copyright (C) 2022 International Atomic Energy Agency (IAEA)
#
# Contact:    nds.contact-point@iaea.org
#
####################################################################

import plotly.express as px


# ------------------------------------------------------------------------------
# MT Numbers
# ------------------------------------------------------------------------------
# Moved to submodules in git@https://github.com/shinokumura/exparser-submodule

# ------------------------------------------------------------------------------
# Selection for FPY
# ------------------------------------------------------------------------------
# Moved to page_commmon


# ------------------------------------------------------------------------------
# Color generation
# ------------------------------------------------------------------------------
def hex_rgba(hex, transparency):
    col_hex = hex.lstrip("#")
    col_rgb = list(int(col_hex[i : i + 2], 16) for i in (0, 2, 4))
    col_rgb.extend([transparency])
    areacol = tuple(col_rgb)
    return areacol


def next_col(cols):
    while True:
        for col in cols:
            yield col


def color_cycle(colors):
    # colors = px.colors.qualitative.Dark24
    # colors = px.colors.sequential.gray
    # print(colors)
    rgba = [hex_rgba(c, transparency=1.0) for c in colors]
    colCycle = ["rgba" + str(elem) for elem in rgba]
    line_color = next_col(cols=colCycle)
    return line_color


def color_libs(lib):
    # line_color = color_cycle()
    colors = px.colors.qualitative.Light24
    if "tendl" in lib:
        colors = [
            "#606060",
            "#808080",
            "#606060",
            "#A0A0A0",
            "#C0C0C0",
            "#E0E0E0",
            "#404040",
        ]
    if "endfb" in lib:
        colors = [
            "#2E91E5",
            "#57A7EA",
            "#81BDEF",
            "#2474B7",
            "#1B5789",
            "#123A5B",
            "#D5E9F9",
        ]
    if "jendl" in lib:
        colors = [
            "#1CA71C",
            "#49B849",
            "#8DD38D",
            "#76CA76",
            "#168516",
            "#106410",
            "#0B420B",
        ]
    if "jeff" in lib:
        colors = [
            "#E15F99",
            "#E77FAD",
            "#ED9FC1",
            "#F3BFD6",
            "#B44C7A",
            "#87395B",
            "#5A263D",
        ]
    if "cendl" in lib:
        colors = ["#cbaf48", "#c1a955", "#b8a261", "#ad9c6c"]
    if "irdff" in lib:
        colors = ["#A9A9A9", "#778899", "#A9A9A9", "#DCDCDC"]
    if "iaea" in lib:
        colors = ["#33CCCC", "#00CCCC", "#66CCCC", "#99FFFF", "#CCFFFF"]

    rgba = [hex_rgba(c, transparency=1.0) for c in colors]
    colCycle = ["rgba" + str(elem) for elem in rgba]
    line_color = next_col(cols=colCycle)

    return line_color
