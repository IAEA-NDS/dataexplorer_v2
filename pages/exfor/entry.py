####################################################################
#
# This file is part of libraries-2021 dataexplorer, https://nds.iaea.org/dataexplorer/.
# Copyright (C) 2022 International Atomic Energy Agency (IAEA)
#
# Contact:    nds.contact-point@iaea.org
#
####################################################################

import dash
from dash import Dash, html, dcc, Input, Output, State, ctx, no_update, callback
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go

from exfor_dictionary.exfor_dictionary import Diction

from pages_common import (
    URL_PATH,
    sidehead,
    page_urls,
    exfor_navbar,
    footer,
    input_entry,
    entry_id_check,
)
from modules.exfor.record import (
    get_record,
    show_entry_links,
    show_entry_bib,
    show_entry_experimental_condition,
    make_tooltip,
    generate_data_table,
    generate_fig,
    get_git_history_api,
    compare_commits_api,
    show_compile_history,
    generate_json_link,
)
from modules.exfor.stat import stat_right_layout
from modules.exfor.aggrid import aggrid_layout_dynamic
from modules.exfor.list import bib_df

entries = bib_df["entry"].to_list()

dash.register_page(__name__, path="/exfor", path_template="/exfor/entry/<entry_id>")
pageparam = "ex"

D = Diction()


def input_ex(entry_id=None):
    return dbc.Row(
        [
            html.Div(children=input_entry(pageparam, entry_id)),
            dcc.Link(html.Label("Reaction Search"), href=URL_PATH + "exfor/search"),
            dcc.Link(html.Label("Geo Search"), href=URL_PATH + "exfor/geo"),
        ]
    )


# See https://dash.plotly.com/dash-core-components/graph
main_fig = dcc.Graph(
    id="main_graph_ex",
    config={
        "displayModeBar": True,
        "scrollZoom": True,
        "modeBarButtonsToAdd": ["drawline", "drawopenpath", "eraseshape"],
        "modeBarButtonsToRemove": ["lasso2d"],
    },
    figure={
        "layout": {
            "height": 550,
        }
    },
)


## right panel of the EXFOR page layout
record_right_layout = [
    exfor_navbar,
    html.Hr(style={"border": "3px", "border-top": "1px solid"}),
    html.Div(id="exfor_entry_links"),
    html.Br(),
    html.Div(id="exfor_entry_bib", children=show_entry_bib()),
    html.Br(),
    html.Div(id="exfor_entry_experimental_conditions"),
    html.Hr(style={"border": "3px", "border-top": "1px solid"}),
    dbc.Row(
        [
            dbc.Col(
                [
                    html.Div(
                        children=[
                            dbc.Badge(
                                "Download CSV",
                                id="btn_csv_all",
                                href="#",
                                color="secondary",
                            ),
                            "  ",
                            dbc.Badge(
                                "Download CSV (selected)",
                                id="btn_csv_selct",
                                href="#",
                                color="white",
                                text_color="dark",
                                className="border me-1",
                            ),
                            # dcc.Download(id="download-dataframe-csv"),
                        ],
                        style={"textAlign": "right", "margin-bottom": "10px"},
                    ),
                    # html.Div(id="data-table"),
                    html.Div(id="data_table"),
                ]
            ),
            dbc.Col(main_fig),
        ]
    ),
    dcc.Store(id="entry_store"),
    html.Hr(style={"border": "3px", "border-top": "1px solid"}),
    footer,
]


## EXFOR page layout
def layout(entry_id=None):
    right_layout = record_right_layout

    return html.Div(
        [
            dcc.Location(id="location_ex"),
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
                                        value="EXFOR Viewer",
                                        style={"font-size": "small"},
                                        persistence=True,
                                        persistence_type="memory",
                                    ),
                                    html.Div(
                                        input_ex(entry_id),
                                    ),
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
                                children=right_layout,
                                style={"margin-right": "20px"},
                            ),
                        ],
                        width=10,
                    ),
                ]
            ),
        ],
        id="main_layout_ex",
        style={"height": "100vh"},
    )


###------------------------------------------------------------------------------------
### App Callback
###------------------------------------------------------------------------------------
@callback(
    [
        Output("location_ex", "href", allow_duplicate=True),
        Output("location_ex", "refresh", allow_duplicate=True),
    ],
    Input("dataset", "value"),
    prevent_initial_call=True,
)
def redirect_to_pages(dataset):
    if dataset:
        return page_urls[dataset], True
    else:
        raise PreventUpdate


