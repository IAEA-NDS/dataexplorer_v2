
####################################################################
#
# This file is part of libraries-2021 dataexplorer, https://nds.iaea.org/dataexplorer/.
# Copyright (C) 2022 International Atomic Energy Agency (IAEA)
#
# Contact:    nds.contact-point@iaea.org
#
####################################################################

import dash_bootstrap_components as dbc
from dash import html, dcc, dash_table
from dash.dash_table.Format import Format, Scheme


def create_tabs(pageparam):
    tabs = dbc.Tabs(
        id="".join(["tabs-", pageparam.lower()]),
        active_tab="".join(["ds-", pageparam.lower()]),
        children=[
            # first tab
            dbc.Tab(
                label="Dataset List",
                tab_id="".join(["ds-", pageparam.lower()]),
                children=[
                    html.Br(),
                    html.P(
                        "Add more data to the chart by selecting dataset from the following table. Use filter function, e.g. >2000 in Year field. "
                    ),
                    # Index Table
                    dash_table.DataTable(
                        id="index_table"+"_"+pageparam.lower(),
                        columns=[
                            {"name": "Author", "id": "author"},
                            {"name": "Year", "id": "year"},
                            {"name": "#Entry", "id": "entry_id", "presentation": "markdown"},
                            {"name": "Points", "id": "points"},
                            {
                                "name": "E_min[MeV]",
                                "id": "e_inc_min",
                                "type": "numeric",
                                "format": Format(precision=3, scheme=Scheme.exponent),
                            },
                            {
                                "name": "E_max[MeV]",
                                "id": "e_inc_max",
                                "type": "numeric",
                                "format": Format(precision=3, scheme=Scheme.exponent),
                            },
                            # {"name": "sf5", "id": "sf5"},
                            # {"name": "sf8", "id": "sf8"},
                            {"name": "x4_code", "id": "x4_code"},
                        ],
                        filter_action="native",
                        sort_action="native",
                        sort_mode="single",
                        page_action="native",
                        page_current=0,
                        page_size=20,
                        style_table={"overflowY": "auto"},
                        markdown_options={"html": True},                        # fill_width=False
                    ),
                ],  # end of first tab children
            ),  # end of first tab
            # start second tab
            dbc.Tab(
                label="Raw Data",
                tab_id="".join(["datatable-", pageparam.lower()]),
                children=[
                    html.Br(),
                    html.P("Selected experimental data in the chart."),
                    html.P("Use filter function e.g. '>0.1' in Energy. "),
                    dash_table.DataTable(
                        id="".join(["exfor_table_", pageparam.lower()]),
                        columns=[
                            {"name": "Author", "id": "author"},
                            {"name": "Year", "id": "year"},
                            {"name": "#Entry", "id": "entry_id", "presentation": "markdown"},
                            {
                                "name": "Energy[MeV]",
                                "id": "en_inc",
                                "type": "numeric",
                                "format": Format(precision=4, scheme=Scheme.exponent),
                            },
                            {
                                "name": "dEnergy[MeV]",
                                "id": "den_inc",
                                "type": "numeric",
                                "format": Format(precision=4, scheme=Scheme.exponent),
                            },
                            {
                                "name": "XS[b]",
                                "id": "data",
                                "type": "numeric",
                                "format": Format(precision=4, scheme=Scheme.exponent),
                            },
                            {
                                "name": "dXS[b]",
                                "id": "ddata",
                                "type": "numeric",
                                "format": Format(precision=2, scheme=Scheme.exponent),
                            },
                        ],
                        filter_action="native",
                        sort_action="native",
                        sort_mode="single",
                        page_action="native",
                        page_current=0,
                        page_size=20,
                        style_table={"overflowY": "auto"},
                        markdown_options={"html": True},  
                    ),
                ],  # end of second tab children
            ),  # end of second tab
            dbc.Tab(
                label="Download Data Files",
                tab_id="".join(["dl-", pageparam.lower()]),
                children=[
                    # html.Div(
                    #     id="".join(["file_list_", pageparam.lower()]),
                    # )
    
                    html.Br(),
                    html.P(
                        "Download all experimental datasets as a CSV file:"
                    ),
                    dcc.Download(id="".join(["csv-link-", pageparam.lower()]),
                    ),
                    html.Br(),
                    html.Br(),
                    html.P("Files in EXFORTABLES:"),
                    # html.Div(
                    #     [html.Button("Download zip", id="btn_zip1"), Download(id="zip1")]
                    # ),
                    # html.Br(),
                    # html.Div(children=exflinks),
                    html.Br(),
                    html.Br(),
                    html.P("Files in ENDFTABLES:"),
                    # html.Div(children=libflinks),
        
                ],
            ),
        ],
    )
    # ])
    return tabs



def create_tabs_fy():
    pageparam = "fy"
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
                    html.P(
                        "Add more data to the chart by selecting dataset from the following table."
                    ),
                    # Index Table
                    dash_table.DataTable(
                        id="index_table_fy",
                        columns=[
                            {"name": "Author", "id": "author"},
                            {"name": "Year", "id": "year"},
                            {"name": "#Entry", "id": "entry_id", "presentation": "markdown"},
                            {"name": "Points", "id": "points"},
                            {
                                "name": "E_inc[MeV]",
                                "id": "e_inc_max",
                                "type": "numeric",
                                "format": Format(precision=4, scheme=Scheme.exponent),
                            },

                        ],
                        filter_action="native",
                        sort_action="native",
                        sort_mode="single",
                        page_action="native",
                        page_current=0,
                        page_size=20,
                        style_table={"overflowY": "auto"},
                        markdown_options={"html": True},    
                    ),
                ],  # end of first tab children
            ),  # end of first tab
            # start second tab
            dbc.Tab(
                label="Raw Data",
                tab_id="".join(["datatable-", pageparam]),
                children=[
                    html.Br(),
                    html.P("Selected experimental data in the chart."),
                    html.P("Use filter function e.g. '>0.1' in E_inc. "),
                    dash_table.DataTable(
                        id="".join(["exfor_table_", pageparam]),
                        columns=[
                            {"name": "Author", "id": "author"},
                            {"name": "Year", "id": "year"},
                            {"name": "#Entry", "id": "entry"},
                            {
                                "name": "E_inc[MeV]",
                                "id": "en_inc",
                                "type": "numeric",
                                "format": Format(precision=4, scheme=Scheme.exponent),
                            },
                            {"name": "A", "id": "mass", "type": "numeric"},
                            {"name": "Z", "id": "charge", "type": "numeric"},
                            {"name": "Iso", "id": "isomer", "type": "numeric"},
                            {
                                "name": "Yield",
                                "id": "data",
                                "type": "numeric",
                                "format": Format(precision=4, scheme=Scheme.exponent),
                            },
                            {
                                "name": "dYield",
                                "id": "ddata",
                                "type": "numeric",
                                "format": Format(precision=2, scheme=Scheme.exponent),
                            },
                        ],
                        filter_action="native",
                        sort_action="native",
                        sort_mode="single",
                        page_action="native",
                        page_current=0,
                        page_size=20,
                        style_table={"overflowY": "auto"},
                        markdown_options={"html": True},    
                    ),
                ],  # end of second tab children
            ),  # end of second tab
            dbc.Tab(
                label="Download Data Files",
                tab_id="".join(["dl-", pageparam]),
                children=[
                    html.Div(
                        id="".join(["file_list_", pageparam]),
                    )
                ],
            ),
        ],
    )
    # ])
    return tabs
