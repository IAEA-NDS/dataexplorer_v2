####################################################################
#
# This file is part of libraries-2021 dataexplorer, https://nds.iaea.org/dataexplorer/.
# Copyright (C) 2022 International Atomic Energy Agency (IAEA)
#
# Contact:    nds.contact-point@iaea.org
#
####################################################################

import statistics
import pandas as pd
import dash
from dash import Dash, html, dcc, Input, Output, State, ctx, no_update, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate


from pages_common import (
    sidehead,
    footer,
    libs_navbar,
    page_urls,
    lib_page_urls,
    def_inp_values,
    URL_PATH,
    # main_fig,
    input_check,
    input_obs,
    input_target,
    input_general,
    input_partial,
    highlight_data,
    generate_reactions,
    export_data,
    input_lin_log_switch,
    del_rows_fig,
    get_indexes,
    export_index,
    generate_api_link,
)
from man import table_desc_thermal

# from config import BASE_URL
from modules.reactions.thermal_table import thermal_data_table_ag
from submodules.common import (
    generate_exfortables_file_path,
    generate_endftables_file_path,
)
from submodules.utilities.reaction import get_mt
from submodules.reactions.queries import lib_th_data_query
from submodules.exfor.queries import data_query
from submodules.utilities.util import get_number_from_string


## Registration of page
dash.register_page(
    __name__,
    path="/reactions/thermal",
    title="Thermal Neutron Cross Section",
    redirect_from=["/thermal"],
)
pageparam = "th"


## Input layout
def input_lib(**query_strings):
    # if query_strings["type"] == "SIG":
    return [
        html.Br(),
        html.Div(children=input_obs(pageparam)),
        html.Div(children=input_target(pageparam, **query_strings)),
        html.Label("Reaction", style={"font-size": "small"}),
        dcc.Dropdown(
            id="reaction_" + pageparam,
            options=["n,a", "n,el", "n,f", "n,g", "n,p", "n,tot"],
            placeholder="Reaction e.g. (n,g)",
            persistence=True,
            persistence_type="memory",
            value=query_strings["reaction"]
            if query_strings.get("reaction")
            else def_inp_values[pageparam.upper()]["reaction"],
            style={"font-size": "small", "width": "100%"},
            multi=True if pageparam == "geo" or pageparam == "sch" else False,
        ),
        # html.Div(children=input_partial(pageparam, **query_strings)),
        html.Br(),
        # html.Div(children=exfor_filter_opt(pageparam)),
        # html.Br(),
        # html.Div(children=reduce_data_switch(pageparam)),
        # html.Div(children=excl_mxw_switch(pageparam)),
        # html.Br(),
        # html.Br(),
        # html.Div(children=libs_filter_opt(pageparam)),
        dcc.Store(id="input_store_th"),
    ]


def get_stat_value(data):
    mean = statistics.mean(data)
    stdev = statistics.stdev(data)
    return mean, stdev


main_fig_thermal = dcc.Graph(
    id="main_fig_th",
    config={
        "displayModeBar": True,
        "scrollZoom": True,
        "modeBarButtonsToAdd": ["drawline", "drawopenpath", "eraseshape"],
        "modeBarButtonsToRemove": ["lasso2d"],
    },
    figure={
        "layout": {
            "title": "Please select target and reaction.",
            "height": 400,
        }
    },
)

## Download options
download_opts = html.Div(
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
                    style={
                        "textAlign": "right",
                        "margin-bottom": "10px",
                    },
                ),
            ]
        ),  # close Row
    ]
)  # Close Div


## Layout of right panel
right_layout_lib = [
    libs_navbar,
    html.Hr(
        style={
            "border": "3px",
            "border-top": "1px solid",
            "margin-top": "5px",
            "margin-bottom": "5px",
        }
    ),
    html.Div(id="search_result_txt_th"),
    # Log/Linear switch
    html.Div(children=input_lin_log_switch(pageparam)),
    main_fig_thermal,
    html.Div(id="thermal_stats"),
    download_opts,
    thermal_data_table_ag,
    table_desc_thermal,
    dcc.Store(id="entries_store_th"),
    dcc.Store(id="libs_store_th"),
    html.Hr(style={"border": "3px", "border-top": "1px solid"}),
    # create_tabs(pageparam),
    footer,
]


