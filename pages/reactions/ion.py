####################################################################
#
# This file is part of libraries-2021 dataexplorer, https://nds.iaea.org/dataexplorer/.
# Copyright (C) 2022 International Atomic Energy Agency (IAEA)
#
# Contact:    nds.contact-point@iaea.org
#
####################################################################

import pandas as pd
import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from collections import OrderedDict
from operator import getitem
from dash.exceptions import PreventUpdate

from common import (
    sidehead,
    footer,
    libs_navbar,
    page_urls,
    lib_selections,
    lib_page_urls,
    input_check,
)
from libraries.datahandle.list import (
    PARTICLE,
    elemtoz_nz,
    read_mass_range,
)
from exforparser.sql.models import Exfor_Bib, Exfor_Data, Exfor_Reactions
from config import session, session_lib, engines, BASE_URL
from libraries.datahandle.tabs import create_tabs
from libraries.datahandle.figs import default_chart, default_axis


## Registration of page
# dash.register_page(__name__, path="/reactions/ion")


def get_projectile():
    return [
        p.projectile for p in session().query(Exfor_Reactions.projectile).distinct()
    ]


projectile = get_projectile()


def get_reactions():
    # return {r.process.split(",")[0]: r.process.split(",")[1] for r in session().query(Exfor_Reactions.process).distinct() if len(r.process.split(",")[0]) != 1}
    return [
        r.process
        for r in session().query(Exfor_Reactions.process).distinct()
        if len(r.process.split(",")[0]) != 1
    ]


def input_lib(**query_strings):
    return [
        dcc.Dropdown(
            id="reaction_category",
            # options=[{"label": j, "value": i} for i, j in sorted(WEB_CATEGORY.items())],
            options=lib_selections,
            placeholder="Select reaction",
            persistence=True,
            persistence_type="memory",
            value="ION",
            style={"font-size": "small", "width": "100%"},
        ),
        dcc.Input(
            id="target_elem",
            placeholder="Target element: C, c, Pd, pd, PD",
            persistence=True,
            persistence_type="memory",
            value=query_strings["target_elem"]
            if query_strings.get("target_elem")
            else "Au",
            style={"font-size": "small", "width": "100%"},
        ),
        dcc.Input(
            id="target_mass",
            placeholder="Target mass: 0:natural, m:metastable",
            persistence=True,
            persistence_type="memory",
            value=query_strings["target_mass"]
            if query_strings.get("target_mass")
            else "197",
            style={"font-size": "small", "width": "100%"},
        ),
        dcc.Dropdown(
            id="reaction",
            options=sorted(get_reactions()),
            # options=["n,g", "n,tot"],
            placeholder="Reaction e.g. (n,g)",
            persistence=True,
            persistence_type="memory",
            value=query_strings["reaction"]
            if query_strings.get("reaction")
            else "6-C-12",
            style={"font-size": "small", "width": "100%"},
        ),
        # dcc.Dropdown(
        #     id="reac_branch",
        #     options=[{"label": reac, "value": reac} for reac in reaction_list],
        #     placeholder="Options",
        #     persistence=True,
        #     persistence_type="memory",
        #     value="",
        #     style={"font-size": "small", "width": "100%"},
        # ),
        html.Br(),
        html.Br(),
        html.P("Fileter EXFOR records by"),
        html.Label("Energy Range"),
        dcc.RangeSlider(
            id="energy_range",
            min=0,
            max=3,
            marks={0: "eV", 1: "keV", 2: "MeV", 3: "GeV"},
            value=[0, 3],
            # tooltip={"placement": "bottom", "always_visible": True},
            vertical=False,
        ),
        html.Br(),
        html.Label("Year Range"),
        dcc.RangeSlider(
            id="year_range",
            min=1930,
            max=2023,
            marks={
                i: f"Label {i}" if i == 1 else str(i) for i in range(1930, 2025, 40)
            },
            value=[1930, 2023],
            tooltip={"placement": "bottom", "always_visible": True},
            vertical=False,
        ),
    ]


main_fig_ion = dcc.Graph(
    id="main_fig_lib",
    config={
        "displayModeBar": True,
        "scrollZoom": True,
        "modeBarButtonsToAdd": ["drawline", "drawopenpath", "eraseshape"],
        "modeBarButtonsToRemove": ["lasso2d"],
    },
    figure={
        "layout": {
            "title": "Please select target and reaction.",
            "height": 600,
        }
    },
)


right_layout_ion = [
    libs_navbar,
    html.Hr(style={"border": "3px", "border-top": "1px solid"}),
    html.Div(id="test_cont"),
    # Log/Linear switch
    dbc.Row(
        [
            dbc.Col(html.Label("X:"), width="auto"),
            dbc.Col(
                dcc.RadioItems(
                    id="xaxis_type",
                    options=[
                        {"label": i, "value": i.lower()} for i in ["Linear", "Log"]
                    ],
                    value="log",
                    persistence=True,
                    persistence_type="memory",
                    labelStyle={"display": "inline-block"},
                ),
                width="auto",
            ),
            dbc.Col(html.Label("Y:"), width="auto"),
            dbc.Col(
                dcc.RadioItems(
                    id="yaxis_type",
                    options=[
                        {"label": i, "value": i.lower()} for i in ["Linear", "Log"]
                    ],
                    value="log",
                    persistence=True,
                    persistence_type="memory",
                    labelStyle={"display": "inline-block"},
                ),
                width="auto",
            ),
        ]
    ),
    dcc.Loading(
        children=main_fig_ion,
        type="circle",
    ),
    html.Hr(style={"border": "3px", "border-top": "1px solid"}),
    create_tabs(""),
    html.Hr(style={"border": "3px", "border-top": "1px solid"}),
    footer,
]


def layout(**query_strings):
    return html.Div(
        [
            dcc.Location(id="location_ion"),
            dbc.Row(
                [
                    ### left panel
                    dbc.Col(
                        [
                            sidehead,
                            html.Div(
                                [
                                    html.Label("Dataset"),
                                    dcc.Dropdown(
                                        id="dataset",
                                        options=list(page_urls.keys()),
                                        value="Libraries-2023",
                                        style={"font-size": "small"},
                                        persistence=True,
                                        persistence_type="memory",
                                    ),
                                    html.Div(input_lib(**query_strings)),
                                ],
                                style={"margin-left": "10px"},
                            ),
                        ],
                        style={
                            "height": "100vh",
                            "background-color": "hsla(30,40%,90%,0.5)",
                        },
                        width=2,
                    ),
                    ### Right panel
                    dbc.Col(
                        [
                            html.Div(
                                id="right_layout",
                                children=right_layout_ion,
                                style={"margin-right": "20px", "margin-left": "10px"},
                            ),
                        ],
                        width=10,
                    ),
                ]
            ),
        ],
        style={"height": "100vh"},
    )
