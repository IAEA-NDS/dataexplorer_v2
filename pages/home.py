####################################################################
#
# This file is part of libraries-2021 dataexplorer, https://nds.iaea.org/dataexplorer/.
# Copyright (C) 2024 International Atomic Energy Agency (IAEA)
#
# Contact:    nds.contact-point@iaea.org
#
####################################################################


import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc


from pages_common import footer


## Registration of page
dash.register_page(
    __name__,
    path="/home",
    title="IAEA Nuclear Dataexplorer",
    description="Nuclear reaction experimental and evaluated data plotter",
)


nav = dbc.NavbarSimple(
    [
        dbc.DropdownMenu(
            [
                dbc.DropdownMenuItem(dbc.NavLink("Cross Section", href="reactions/xs")),
                dbc.DropdownMenuItem(
                    dbc.NavLink(
                        "Residual Production Cross Section", href="reactions/residual"
                    )
                ),
                dbc.DropdownMenuItem(dbc.NavLink("Fission Yield", href="reactions/fy")),
            ],
            label="Dataexplorer",
            nav=True,
        ),
        dbc.DropdownMenu(
            [
                dbc.DropdownMenuItem(dbc.NavLink("EXFOR Entry Search", href="exfor")),
                dbc.DropdownMenuItem(
                    dbc.NavLink("EXFOR Reaction Search", href="exfor/search")
                ),
                dbc.DropdownMenuItem(dbc.NavLink("Geo", href="exfor/geo")),
            ],
            label="EXFOR Viewer",
            nav=True,
        ),
        dbc.DropdownMenu(
            [
                dbc.DropdownMenuItem(
                    dbc.NavLink("Dataexplorer API", href="api/reactions")
                ),
                dbc.DropdownMenuItem(dbc.NavLink("EXFOR API", href="api/exfor")),
                dbc.DropdownMenuItem(dbc.NavLink("RIPLE-3 API", href="api/ripl3")),
            ],
            label="APIs",
            nav=True,
        ),
    ],
    brand="IAEA NDS",
    brand_href="nds.iaea.org",
    color="primary",
    dark=True,
    className="bi bi-list mobile-nav-toggle",
)


layout = dbc.Container(
    [
        dcc.Location(id="location"),
        nav,
        dbc.Row(
            dbc.Col(
                [
                    html.H2(
                        "IAEA Nuclear Dataexplorer/EXFOR Viewer",
                        className="text-center",
                    ),
                    html.P(
                        "Data Viewer for LIBRARIES made for TALYS development and Data Repository for Experimental Nuclear Reaction data",
                        className="text-center",
                    ),
                ]
            ),
            align="center",
            style={"height": "250px"},
        ),
        dbc.Row(
            [
                dbc.Card(
                    [
                        dbc.CardBody(
                            [
                                html.H4(
                                    "Dataexplorer",
                                    className="card-title",
                                ),
                                html.P(
                                    "Nuclear reaction cross section, residual production cross section, fission yield data plot",
                                    className="card-text",
                                ),
                                dbc.Button(
                                    "View Data",
                                    href="reactions/xs?target_elem=Al&target_mass=27&reaction=n%2Cp",
                                    color="primary",
                                ),
                            ],
                        ),
                    ],
                    style={"width": "30%", "height": "200px"},
                ),
                dbc.Card(
                    [
                        dbc.CardBody(
                            [
                                html.H4(
                                    "EXFOR Viewer",
                                    className="card-title",
                                ),
                                html.P(
                                    "EXFOR data search and data plot.",
                                    className="card-text",
                                ),
                                dbc.Button(
                                    "View Data",
                                    href="exfor/search",
                                    color="primary",
                                ),
                            ],
                        ),
                    ],
                    style={"width": "30%", "height": "200px"},
                ),
                dbc.Card(
                    [
                        dbc.CardBody(
                            [
                                html.H4("API Docs", className="card-title"),
                                html.P(
                                    "Dataexplorer and EXFOR Viewer API documents",
                                    className="card-text",
                                ),
                                dbc.Button(
                                    "View Document", href="api_manual/", color="success"
                                ),
                            ],
                        ),
                    ],
                    style={"width": "30%"},
                ),
            ],
            className="mb-4",
            justify="center",
        ),
        html.Hr(style={"border": "3px", "border-top": "1px solid"}),
        footer,
    ],
    fluid="True",
    style={"height": "100vh"},
)
