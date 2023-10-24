####################################################################
#
# This file is part of libraries-2023 dataexplorer, https://nds.iaea.org/dataexplorer/.
# Copyright (C) 2022 International Atomic Energy Agency (IAEA)
#
# Contact:    nds.contact-point@iaea.org
#
####################################################################

import pandas as pd
import plotly.express as px
import os
import json

from config import MT_PATH_JSON, MT50_PATH_JSON


# ------------------------------------------------------------------------------
# MT Numbers
# ------------------------------------------------------------------------------
resid_mt_range = {"N": list(range(50,90)) , 
            "P": list(range(600,649)), 
            "D": list(range(650,699)), 
            "T": list(range(700,749)), 
            "H": list(range(750,799)), 
            "A": list(range(800,849)), 
            "G": [102]
            } # not sure about photon induced case


def read_mt_json():
    if os.path.exists(MT_PATH_JSON):
        with open(MT_PATH_JSON) as map_file:
            return json.load(map_file)


def reaction_list(projectile):
    if not projectile:
        return read_mt_json()
    
    assert len(projectile) == 1

    all = read_mt_json()
    # "EL": {
    #   "mt": "2",
    #   "reaction": "(n,elas.)",
    #   "sf5-8": null
    #  },
    
    all = { "N" if projectile.upper()!="N" and k=="INL" else k : i for k, i in all.items()   }
    partial = {}

    for p in resid_mt_range.keys():
        for n in range(len(resid_mt_range[p.upper()])):
            partial[f"{p.upper()}{str(n)}"] = {
                                        "mt": str(resid_mt_range[p.upper()][n]),
                                        "reaction": f"({projectile.lower()},{p.lower()}{str(n)})", 
                                        "sf5-8": "PAR,SIG,,"
                                        }

    return dict(**all, **partial)

# def read_mt50_json():
#     if os.path.exists(MT50_PATH_JSON):
#         with open(MT50_PATH_JSON) as map_file:
#             return json.load(map_file)


# mt50_list = read_mt50_json()

LIB_LIST_MAX = [
    "tendl.2021",
    "endfb8.0",
    "jeff3.3",
    "jendl5.0",
    "iaea.2019",
    "cendl3.2",
    "irdff2.0",
    "iaea.pd",
]

LIB_LIST_MIN = [
    "endfb8.0",
    "jendl5.0",
    "jeff3.3",
    "iaea.pd",
    "irdff2.0",
    "cendl3.2",
    "tendl.2021",
]

LIB_LIST_RP = [
    "tendl.2021",
    "iaea.2019",
    "iaea.pd",
    "endfb8.0",
    "jendl5.0",
    "irdff2.0",
]

LIB_LIST_FY = ["endfb8.0", "jeff3.3", "jendl5.0"]

LIB_LIST_MAX.sort(reverse=True)


# ------------------------------------------------------------------------------
# Selection for FPY
# ------------------------------------------------------------------------------
MT_BRANCH_LIST_FY = {
            "Primary":     {"branch": "PRE", "mt": "460"},
            "Independent": {"branch": "IND", "mt": "454"},
            "Cumulative":  {"branch": "CUM", "mt": "459"},
              }



MT_LIST_FY = {"PRE": "460", "IND": "454", "CUM": "459"}


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