## Main layout of libraries-2023 page
# layout = html.Div(
def layout(**query_strings):
    return html.Div(
        [
            dcc.Location(id="location_th"),
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
                                children=right_layout_lib,
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


# ###------------------------------------------------------------------------------------
# ### App Callback
# ###------------------------------------------------------------------------------------
@callback(
    [
        Output("location_th", "href", allow_duplicate=True),
        Output("location_th", "refresh", allow_duplicate=True),
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
        Output("location_th", "href", allow_duplicate=True),
        Output("location_th", "refresh", allow_duplicate=True),
    ],
    Input("observable_th", "value"),
    prevent_initial_call=True,
)
def redirect_to_subpages_th(type):
    # print("redirect_to_subpages")
    if type:
        return lib_page_urls[type], True  # , dict({"type": type})

    else:
        raise PreventUpdate


@callback(
    Output("reaction_th", "options"),
    Input("incident_particle_th", "value"),
)
def update_reaction_list_th(proj):
    # print("update_reaction_list")

    if not proj:
        raise PreventUpdate

    else:
        return generate_reactions(proj)


@callback(
    Output("input_store_th", "data"),
    [
        Input("observable_th", "value"),
        Input("target_elem_th", "value"),
        Input("target_mass_th", "value"),
        Input("reaction_th", "value"),
        # Input("exclude_mxw_switch_th", "value"),
    ],
    # prevent_initial_call=True,
)
def input_store_th(type, elem, mass, reaction):
    print("input_store_th", type)
    if type != "TH":
        return dict({"type": type})

    elem, mass, reaction = input_check(type, elem, mass, reaction)
    mt = get_mt(reaction)

    return dict(
        {
            "type": type,
            "target_elem": elem,
            "target_mass": mass,
            "reaction": reaction,
            "inc_pt": reaction.split(",")[0].upper() if reaction else None,
            "rp_elem": None,
            "rp_mass": None,
            "level_num": None,
            "branch": None,
            "mt": mt,
            "excl_junk_switch": None,
        }
    )


@callback(
    [
        Output("location_th", "search"),
        Output("location_th", "refresh", allow_duplicate=True),
    ],
    Input("input_store_th", "data"),
    prevent_initial_call=True,
)
def update_url_th(input_store):
    # print("update_url")

    if input_store:
        type = input_store.get("type").upper()
        elem = input_store.get("target_elem")
        mass = input_store.get("target_mass")
        reaction = input_store.get("reaction")
    else:
        raise PreventUpdate

    if type == "TH" and elem and mass and reaction:
        query_string = ""
        if elem:
            query_string += "?&target_elem=" + elem

        if mass:
            query_string += "&target_mass=" + mass

        if reaction:
            query_string += "&reaction=" + reaction.replace("+", "%2B")

        return query_string, False

    else:
        return no_update, False


@callback(
    [
        Output("search_result_txt_th", "children"),
        Output("entries_store_th", "data"),
        Output("libs_store_th", "data"),
    ],
    Input("input_store_th", "data"),
    # prevent_initial_call=True,
)
def initial_data_th(input_store):
    # print("initial_data_th", input_store)
    if input_store:
        return get_indexes(input_store)

    else:
        raise PreventUpdate


@callback(
    [
        Output("main_fig_th", "figure", allow_duplicate=True),
        Output("thermal_stats", "children"),
        Output("thermal_data_table", "rowData"),
        Output("xaxis_type_th", "value"),
        Output("yaxis_type_th", "value"),
    ],
    [
        Input("input_store_th", "data"),
        Input("entries_store_th", "data"),
        Input("libs_store_th", "data"),
        Input("rest_btn_th", "n_clicks"),
    ],
    prevent_initial_call=True,
)
def create_fig_th(input_store, legends, libs, r_click):
    # print("create_fig")
    if input_store:
        target_elem = input_store.get("target_elem")
        target_mass = input_store.get("target_mass")
        reaction = input_store.get("reaction")
        mt = input_store.get("mt")

        if ctx.triggered_id != "rest_btn_xs":
            no_update

    else:
        raise PreventUpdate

    xaxis_type = "linear"
    yaxis_type = "log"
    thermal_stat_content = ""

    fig = go.Figure(
        layout=go.Layout(
            # template="plotly_white",
            xaxis={
                "title": "Year",
                "type": xaxis_type,
                "range": [1970, 2024],
                "autorange": True,
                "rangeslider": {
                    "bgcolor": "White",
                    "visible": True,
                    "autorange": True,
                    "thickness": 0.2,
                },
            },
            yaxis={
                "title": "Cross section [barn]",
                "type": yaxis_type,
                "fixedrange": False,
            },
            margin={"l": 40, "b": 40, "t": 30, "r": 0},
        )
    )

    df = pd.DataFrame()
    # print(legends)
    monoen_stats = ""
    mxw_stats = ""
    thermal_stat_content = ""
    if legends:
        df = data_query(input_store, legends.keys())

    if df.empty:
        thermal_stat_content = dbc.Col(
            [
                f"{target_elem}-{target_mass}({reaction})",
                html.Br(),
                f"# EXFOR data mean",
                html.Br(),
                "No data",
                html.Br(),
                f"# EXFOR MXW and SPA data mean",
                html.Br(),
                "No data",
                html.Br(),
                f"",
            ]
        )
        # return no_update, thermal_stat_content, no_update, no_update, no_update

    else:
        df["bib"] = df["entry_id"].map(legends)
        df = pd.concat([df, df["bib"].apply(pd.Series)], axis=1)
        df = df.drop(columns=["bib"])
        df = df.sort_values(
            by=["sf9", "sf8", "year"], ascending=False, na_position="first"
        )

        df["entry_id_link"] = (
            "["
            + df["entry_id"]
            + "]("
            + URL_PATH
            + "exfor/entry/"
            + df["entry_id"]
            + ")"
        )

        i = 0

        """
        calculate mean value
        """
        if len(df.loc[(df["sf8"].isnull()) & (df["sf9"].isnull())]) >= 1:
            try:
                mean, stdev = get_stat_value(
                    df.loc[(df["sf8"].isnull()) & (df["sf9"].isnull()), "data"]
                )
                monoen_stats = f"{mean:.4E} (+/-  {stdev:.4E})"
            except:
                mean = df.loc[(df["sf8"].isnull()) & (df["sf9"].isnull()), "data"].iloc[
                    0
                ]
                stdev = df.loc[
                    (df["sf8"].isnull()) & (df["sf9"].isnull()), "ddata"
                ].iloc[0]

            monoen_stats = (
                f"{mean:.4E} (+/-  {stdev:.4E})"
                if mean and stdev
                else f"{mean:.4E} (+/-  NaN)"
            )

        if len(df.loc[(df["sf8"] == "MXW") | (df["sf8"] == "SPA")]) >= 1:
            try:
                mean, stdev = get_stat_value(
                    df.loc[(df["sf8"] == "MXW") | (df["sf8"] == "SPA"), "data"]
                )
            except:
                mean = df.loc[(df["sf8"] == "MXW") | (df["sf8"] == "SPA"), "data"].iloc[
                    0
                ]
                stdev = df.loc[
                    (df["sf8"] == "MXW") | (df["sf8"] == "SPA"), "ddata"
                ].iloc[0]

            mxw_stats = (
                f"{mean:.4E} (+/-  {stdev:.4E})"
                if mean and stdev
                else f"{mean:.4E} (+/-  NaN)"
                if mean and not stdev
                else f"NaN    (+/-  NaN)"
            )

        thermal_stat_content = dbc.Col(
            [
                f"{target_elem}-{target_mass}({reaction})",
                html.Br(),
                f"# EXFOR data mean",
                html.Br(),
                monoen_stats if monoen_stats else f"NaN    (+/-  NaN)",
                html.Br(),
                f"# EXFOR MXW/SPA data mean",
                html.Br(),
                mxw_stats if mxw_stats else f"NaN    (+/-  NaN)",
                html.Br(),
                f"",
            ]
        )




        """
        Update figure
        """
        for index, row in df.iterrows():
            fig.add_trace(
                go.Scatter(
                    x=[row["year"]],
                    y=[row["data"]],
                    # error_x=dict(type="data", array=[row["den_inc"]]),
                    error_y=dict(type="data", array=[ row["ddata"] ]),
                    showlegend=True,
                    name=f"{row['author']}, {row['year']} [{row['entry_id']}]",
                    marker=dict(
                        size=8,
                        symbol=i,
                    ),
                    mode="markers",
                )
            )
            i += 1

            if i > 30:
                i = 1

    if libs:
        lib_df = lib_th_data_query( libs.keys() )

    return fig, thermal_stat_content, df.to_dict("records"), xaxis_type, yaxis_type



@callback(
    Output("main_fig_th", "figure", allow_duplicate=True),
    [
        Input("xaxis_type_th", "value"),
        Input("yaxis_type_th", "value"),
    ],
    State("main_fig_th", "figure"),
    prevent_initial_call=True,
)
def update_axis(xaxis_type, yaxis_type, fig):
    # if xaxis_type and yaxis_type and fig:
    fig.get("layout").get("yaxis").update({"type": yaxis_type})
    fig.get("layout").get("xaxis").update({"type": xaxis_type})

    return fig






@callback(
    Output("main_fig_th", "figure", allow_duplicate=True),
    Input("thermal_data_table", "selectedRows"),
    State("main_fig_th", "figure"),
    prevent_initial_call=True,
)
def highlight_data_th(selected, fig):
    return highlight_data(selected, fig)




@callback(
    [
        Output("main_fig_th", "figure", allow_duplicate=True),
        Output("thermal_data_table", "rowTransaction"),
    ],
    Input("del_btn_th", "n_clicks"),
    [
        State("main_fig_th", "figure"),
        State("thermal_data_table", "selectedRows"),
    ],
    prevent_initial_call=True,
)
def del_rows_th(n1, fig, selected):
    if n1:
        if selected is None:
            return no_update, no_update
        return del_rows_fig(selected, fig)




@callback(
    Output("cb_state_exfor_th", "content"),
    Input("cb_state_exfor_th", "n_clicks"),
    Input("thermal_data_table", "columnState"),
    State("thermal_data_table", "selectedRows"),
    prevent_initial_call=True,
)
def selected_th(n, col_state, selected):
    if selected is None:
        return "No selections"
    if col_state is None:
        return no_update

    dff = pd.DataFrame(selected)

    # get current column order in grid
    columns = [row["colId"] for row in col_state]
    dff = dff[columns]

    return dff.to_string()




@callback(
    [
        Output("thermal_data_table", "exportDataAsCsv"),
        Output("thermal_data_table", "csvExportParams"),
    ],
    [
        Input("btn_csv_exfor_th", "n_clicks"),
        Input("btn_csv_exfor_selct_th", "n_clicks"),
        Input("input_store_th", "data"),
    ],
    prevent_initial_call=True,
)
def export_data_xs(n1, n2, input_store):
    # return export_data(n_clicks_all, n_clicks_slctd, input_store)
    if not input_store:
        raise PreventUpdate

    if ctx.triggered_id == "btn_csv_exfor_th":
        return export_data(False, input_store)

    elif ctx.triggered_id == "btn_csv_exfor_selct_th":
        return export_data(True, input_store)

    else:
        return no_update, no_update




@callback(
    Output("btn_api_data_th", "href"),
    Input("location_th", "search"),
)
def generate_api_links(search_str):
    return generate_api_link(pageparam, search_str)[1]
