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
import dash_ag_grid as dag


def index_table(pageparam):
    return dash_table.DataTable(
        id="index_table" + "_" + pageparam.lower(),
        columns=[
            {"name": "Author", "id": "author"},
            {"name": "Year", "id": "year"},
            {
                "name": "#Entry",
                "id": "entry_id",
                "presentation": "markdown",
            },
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
        markdown_options={"html": True},  # fill_width=False
    )


def data_table(pageparam):
    return dash_table.DataTable(
        id="".join(["exfor_table_", pageparam.lower()]),
        columns=[
            {"name": "Author", "id": "author"},
            {"name": "Year", "id": "year"},
            {
                "name": "#Entry",
                "id": "entry_id",
                "presentation": "markdown",
            },
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
                "name": "Data",
                "id": "data",
                "type": "numeric",
                "format": Format(precision=4, scheme=Scheme.exponent),
            },
            {
                "name": "dData",
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
    )


def create_tabs(pageparam):
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
                        "Add more data to the chart by selecting dataset from the following table. Use filter function, e.g. >2000 in Year field. "
                    ),
                    # Index Table
                    # index_table(pageparam)
                    index_table_ag(pageparam),
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
                    # data table
                    data_table(pageparam),
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
                    html.P("Download all experimental datasets as a CSV file:"),
                    dcc.Download(
                        id="".join(["csv-link-", pageparam.lower()]),
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
                            {
                                "name": "#Entry",
                                "id": "entry_id",
                                "presentation": "markdown",
                            },
                            {"name": "Points", "id": "points"},
                            {
                                "name": "E_inc[MeV]",
                                "id": "e_inc_max",
                                "type": "numeric",
                                "format": Format(precision=4, scheme=Scheme.exponent),
                            },
                            {"name": "x4_code", "id": "x4_code"},
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
                                "name": "Data",
                                "id": "data",
                                "type": "numeric",
                                "format": Format(precision=4, scheme=Scheme.exponent),
                            },
                            {
                                "name": "dData",
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


########### AGGRID tables
defaultFilterParams = {
    "filterOptions": ["contains"],
    "defaultOption": "contains",
    "trimInput": True,
    # "debounceMs": 1000,
}


columnDefs = [
    {
        "headerName": "Author",
        "field": "author",
        "type": "rightAligned",
        "filter": "agTextColumnFilter",
        "filterParams": defaultFilterParams,
        "checkboxSelection": True,
        "headerCheckboxSelection": True,
    },
    {
        "headerName": "Year",
        "field": "year",
        "type": "rightAligned",
        "filter": "agNumberColumnFilter",
    },
    {
        "headerName": "Entry Id",
        "field": "entry_id_link",
        "type": "rightAligned",
        "filter": "agTextColumnFilter",
        "filterParams": defaultFilterParams,
        # "cellStyle": {"color": "blue", "text-decoration": "underline"},
        "cellRenderer": "markdown",
    },
    {
        "headerName": "Points",
        "field": "points",
        "type": "rightAligned",
        "filter": "agNumberColumnFilter",
    },
    {
        "headerName": "E_min [MeV]",
        "field": "e_inc_min",
        "type": "rightAligned",
        "filter": "agNumberColumnFilter",
    },
    {
        "headerName": "E_max [MeV]",
        "field": "e_inc_max",
        "type": "rightAligned",
        "filter": "agNumberColumnFilter",
    },
    {
        "headerName": "EXFOR Reaction Code",
        "field": "x4_code",
        "type": "rightAligned",
        "filter": "agTextColumnFilter",
        "filterParams": defaultFilterParams,
    },
    {
        "headerName": "SF8",
        "field": "sf8",
        "type": "rightAligned",
        "filter": "agTextColumnFilter",
    },
]

defaultColDef = {
    "flex": 1,
    "width": 50,
    # "floatingFilter": True,
    "resizable": True,
    "sortable": True,
    "filter": True,
}

columnSizeOptions = {
    "defaultMinWidth": 100,
    "columnLimits": [
        {"key": "author", "minWidth": 200},
        {"key": "entry_id", "minWidth": 100},
        {"key": "x4_code", "minWidth": 300},
        {"key": "year", "maxWidth": 80},
        {"key": "sf8", "maxWidth": 80},
        {"key": "points", "maxWidth": 80},
    ],
}


def index_table_ag(pageparam):
    return dag.AgGrid(
        id="index_table_" + pageparam,
        # enableEnterpriseModules=False,
        columnDefs=columnDefs,
        # rowData=df.to_dict("records"),.
        columnSize="sizeToFit",
        columnSizeOptions=columnSizeOptions,
        dashGridOptions={
            "rowSelection": "multiple",
            "rowMultiSelectWithClick": True,
            # "pagination": True,
            # "paginationPageSize": 100
        },
        className="ag-theme-balham",  ## Themes: ag-theme-alpine, ag-theme-alpine-dark, ag-theme-balham, ag-theme-balham-dark, ag-theme-material, and ag-bootstrap.
        persistence=True,
        persisted_props=["filterModel"]
    )