@callback(
    [
        Output("location_ex", "href", allow_duplicate=True),
        Output("location_ex", "refresh", allow_duplicate=True),
    ],
    Input("entid_ex", "value"),
    prevent_initial_call=True,
)
def redirect_to_url(entry_id):
    ## if the entry_id changes, redirect to the url
    entry_id = entry_id_check(entry_id)
    return f"{URL_PATH}exfor/entry/{entry_id}", True


@callback(
    [
        Output("location_ex", "pathname"),
        Output("location_ex", "refresh", allow_duplicate=True),
    ],
    Input("selected_reaction", "value"),
    prevent_initial_call=True,
)
def update_url_ex(entry_id):
    ## if change the subentry from the list, only the path should be changed
    entry_id = entry_id_check(entry_id)
    return entry_id, False


## Get JSON and store it
@callback(Output("entry_store", "data"), Input("entid_ex", "value"))
def entry_store(entry_id):
    entry_id = entry_id_check(entry_id)
    return get_record(entry_id[0:5])


## Generate links
@callback(
    Output("exfor_entry_links", "children"),
    [Input("entid_ex", "value"), Input("entry_store", "data")],
)
def entnumentid_ex(entry_id, entry_json):
    entry_id = entry_id_check(entry_id)
    if entry_json:
        return show_entry_links(entry_id[0:5], entry_json)
    else:
        raise PreventUpdate


## EXFOR experimental BIB
@callback(
    Output("exfor_entry_bib", "children"),
    [Input("entid_ex", "value"), Input("entry_store", "data")],
    prevent_initial_call=True,
)
def get_entry_bib(entry_id, entry_json):
    entry_id = entry_id_check(entry_id)
    if entry_json:
        return show_entry_bib(entry_json)
    else:
        return no_update


## input
@callback(
    Output("selected_reaction", "value"),
    Input("entid_ex", "value"),
)
def get_entry_exp(entry_id):
    entry_id = entry_id_check(entry_id)
    if not entry_id:
        raise PreventUpdate

    elif len(entry_id) != 11:
        raise PreventUpdate

    if len(entry_id) == 11:
        return entry_id


## EXFOR experimental condition
@callback(
    Output("exfor_entry_experimental_conditions", "children"),
    [Input("selected_reaction", "value"), Input("entry_store", "data")],
)
def get_entry_exp(selected_id, entry_json):
    if entry_json:
        return show_entry_experimental_condition(selected_id, entry_json)
    else:
        raise PreventUpdate


## Get table and update data
@callback(
    [Output("data_table", "children"), Output("main_graph_ex", "figure")],
    [Input("selected_reaction", "value"), Input("entry_store", "data")],
)
def update_fig_data(selected_id, entry_json):
    if not selected_id:
        raise PreventUpdate

    if len(selected_id) != 11:
        raise PreventUpdate

    if entry_json and selected_id:
        df = generate_data_table(selected_id, entry_json)
        fig = generate_fig(df)

        if len(df.index) == 0:
            return None, fig

        data_col = [col for col in df.keys() if "DATA" in col and not "ERR" in col]
        en_col = [col for col in df.keys() if "EN" in col and not "ERR" in col]
        ang_col = [col for col in df.keys() if "ANG" in col and not "ERR" in col]

        if data_col and en_col:
            fig.add_trace(
                go.Scatter(
                    x=df[en_col[0]],
                    y=df[data_col[0]],
                )
            )
            fig.update_layout(xaxis={"title": en_col[0]}, yaxis={"title": data_col[0]})

        if data_col and ang_col:
            fig.add_trace(
                go.Scatter(
                    x=df[ang_col[0]],
                    y=df[data_col[0]],
                )
            )
            fig.update_layout(xaxis={"title": ang_col[0]}, yaxis={"title": data_col[0]})

        return aggrid_layout_dynamic("entry", df), fig

    else:
        return no_update, no_update


@callback(
    [
        Output("aggrid_entry", "exportDataAsCsv"),
        Output("aggrid_entry", "csvExportParams"),
    ],
    [
        Input("selected_reaction", "value"),
        Input("btn_csv_all", "n_clicks"),
        Input("btn_csv_selct", "n_clicks"),
    ],
    prevent_initial_call=True,
)
def export_data_as_csv_all(selected_id, n_clicks_all, n_clicks_slctd):
    if ctx.triggered_id == "n_clicks_all":
        filename = f"{selected_id}-exfor.csv"
        return True, {"fileName": filename}

    elif ctx.triggered_id == "n_clicks_slctd":
        filename = f"{selected_id}-exfor.csv"
        return True, {
            "fileName": filename,
            "onlySelected": True,
            "onlySelectedAllPages": True,
        }

    else:
        return no_update, no_update
