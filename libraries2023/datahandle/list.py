####################################################################
#
# This file is part of libraries-2021 dataexplorer, https://nds.iaea.org/dataexplorer/.
# Copyright (C) 2022 International Atomic Energy Agency (IAEA)
#
# Contact:    nds.contact-point@iaea.org
#
####################################################################

import pandas as pd
import plotly.express as px
import os
import json

from config import MT_PATH_JSON

# ------------------------------------------------------------------------------
# Element
#
ELEMS = [
    "H",
    "He",
    "Li",
    "Be",
    "B",
    "C",
    "N",
    "O",
    "F",
    "Ne",
    "Na",
    "Mg",
    "Al",
    "Si",
    "P",
    "S",
    "Cl",
    "Ar",
    "K",
    "Ca",
    "Sc",
    "Ti",
    "V",
    "Cr",
    "Mn",
    "Fe",
    "Co",
    "Ni",
    "Cu",
    "Zn",
    "Ga",
    "Ge",
    "As",
    "Se",
    "Br",
    "Kr",
    "Rb",
    "Sr",
    "Y",
    "Zr",
    "Nb",
    "Mo",
    "Tc",
    "Ru",
    "Rh",
    "Pd",
    "Ag",
    "Cd",
    "In",
    "Sn",
    "Sb",
    "Te",
    "I",
    "Xe",
    "Cs",
    "Ba",
    "La",
    "Ce",
    "Pr",
    "Nd",
    "Pm",
    "Sm",
    "Eu",
    "Gd",
    "Tb",
    "Dy",
    "Ho",
    "Er",
    "Tm",
    "Yb",
    "Lu",
    "Hf",
    "Ta",
    "W",
    "Re",
    "Os",
    "Ir",
    "Pt",
    "Au",
    "Hg",
    "Tl",
    "Pb",
    "Bi",
    "Po",
    "At",
    "Rn",
    "Fr",
    "Ra",
    "Ac",
    "Th",
    "Pa",
    "U",
    "Np",
    "Pu",
    "Am",
    "Cm",
    "Bk",
    "Cf",
    "Es",
    "Fm",
    "Md",
    "No",
    "Lr",
    "Rf",
    "Db",
    "Sg",
    "Bh",
    "Hs",
    "Mt",
    "Ds",
    "Rg",
]


def ztoelem(z):
    if z == 0:
        elem_name = "n"
    else:
        try:
            z = z - 1
            elem_name = ELEMS[z]
        except ValueError:
            elem_name = ""
    return elem_name


def elemtoz(elem):
    try:
        z = ELEMS.index(elem)
        z = z + 1
        z = str(z).zfill(3)
    except ValueError:
        z = ""
    return z


def elemtoz_nz(elem):
    try:
        z = ELEMS.index(elem)
        z = z + 1
        z = str(z)
    except ValueError:
        z = ""
    return z


# ------------------------------------------------------------------------------
# Mass
# ------------------------------------------------------------------------------
def read_mass_range():
    mass_range = {}
    with open("A_min_max.txt") as f:
        for z in f.readlines():
            if z.startswith("#"):
                continue
            z_mass = z.split(",")
            mass_range[z_mass[0]] = {"min": z_mass[1].strip(), "max": z_mass[2].strip()}
    return mass_range


# ------------------------------------------------------------------------------
# MT / MF
# ------------------------------------------------------------------------------

def read_mt_json():
    if os.path.exists(MT_PATH_JSON):
        with open(MT_PATH_JSON) as map_file:
            return json.load(map_file)
reaction_list = read_mt_json()


# ------------------------------------------------------------------------------
# Incident particles
# ------------------------------------------------------------------------------

PARTICLE    = ["N", "P", "D", "T", "A", "H", "G"]
PARTICLE_FY = ["N", "0", "P", "D", "T", "A", "H", "G"]


# ------------------------------------------------------------------------------
# Isomeric state
# ------------------------------------------------------------------------------

ISOMERIC = ["", "g", "m", "m2"]


# ------------------------------------------------------------------------------
# Name of libraries used in each app
# ------------------------------------------------------------------------------

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
