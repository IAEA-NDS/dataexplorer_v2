####################################################################
#
# This file is part of libraries-2021 dataexplorer, https://nds.iaea.org/dataexplorer/.
# Copyright (C) 2022 International Atomic Energy Agency (IAEA)
#
# Contact:    nds.contact-point@iaea.org
#
####################################################################

import os

from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

from libraries.index_table import index_table_ag
from libraries.data_table import data_table_ag


def create_tabs(pageparam):
    pageparam = pageparam.lower()
    tabs = dbc.Tabs(
        id="".join(["tabs-", pageparam]),
        active_tab="".join(["ds-", pageparam]),
        children=[
            # first tab
            dbc.Tab(
                label="Dataset List",
                tab_id="".join(["ds-", pageparam]),
                children=[
                    html.Br(),
                    html.Div(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            dbc.Button(
                                                "Remove Selected",
                                                id="".join(["del_btn_", pageparam]),
                                                outline=True,
                                                color="secondary",
                                                className="me-1",
                                                n_clicks=0,
                                            ),
                                            dbc.Button(
                                                "Reset",
                                                id="".join(["rest_btn_", pageparam]),
                                                outline=True,
                                                color="secondary",
                                                className="me-1",
                                                n_clicks=0,
                                            ),
                                        ]
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Badge(
                                                "Download CSV",
                                                id="".join(
                                                    ["btn_csv_index_", pageparam]
                                                ),
                                                href="#",
                                                color="secondary",
                                            ),
                                            "  ",
                                            dbc.Badge(
                                                "Download CSV (selected)",
                                                id="".join(
                                                    ["btn_csv_index_selct_", pageparam]
                                                ),
                                                href="#",
                                                color="white",
                                                text_color="dark",
                                                className="border me-1",
                                            ),
                                            "  ",
                                            dbc.Badge(
                                                "API",
                                                id="".join(["btn_api_", pageparam]),
                                                href=f"api/",
                                                color="info",
                                                className="me-1",
                                            ),
                                        ],
                                        style={
                                            "textAlign": "right",
                                            "margin-bottom": "10px",
                                        },
                                    ),
                                ]
                            ),  # close Row
                        ],  # close Div
                    ),
                    # Index Table
                    index_table_ag(pageparam),
                ],  # end of first tab children
            ),  # end of first tab
            # start second tab
            dbc.Tab(
                label="Raw Data",
                tab_id="".join(["datatable-", pageparam.lower()]),
                children=[
                    html.Br(),
                    html.Div(
                        [
                            dbc.Badge(
                                "Download CSV",
                                id="".join(["btn_csv_exfor_", pageparam]),
                                href="#",
                                color="secondary",
                            ),
                            "  ",
                            dbc.Badge(
                                "Download CSV (selected)",
                                id="".join(["btn_csv_exfor_selct_", pageparam]),
                                href="#",
                                color="white",
                                text_color="dark",
                                className="border me-1",
                            ),
                            "  ",
                            dbc.Badge(
                                "API",
                                id="".join(["btn_api_data_", pageparam]),
                                href=f"api/",
                                color="info",
                                className="me-1",
                            ),
                        ],
                        style={"textAlign": "right", "margin-bottom": "10px"},
                    ),
                    # data table
                    data_table_ag(pageparam),
                ],  # end of second tab children
            ),  # end of second tab
            dbc.Tab(
                label="Download Data Files",
                tab_id="".join(["dl-", pageparam.lower()]),
                children=[
                    html.Br(),
                    html.P(
                        children=[
                            "Files in ",
                            html.A(
                                "EXFORTABLES",
                                href="https://github.com/shinokumura/endftables_py",
                                className="text-dark",
                            ),
                            " by ",
                            html.A(
                                "exforparser",
                                href="https://github.com/shinokumura/exforparser",
                                className="text-dark",
                            ),
                            ":",
                        ]
                    ),
                    html.Div(id="".join(["exfiles_link_", pageparam.lower()])),
                    html.Br(),
                    html.Br(),
                    html.P(
                        children=[
                            "Files in ",
                            html.A(
                                "ENDFTABLES",
                                href="https://nds.iaea.org/talys/",
                                className="text-dark",
                            ),
                            ":",
                        ]
                    ),
                    html.Div(id="".join(["libfiles_link_", pageparam.lower()])),
                ],
            ),
        ],
    )
    # ])
    return tabs


#                             " and ",
# ,
