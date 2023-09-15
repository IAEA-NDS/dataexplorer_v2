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
from dash import html
from dash.exceptions import PreventUpdate
import urllib.parse


from man import manual
from submodules.utilities.elem import ELEMS, elemtoz_nz
from submodules.utilities.mass import mass_range
from libraries.datahandle.list import reaction_list


# ------------------------------------------------------------------------------
# Incident particles
# ------------------------------------------------------------------------------

PARTICLE = ["N", "P", "D", "T", "A", "H", "G"]
PARTICLE_FY = ["N", "0", "P", "D", "T", "A", "H", "G"]


# ------------------------------------------------------------------------------
# Isomeric state
# ------------------------------------------------------------------------------

ISOMERIC = ["", "g", "m", "m2"]


# ------------------------------------------------------------------------------
# Name of libraries used in each app
# ------------------------------------------------------------------------------

url_basename = dash.get_relative_path("/")


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
                    html.Img(src=dash.get_asset_url("logo.png"), height="30px"),
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
    "Libraries-2023": url_basename + "reactions/xs",
    "EXFOR": url_basename + "exfor",
}


lib_selections = [
    {
        "label": "Cross Section (XS)",
        "value": "XS",
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
]


lib_page_urls = {
    "XS": url_basename + "reactions/xs",
    "Residual": url_basename + "reactions/residual",
    "FY": url_basename + "reactions/fy",
    "DA": url_basename + "reactions/da",
    "DE": url_basename + "reactions/de",
    "FIS": url_basename + "reactions/fission",
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
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        [
                            html.A(
                                [
                                    html.Img(
                                        src=dash.get_asset_url("logo.png"),
                                        height="20px",
                                    ),
                                ],
                                href="https://nds.iaea.org",
                            ),
                            " Libraries 2023",
                        ],
                    ),
                    width=2,
                    style={"font-size": "medium"},
                ),
                dbc.Col(
                    html.Div(
                        [
                            "Buildt with ",
                            html.A(
                                "endftables",
                                href="https://nds.iaea.org/talys/",
                                # className="text-dark",
                            ),
                            " and ",
                            html.A(
                                "exforparser",
                                href="https://github.com/shinokumura/exforparser",
                                # className="text-dark",
                            ),
                            ".",
                        ],
                        style={
                            "font-size": "smaller",
                            "color": "gray",
                            "text-align": "left",
                        },
                    ),
                ),
            ]
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


def remove_query_parameter(url, param):
    # クエリ文字列から指定されたパラメータを削除するユーティリティ関数
    url_parts = urllib.parse.urlparse(url)
    query_params = urllib.parse.parse_qs(url_parts.query)
    query_params.pop(param, None)
    updated_query = urllib.parse.urlencode(query_params, doseq=True)
    return url_parts._replace(query=updated_query).geturl()


def limit_number_of_datapoints(points, df):
    if points <= 100:
        return df

    elif 100 < points <= 1000:
        nskip = int(points / 100)

        return df.iloc[::nskip, :]

    elif points > 1000:
        nskip = int(points / 1000)
        return df.iloc[::nskip, :]

    else:
        return df
