####################################################################
#
# This file is part of libraries-2021 dataexplorer, https://nds.iaea.org/dataexplorer/.
# Copyright (C) 2022 International Atomic Energy Agency (IAEA)
#
# Contact:    nds.contact-point@iaea.org
#
# Change logs:
#    First release: 2021-08-20
#    Update libraries: 2022-09-05, JENDL4.0 and TENDL2019 have been replced by JENDL5.0 and TENDL2021
#
####################################################################

import re
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.exceptions import PreventUpdate

# from app import app
from man import manual
from libraries.datahandle.list import (
    PARTICLE,
    ELEMS,
    reaction_list,
    elemtoz_nz,
    read_mass_range,
)

toast = html.Div(
    [
        dbc.Col(
            # dbc.Button("Tips", id="toast-toggle", color="primary", n_clicks=0,)
            [html.Div(html.P("Tips", id="toast-toggle"))]
        ),
        dbc.Col(
            dbc.Toast(
                [html.Div(manual)],
                id="toast",
                header="Tips for Data Explorer",
                icon="primary",
                dismissable=True,
                is_open=False,
                style={
                    "position": "absolute",
                    "top": 10,
                    "left": 10,
                    "width": 850,
                    "maxWidth": "1000px",
                    "zIndex": 1,
                },
                body_style={"background-color": "white", "font-size": "large"},
            )
        ),
    ]
)


sidehead = dbc.Row(
    [
        dbc.Col(
            html.A(
                [
                    html.Img(src=dash.get_asset_url("logo.png"), height="40px"),
                ],
                href="https://nds.iaea.org",
            )
        ),
        dbc.Col(html.P("Docs")),
        dbc.Col(toast),
        html.Label("Dataexplorer"),
        html.Br(),
    ],
)


page_urls = {
    # "Libraries-2022": "/dataexplorer/",
    "Libraries-2023": "/dataexplorer/reactions/xs",
    "EXFOR": "/dataexplorer/exfor",
}


lib_selections = [
    # {
    #     "label": "AGGRID",
    #     "value": "AGTEST",
    # },
    {
        "label": "Cross Section (XS)",
        "value": "SIG",
    },
    {
        "label": "Residual Production XS",
        "value": "Residual",
    },
    {"label": "Fission Yield (FY)", "value": "FY"},
    {"label": "Angular Distribution (DA)", "value": "DA"},
    {"label": "Energy Distribution (DE)", "value": "DE"},
    {
        "label": "Fission observables",
        "value": "FIS",
    },
    # {
    #     "label": "Ion Induced Reactions",
    #     "value": "ION",
    # },
]


lib_page_urls = {
    "AGTEST": "/dataexplorer/reactions/agtest",
    "SIG": "/dataexplorer/reactions/xs",
    "Residual": "/dataexplorer/reactions/residual",
    "FY": "/dataexplorer/reactions/fy",
    "DA": "/dataexplorer/reactions/da",
    "DE": "/dataexplorer/reactions/de",
    "FIS": "/dataexplorer/reactions/fission",
    # "ION": "/dataexplorer/reactions/ion",
}


navbar = html.Div(
    [
        html.H5(html.B("IAEA Nuclear Data Explorer")),
        html.P(
            "Nuclear Data Section | International Atomic Energy Agency.",
            style={"font-size": "medium"},
        ),
        html.P(
            "Hello, we will update frequentry.",
            style={"font-size": "smaller", "color": "gray"},
        ),
    ]
)


libs_navbar = html.Div(
    [
        html.H5(html.B("IAEA Nuclear Data Explorer")),
        html.P("Libraries 2023", style={"font-size": "medium"}),
        html.P(
            "Data have been renewed using a new exfor_parse",
            style={"font-size": "smaller", "color": "gray"},
        ),
    ]
)


exfor_navbar = html.Div(
    [
        html.H5(html.B("IAEA Nuclear Data Explorer")),
        html.P(
            "Experimental Nuclear Reaction Data (EXFOR) is compiled by the International Network of Nuclear Reaction Data Centres (NRDC) under the auspices of the International Atomic Energy Agency.",
            style={"font-size": "small"},
        ),
        html.P(
            "Number of entry: 2448, Number of dataset: 123456",
            style={"font-size": "smaller", "color": "gray"},
        ),
    ]
)


footer = html.Div(
    [
        html.Br(),
        html.Hr(style={"border": "3px", "border-top": "1px solid"}),
        "Copyright 2022, International Atomic Energy Agency - ",
        html.A(
            "Nuclear Data Section.", href="https://nds.iaea.org/", className="text-dark"
        ),
        html.Br(),
        html.A(
            "Terms of use.",
            href="https://nucleus.iaea.org/Pages/Others/Terms-Of-Use.aspx",
            className="text-dark",
        ),
        html.Br(),
        "email:",
        html.A(
            "nds.contact-point@iaea.org",
            href="mailto:nds.contact-point@iaea.org",
            className="text-dark",
        ),
        html.Br(),
    ],
    style={"text-align": "center"},
    className="text-dark",
)


def dict_merge(dicts_list):
    d = {**dicts_list[0]}
    for entry in dicts_list[1:]:
        # print("entry:", entry)
        for k, v in entry.items():
            d[k] = (
                [d[k], v]
                if k in d and type(d[k]) != list
                else [*d[k] + v]
                if k in d
                else v
            )
    return d


def data_length_unify(data_dict):
    data_len = []
    new_list = []
    data_list = data_dict["data"]

    for i in data_list:
        data_len += [len(i)]

    for l in range(len(data_len)):
        if data_len[l] < max(data_len):
            data_list[l] = data_list[l] * max(data_len)

    ## Check if list length are all same
    it = iter(data_list)
    the_next = len(next(it))
    assert all(len(l) == the_next for l in it)

    ## overwrite the "data" block by extended list
    data_dict["data"] = data_list

    return data_dict


mass_range = read_mass_range()


def input_check(type, elem, mass, reaction):
    if not type or not elem or not mass or not reaction:
        # if any(not i for i in (type, elem, mass, reaction)):
        raise PreventUpdate

    if elem.capitalize() not in ELEMS:
        raise PreventUpdate

    if not mass:
        raise PreventUpdate

    if elem and mass:
        min = mass_range[elemtoz_nz(elem.capitalize())]["min"]
        max = mass_range[elemtoz_nz(elem.capitalize())]["max"]

        if not int(min) < int(get_number_from_string(mass)) < int(max):
            raise PreventUpdate

    else:
        raise PreventUpdate

    return elem.capitalize(), mass.lower(), reaction.upper()


def generate_reactions():
    options = [
        {"label": f"{proj.lower()},n", "value": f"{proj.lower()},n"}
        if proj != "N" and reac == "INL"
        else {
            "label": f"{proj.lower()},{reac.lower()}",
            "value": f"{proj.lower()},{reac.lower()}",
        }
        for proj in PARTICLE
        for reac in reaction_list.keys()
    ]
    return options


def energy_range_conversion(energy_range):
    if len(energy_range) == 2:
        if energy_range[0] <= 1:
            lower = 0
        else:
            lower = 10 ** energy_range[0] / 1e6

        upper = 10 ** energy_range[1] / 1e6

        return lower, upper

    else:
        return None, None


def get_number_from_string(str):
    return re.sub(r"\D+", "", str)


def get_str_from_string(str):
    return re.sub(r"\d+", "", str)
