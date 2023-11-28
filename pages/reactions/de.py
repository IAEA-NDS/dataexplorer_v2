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
from dash.exceptions import PreventUpdate

from pages_common import (
    sidehead,
    footer,
    libs_navbar,
    URL_PATH,
    page_urls,
    lib_page_urls,
    input_check,
    input_general,
    exfor_filter_opt,
    energy_range_conversion,
)

from submodules.utilities.reaction import reaction_list
from modules.reactions.tabs import create_tabs
from modules.reactions.figs import default_chart, default_axis
from submodules.reactions.queries import (
    lib_query,
    lib_xs_data_query,
)
from submodules.exfor.queries import (
    index_query,
    get_entry_bib,
    data_query,
)


## Registration of page
dash.register_page(__name__, path="/reactions/de")
pageparam = "de"


def input(**query_strings):
    return [
        html.Div(children=input_general(pageparam, **query_strings)),
        html.Br(),
        html.Div(children=exfor_filter_opt(pageparam)),
        html.Br(),
    ]


## main figure
main_fig_de = dcc.Graph(
    id="main_fig_de",
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


right_layout_de = [
    libs_navbar,
    html.Hr(style={"border": "3px", "border-top": "1px solid"}),
    html.Div(id="result_cont_de"),
    # Log/Linear switch
    dbc.Row(
        [
            dbc.Col(html.Label("X:"), width="auto"),
            dbc.Col(
                dcc.RadioItems(
                    id="xaxis_type_de",
                    options=[
                        {"label": i, "value": i.lower()} for i in ["Linear", "Log"]
                    ],
                    value="linear",
                    persistence=True,
                    persistence_type="memory",
                    labelStyle={"display": "inline-block"},
                ),
                width="auto",
            ),
            dbc.Col(html.Label("Y:"), width="auto"),
            dbc.Col(
                dcc.RadioItems(
                    id="yaxis_type_de",
                    options=[
                        {"label": i, "value": i.lower()} for i in ["Linear", "Log"]
                    ],
                    value="linear",
                    persistence=True,
                    persistence_type="memory",
                    labelStyle={"display": "inline-block"},
                ),
                width="auto",
            ),
        ]
    ),
    dcc.Loading(
        children=main_fig_de,
        type="circle",
    ),
    html.Hr(style={"border": "3px", "border-top": "1px solid"}),
    create_tabs("de"),
    html.Hr(style={"border": "3px", "border-top": "1px solid"}),
    footer,
]


def layout(**query_strings):
    return html.Div(
        [
            dcc.Location(id="location_de"),
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
                                    html.Div(input(**query_strings)),
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
                                children=right_layout_de,
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


###------------------------------------------------------------------------------------
### App Callback
###------------------------------------------------------------------------------------
@callback(
    Output("location_de", "href", allow_duplicate=True),
    Input("dataset", "value"),
    prevent_initial_call=True,
)
def redirect_to_pages_de(dataset):
    if dataset:
        return page_urls[dataset]
    else:
        raise PreventUpdate


@callback(
    Output("location_de", "href", allow_duplicate=True),
    Input("observable_de", "value"),
    prevent_initial_call=True,
)
def redirect_to_subpages_de(type):
    if type:
        return lib_page_urls[type]
    else:
        raise PreventUpdate


@callback(
    Output("location_de", "href", allow_duplicate=True),
    [
        Input("observable_de", "value"),
        Input("target_elem_de", "value"),
        Input("target_mass_de", "value"),
        Input("reaction_de", "value"),
    ],
    prevent_initial_call=True,
)
def update_url_de(type, elem, mass, reaction):
    input_check(type, elem, mass, reaction)

    if type == "DE" and (elem and mass and reaction):
        url = URL_PATH + "reactions/de"

        if elem:
            url += "?&target_elem=" + elem
        if mass:
            url += "&target_mass=" + mass
        if reaction:
            url += "&reaction=" + reaction
        return url

    else:
        raise PreventUpdate


@callback(
    [
        Output("result_cont_de", "children"),
        Output("main_fig_de", "figure"),
        Output("index_table_de", "rowData"),
        Output("exfor_table_de", "rowData"),
    ],
    [
        Input("observable_de", "value"),
        Input("target_elem_de", "value"),
        Input("target_mass_de", "value"),
        Input("reaction_de", "value"),
    ],
    # prevent_initial_call=True,
)
def update_fig_de(type, elem, mass, reaction):
    elem, mass, reaction = input_check(type, elem, mass, reaction)
    print(type, elem, mass, reaction)
    df = pd.DataFrame()
    index_df = pd.DataFrame()

    mt = reaction_list[reaction.split(",")[1].upper()]["mt"].zfill(3)
    xaxis_type, yaxis_type = default_axis(mt)
    fig = go.Figure(
        layout=go.Layout(
            xaxis={
                "title": "Emission Energy [eV]",
                "type": "linear",
                "rangeslider": {
                    "bgcolor": "White",
                    "visible": True,
                    "autorange": True,
                    "thickness": 0.15,
                },
            },
            yaxis={
                "title": "Energy distribution [b/eV]",
                "type": "linear",
                "fixedrange": False,
            },
            margin={"l": 40, "b": 40, "t": 30, "r": 0},
        )
    )

    entries = index_query(
        type, elem, mass, reaction, branch=None, rp_elem=None, rp_mass=None
    )
    search_result = (
        f"Search results for {type} {elem}-{mass}({reaction}): {len(entries)}"
    )

    if not entries:
        return search_result, fig, None, None

    if entries:
        legend = get_entry_bib(e[:5] for e in entries.keys())
        legend = {
            t: dict(**i, **v)
            for k, i in legend.items()
            for t, v in entries.items()
            if k == t[:5]
        }
        df = data_query(entries.keys())

        i = 0
        for e in legend.keys():
            fig.add_trace(
                go.Scatter(
                    x=df[df["entry_id"] == e]["e_out"],
                    y=df[df["entry_id"] == e]["data"],
                    error_x=dict(type="data", array=df[df["entry_id"] == e]["de_out"]),
                    error_y=dict(type="data", array=df[df["entry_id"] == e]["ddata"]),
                    showlegend=True,
                    name=f"{legend[e]['author']}, {legend[e]['year']}"
                    if legend[e].get("year")
                    else legend[e]["author"],
                    marker=dict(size=8, symbol=i),
                    mode="markers",
                )
            )
            i += 1

            if i == 30:
                i = 1

        index_df = pd.DataFrame.from_dict(legend, orient="index").reset_index()
        index_df.rename(columns={"index": "entry_id"}, inplace=True)
        index_df["entry_id_link"] = (
            "["
            + index_df["entry_id"]
            + "](../exfor/entry/"
            + index_df["entry_id"]
            + ")"
        )
        df["bib"] = df["entry_id"].map(legend)
        df = pd.concat([df, df["bib"].apply(pd.Series)], axis=1)
        df = df.drop(columns=["bib"])
        df["entry_id_link"] = (
            "[" + df["entry_id"] + "](../exfor/entry/" + df["entry_id"] + ")"
        )
    return (
        search_result,
        fig,
        index_df.to_dict("records"),
        df.to_dict("records"),
    )


@callback(
    Output("main_fig_de", "figure", allow_duplicate=True),
    [
        Input("xaxis_type_de", "value"),
        Input("yaxis_type_de", "value"),
    ],
    State("main_fig_de", "figure"),
    prevent_initial_call=True,
)
def update_axis(xaxis_type, yaxis_type, fig):
    ## Switch the axis type
    fig.get("layout").get("yaxis").update({"type": yaxis_type})
    fig.get("layout").get("xaxis").update({"type": xaxis_type})

    return fig


@callback(
    [
        Output("main_fig_de", "figure", allow_duplicate=True),
        Output("index_table_de", "filter_query"),
    ],
    [
        Input("energy_range_de", "value"),
        Input("year_range_de", "value"),
    ],
    State("main_fig_de", "figure"),
    prevent_initial_call=True,
)
def fileter_by_range_lib(energy_range, year_range, fig):
    # print(json.dumps(fig, indent=1))
    print(energy_range, year_range)
    filter = ""

    for records in fig.get("data"):
        if len(records.get("name").split(",")) > 1:
            author, year = records.get("name").split(",")

            sum_x = sum([float(x) for x in records["x"] if x is not None])
            lower, upper = energy_range_conversion(energy_range)

            filter = (
                "{year} ge "
                + str(year_range[0])
                + " && {year} le "
                + str(year_range[1])
            )
            filter += (
                " && {e_inc_min} ge " + str(lower) + " && {e_inc_max} le " + str(upper)
            )

            if (
                not lower < sum_x / len(records["x"]) < upper
                or not year_range[0] < int(year) < year_range[1]
            ):
                records.update({"visible": "legendonly"})

            if (
                lower < sum_x / len(records["x"]) < upper
                and year_range[0] < int(year) < year_range[1]
            ):
                records.update({"visible": "true"})

    return fig, filter


@callback(
    [
        Output("exfor_table_de", "exportDataAsCsv"),
        Output("exfor_table_de", "csvExportParams"),
    ],
    Input("csv-button_de", "n_clicks"),
)
def export_data_as_csv_de(n_clicks):
    if n_clicks:
        return True, {
            "fileName": "ag_grid_all_cols_test.csv",
            "columnKeys": [
                "author",
                "year",
                "entry_id",
                "en_inc",
                "den_inc",
                "data",
                "ddata",
            ],
        }

    else:
        return False, {}
