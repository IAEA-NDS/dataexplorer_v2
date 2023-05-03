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
import re
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from collections import OrderedDict
from dash.exceptions import PreventUpdate

from common import sidehead, footer, libs_navbar, page_urls, lib_selections, lib_page_urls, input_check, energy_range_conversion
from libraries2023.datahandle.list import (
    PARTICLE,
    read_mt_json,
    read_mass_range,
)

from config import BASE_URL
from libraries2023.datahandle.tabs import create_tabs
from libraries2023.datahandle.figs import default_chart, default_axis
from sql.queries import reaction_query, get_entry_bib, data_query, lib_query, lib_xs_data_query

## Registration of page
dash.register_page(__name__, path="/", title='IAEA Nuclear Dataexplorer', description='Nuclear reaction experimental and evaluated data plotter')

layout = html.Div([
    dbc.Row(dbc.Col(html.H1("IAEA Nuclear Dataexplorer"), width=6), justify="center",),
    dbc.Row([
        dbc.Card(
            [
                dbc.CardImg(
                    src=dash.get_asset_url("1.jpg"),
                    top=True,
                    style={"opacity": 0.3, "width": "450px", "height": "200px"},
                ),
                dbc.CardBody(
                    [
                        html.H4("Nulcear reaction cross section plot", className="card-title"),
                        html.P(
                            "Nuclear reaction cross section ",
                            className="card-text",
                        ),
                        dbc.Button("Go to plot", href="reactions/xs", color="primary"),
                    ],
                ),
            ],
            style={"width": "30%", "height": "200px"},
        ),
        dbc.Card(
            [
                dbc.CardImg(
                    src=dash.get_asset_url("2.jpg"),
                    top=True,
                    style={"opacity": 0.3, "width": "450px", "height": "200px"},
                ),

                dbc.CardBody(
                    [
                        html.H4("Residual production cross section", className="card-title"),
                        html.P(
                            "Cross section plot filtered by a residual product.",
                            className="card-text",
                        ),
                        dbc.Button("Go to plot", href="reactions/residual", color="primary"),
                    ],
                ),

            ],
            style={"width": "30%"},
        ),
    ],className="mb-4",justify="center",),
    dbc.Row([
        dbc.Card(
            [
                dbc.CardImg(
                    src=dash.get_asset_url("3.png"),
                    top=True,
                    style={"opacity": 0.3, "width": "450px", "height": "200px"},
                ),
                dbc.CardBody(
                    [
                        html.H4("Fission product yield", className="card-title"),
                        html.P(
                            "Nuclear reaction cross section ",
                            className="card-text",
                        ),
                        dbc.Button("Go to plot", href="reactions/xs", color="success"),
                    ],
                ),
            ],
            style={"width": "30%"},
        ),
        dbc.Card(
            [
                dbc.CardImg(
                    src=dash.get_asset_url("4.jpg"),
                    top=True,
                    style={"opacity": 0.3, "width": "450px", "height": "200px"},
                ),

                dbc.CardBody(
                    [
                        html.H4("Angular distribution", className="card-title"),
                        html.P(
                            "Cross section plot filtered by a residual product.",
                            className="card-text",
                        ),
                        dbc.Button("Go to plot", href="reactions/residual", color="success"),
                    ],
                ),
            ],
            style={"width": "30%"},
        ),
    ],className="mb-4",justify="center",),
    dbc.Row([
        dbc.Card(
            [
                dbc.CardImg(
                    src=dash.get_asset_url("5.jpg"),
                    top=True,
                    style={"opacity": 0.3, "width": "450px", "height": "200px"},
                ),
                dbc.CardBody(
                    [
                        html.H4("Energy distribution", className="card-title"),
                        html.P(
                            "Nuclear reaction cross section ",
                            className="card-text",
                        ),
                        dbc.Button("Go somewhere", href="reactions/xs", color="warning"),
                    ],
                ),
            ],
            style={"width": "30%"},
        ),
        dbc.Card(
            [
                dbc.CardImg(
                    src=dash.get_asset_url("6.jpg"),
                    top=True,
                    style={"opacity": 0.3, "width": "450px", "height": "200px"},
                ),
                dbc.CardBody(
                    [
                        html.H4("EXFOR statistics", className="card-title"),
                        html.P(
                            "Cross section plot filtered by a residual product.",
                            className="card-text",
                        ),
                        dbc.Button("Go somewhere", href="reactions/residual", color="warning"),
                    ],
                ),
            ],
            style={"width": "30%"},
        ),
    ],className="mb-4",justify="center",)

], className="mx-auto" )