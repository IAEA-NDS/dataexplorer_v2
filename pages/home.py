####################################################################
#
# This file is part of libraries-2021 dataexplorer, https://nds.iaea.org/dataexplorer/.
# Copyright (C) 2022 International Atomic Energy Agency (IAEA)
#
# Contact:    nds.contact-point@iaea.org
#
####################################################################


import dash
from dash import html, dcc
import dash_bootstrap_components as dbc


from common import footer, libs_navbar

## Registration of page
dash.register_page(__name__, path="/", title='IAEA Nuclear Dataexplorer', description='Nuclear reaction experimental and evaluated data plotter')

layout = html.Div([
    # libs_navbar,
    dbc.Row(dbc.Col(html.H1("IAEA Nuclear Dataexplorer"), width=6), justify="center",),
    dbc.Row([
        dbc.Card(
            [
                dbc.CardImg(
                    src=dash.get_asset_url("1.jpg"),
                    top=True,
                    style={"opacity": 0.3, "width": "400px", "height": "200px"},
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
                    style={"opacity": 0.3, "width": "400px", "height": "200px"},
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
                    style={"opacity": 0.3, "width": "400px", "height": "200px"},
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
                    style={"opacity": 0.3, "width": "400px", "height": "200px"},
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
                    style={"opacity": 0.3, "width": "400px", "height": "200px"},
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
                    style={"opacity": 0.3, "width": "400px", "height": "200px"},
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
    ],className="mb-4",justify="center",),
    html.Hr(style={"border": "3px", "border-top": "1px solid"}),
    dbc.Row([
    dbc.Card(
        [
            dbc.CardImg(
                src=dash.get_asset_url("api.jpg"),
                top=True,
                style={"opacity": 0.3, "width": "400px", "height": "200px"},
            ),
            dbc.CardBody(
                [
                    html.H4("API Manual", className="card-title"),
                    html.P(
                        "Nuclear reaction cross section ",
                        className="card-text",
                    ),
                    dbc.Button("Go to plot", href="/api_manual", color="success"),
                ],
            ),
        ],
        style={"width": "30%"},
    ),
    ],className="mb-4",justify="center",),


    footer,
  

], className="mx-auto" )