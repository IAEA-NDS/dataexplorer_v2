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
from dash import html, dcc, Input, Output, State, ctx, no_update, callback
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go


from pages_common import (
    PARTICLE_FY,
    ENERGIES,
    sidehead,
    footer,
    libs_navbar,
    page_urls,
    lib_page_urls,
    URL_PATH,
    main_fig,
    input_check,
    input_obs,
    input_target,
    excl_mxw_switch,
    exfor_year_filter,
    exfor_energy_selector,
    libs_filter_opt,
    get_indexes,
    scale_data,
    del_rows_fig,
    highlight_data,
    filter_by_year_range,
    export_index,
    export_data,
    list_link_of_files,
    generate_api_link,
)

from modules.reactions.list import color_libs
from modules.reactions.tabs import create_tabs

from submodules.common import (
    generate_exfortables_file_path,
    generate_endftables_file_path,
)
from submodules.utilities.reaction import MT_BRANCH_LIST_FY
from submodules.reactions.queries import lib_fy_data_query
from submodules.exfor.queries import data_query


## Registration of page
dash.register_page(__name__, path="/reactions/fy", redirect_from=["/fy"])
pageparam = "fy"


## Input layout
def input_fy(**query_strings):
    return [
        html.Br(),
        html.Div(children=input_obs(pageparam)),
        html.Div(children=input_target(pageparam, **query_strings)),
        html.Label("Reaction"),
        dcc.Dropdown(
            id="reaction_fy",
            options=[f"{pt.lower()},f" for pt in PARTICLE_FY],
            placeholder="Reaction e.g. (n,f)",
            persistence=True,
            persistence_type="memory",
            value=query_strings["reaction"] if query_strings.get("reaction") else "n,f",
            style={"font-size": "small", "width": "100%"},
        ),
        html.Br(),
        html.P("EXFOR Filter Options"),
        html.Div(children=exfor_energy_selector(pageparam)),
        html.Div(children=exfor_year_filter(pageparam)),
        html.Br(),
        html.Div(children=excl_mxw_switch(pageparam)),
        html.Br(),
        html.Label("Measured for"),
        dcc.Dropdown(
            id="reac_branch_fy",
            options=[{"label": l, "value": l} for l, i in MT_BRANCH_LIST_FY.items()],
            placeholder="Options",
            persistence=True,
            persistence_type="memory",
            value=query_strings["fy_type"].capitalize()
            if query_strings.get("fy_type")
            else "Cumulative",
            style={"font-size": "small", "width": "100%"},
        ),
        dcc.RadioItems(
            id="mesurement_opt_fy",
            options=[
                {"label": "Mass [MASS]", "value": "A"},
                {"label": "Element [ELEM]", "value": "Z"},
                {"label": "Product [ELEM/MASS]", "value": "Product"},
            ],
            value="A",
        ),
        html.Label("Product", style={"font-size": "small"}),
        dcc.Dropdown(
            id="reac_product_fy",
            options=[],
            placeholder="Options",
            persistence=True,
            persistence_type="memory",
            multi=True,
            style={"font-size": "small", "width": "100%"},
        ),
        html.Br(),
        html.Br(),
        html.Div(children=libs_filter_opt(pageparam)),
        dcc.Store(id="input_store_fy"),
    ]


## Layout of right panel
right_layout_fy = [
    libs_navbar,
    html.Hr(
        style={
            "border": "3px",
            "border-top": "1px solid",
            "margin-top": "5px",
            "margin-bottom": "5px",
        }
    ),
    html.Div(id="search_result_txt_fy"),
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
    dbc.Row(
        [
            dbc.Col(html.Label("Plot by"), width="auto"),
            dbc.Col(
                dcc.RadioItems(
                    id="plot_opt_fy",
                    options=["Mass", "Charge", "Energy"],
                    value="Mass",
                    labelStyle={"display": "inline-block"},
                ),
                width="auto",
            ),
        ]
    ),
    main_fig(pageparam),
    dcc.Store(id="entries_store_fy"),
    dcc.Store(id="libs_store_fy"),
    html.Hr(style={"border": "3px", "border-top": "1px solid"}),
    create_tabs(pageparam),
    footer,
]


def layout(**query_strings):
    return html.Div(
        [
            dcc.Location(id="location_fy"),
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
                                    html.Div(input_fy(**query_strings)),
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
                                children=right_layout_fy,
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
    [
        Output("location_fy", "href", allow_duplicate=True),
        Output("location_fy", "refresh", allow_duplicate=True),
    ],
    Input("dataset", "value"),
    prevent_initial_call=True,
)
def redirect_to_pages_fy(dataset):
    if dataset:
        return page_urls[dataset], True

    else:
        raise PreventUpdate


@callback(
    [
        Output("location_fy", "href", allow_duplicate=True),
        Output("location_fy", "refresh", allow_duplicate=True),
    ],
    Input("observable_fy", "value"),
    prevent_initial_call=True,
)
def redirect_to_subpages_fy(type):
    # print("redirect_to_subpages")
    if type:
        return lib_page_urls[type], True  # , dict({"type": type})

    else:
        raise PreventUpdate


@callback(
    Output("input_store_fy", "data"),
    [
        Input("observable_fy", "value"),
        Input("target_elem_fy", "value"),
        Input("target_mass_fy", "value"),
        Input("reaction_fy", "value"),
        Input("reac_branch_fy", "value"),
        Input("mesurement_opt_fy", "value"),
        Input("reac_product_fy", "value"),
        Input("exclude_mxw_switch_fy", "value"),
    ],
    # prevent_initial_call=True,
)
def input_store_fy(
    type,
    elem,
    mass,
    reaction,
    fy_type,
    mesurement_opt_fy,
    reac_product_fy,
    excl_junk_switch,
):
    # print("input_store_fy", type)
    if type != "FY":
        return dict({"type": type})

    elem, mass, reaction = input_check(type, elem, mass, reaction)

    return dict(
        {
            "type": type,
            "target_elem": elem,
            "target_mass": mass,
            "reaction": reaction,
            "fy_type": fy_type,
            "branch": MT_BRANCH_LIST_FY[fy_type]["branch"]
            if MT_BRANCH_LIST_FY.get(fy_type)
            else None,  # fy_type in query string
            "mt": MT_BRANCH_LIST_FY[fy_type]["mt"]
            if MT_BRANCH_LIST_FY.get(fy_type)
            else None,
            "mesurement_opt_fy": mesurement_opt_fy,
            "reac_product_fy": reac_product_fy,
            "excl_junk_switch": excl_junk_switch,
        }
    )


@callback(
    [
        Output("location_fy", "search"),
        Output("location_fy", "refresh", allow_duplicate=True),
    ],
    Input("input_store_fy", "data"),
    prevent_initial_call=True,
)
def update_url_fy(input_store):
    # print("update_url", input_store)

    if input_store:
        type = input_store.get("type").upper()
        elem = input_store.get("target_elem")
        mass = input_store.get("target_mass")
        reaction = input_store.get("reaction")
        # branch = input_store.get("branch")
        fy_type = input_store.get("fy_type")

    else:
        raise PreventUpdate

    if type == "FY" and (elem and mass and reaction):
        query_string = ""
        if elem:
            query_string += "?&target_elem=" + elem
        if mass:
            query_string += "&target_mass=" + mass
        if reaction:
            query_string += "&reaction=" + reaction
        if fy_type:
            query_string += "&fy_type=" + fy_type
        # if branch:
        #     query_string += "&branch=" + branch

        return query_string, False

    else:
        return no_update, False


@callback(
    [
        Output("search_result_txt_fy", "children"),
        Output("index_table_fy", "rowData"),
        Output("entries_store_fy", "data"),
        Output("libs_store_fy", "data"),
    ],
    [
        Input("input_store_fy", "data"),
        Input("rest_btn_fy", "n_clicks"),
    ],
    prevent_initial_call=True,
)
def initial_data_fy(input_store, r_click):
    # print("initial_data_fy")
    if input_store:
        if ctx.triggered_id != "rest_btn_fy":
            no_update

        ## search_result,
        ## index_df.to_dict("records"),
        ## legends,
        ## libs,
        return get_indexes(input_store)

    else:
        raise PreventUpdate


@callback(
    [
        Output("main_fig_fy", "figure", allow_duplicate=True),
        Output("reac_product_fy", "options"),
        Output("exfor_table_fy", "rowData"),
        Output("index_table_fy", "filterModel", allow_duplicate=True),
    ],
    [
        Input("input_store_fy", "data"),
        Input("energy_unit_fy", "value"),
        Input("entries_store_fy", "data"),
        Input("libs_store_fy", "data"),
        Input("endf_selct_fy", "value"),
        Input("plot_opt_fy", "value"),
    ],
    prevent_initial_call=True,
)
def create_fig_fy(input_store, energy_unit, legends, libs, endf_selct, plot_opt_fy):
    # print("create_fig")
    if input_store:
        reaction = input_store.get("reaction")
        mesurement_opt_fy = input_store.get("mesurement_opt_fy")
        reac_product_fy = input_store.get("reac_product_fy")

    else:
        raise PreventUpdate

    lower = float( ENERGIES[energy_unit][0] )
    upper = float( ENERGIES[energy_unit][1] )
    filter_model = {}

    if energy_unit != "All":
        filter_model = {
            "e_inc_min": {
                "filterType": "number",
                "type": "greaterThanOrEqual",
                "filter": lower,
            },
            "e_inc_max": {
                "filterType": "number",
                "type": "lessThanOrEqual",
                "filter": upper,
            },
        }


    fig = go.Figure(
        layout=go.Layout(
            xaxis={
                "title": "Incident energy [MeV]",
                "type": "linear",
                "range": [70, 180],
                "autorange": True if reaction[0] != "n" else False,
                "rangeslider": {
                    "bgcolor": "White",
                    "visible": True,
                    "autorange": True,
                    "thickness": 0.2,
                },
            },
            yaxis={
                "title": "Cross section [barn]",
                "type": "linear",
                "fixedrange": False,
            },
            margin={"l": 40, "b": 40, "t": 30, "r": 0},
        )
    )

    lib_df = pd.DataFrame()
    if libs:
        if endf_selct:
            libs_select = [k for k, l in libs.items() if l in endf_selct]
        else:
            libs_select = libs.keys()

        lib_df = lib_fy_data_query(libs_select)
        lib_df = lib_df[(lib_df["en_inc"] >= lower) & (lib_df["en_inc"] < upper)]
        print(lib_df)

        if plot_opt_fy == "Mass":
            x_ax = "mass"
            dff = lib_df.groupby(["reaction_id", "mass", "en_inc"], as_index=False)[
                "data"
            ].max(numeric_only=True)

            for l in libs_select:
                line_color = color_libs(libs[l])
                new_col = next(line_color)

                fig.add_trace(
                    go.Scatter(
                        x=dff[dff["reaction_id"] == int(l)]["mass"].astype(float),
                        y=dff[dff["reaction_id"] == int(l)]["data"].astype(float),
                        showlegend=True,
                        line_color=new_col,
                        name=str(libs[l]),
                        mode="lines",
                    )
                )

            fig.update_layout(
                dict(xaxis={"title": "Mass number"}, xaxis_range=[60, 180])
            )

        elif plot_opt_fy == "Charge":
            x_ax = "charge"
            dff = lib_df.groupby(["reaction_id", "charge", "en_inc"], as_index=False)[
                "data"
            ].max(numeric_only=True)

            for l in libs_select:
                line_color = color_libs(libs[l])
                new_col = next(line_color)

                fig.add_trace(
                    go.Scatter(
                        x=dff[dff["reaction_id"] == int(l)]["charge"].astype(float),
                        y=dff[dff["reaction_id"] == int(l)]["data"].astype(float),
                        showlegend=True,
                        line_color=new_col,
                        name=str(libs[l]),
                        mode="lines",
                    )
                )
            fig.update_layout(
                dict(xaxis={"title": "Charge number"}, xaxis_range=[20, 80])
            )

        elif plot_opt_fy == "Energy":
            x_ax = "en_inc"
            fig.update_layout(
                dict(xaxis={"title": "Incident energy [MeV]"}, xaxis_range=[0, 20])
            )

    reac_products = []
    df = pd.DataFrame()

    if legends:
        df = data_query(input_store, legends.keys())
        df = df[(df["en_inc"] >= lower) & (df["en_inc"] < upper)]
        df["bib"] = df["entry_id"].map(legends)
        df = pd.concat([df, df["bib"].apply(pd.Series)], axis=1)
        df = df.drop(columns=["bib"])

        df["entry_id_link"] = (
            "["
            + df["entry_id"]
            + "]("
            + URL_PATH
            + "exfor/entry/"
            + df["entry_id"]
            + ")"
        )
        # print(df)
        reac_products = sorted([i for i in df["residual"].unique() if i is not None])
        # print(reac_products)
        i = 0
        for e in list(legends.keys()):
            if e == "total_points":
                continue

            df2 = df[df["entry_id"] == e]

            # Filtered by reaction product
            if reac_product_fy:
                df2 = df2[df2["residual"].isin(reac_product_fy)]

            if mesurement_opt_fy == "A":
                x_ax = "mass"

            elif mesurement_opt_fy == "Z":
                x_ax = "charge"

            else:
                x_ax = "mass"

            if plot_opt_fy == "Mass":
                x_ax = "mass"
                fig.update_layout(dict(xaxis={"title": "Mass number"}))

            elif plot_opt_fy == "Charge":
                x_ax = "charge"
                fig.update_layout(dict(xaxis={"title": "Charge number"}))

            elif plot_opt_fy == "Energy":
                x_ax = "en_inc"
                fig.update_layout(dict(xaxis={"title": "Incident energy [MeV]"}))

            i = 0
            # ------

            fig.add_trace(
                go.Scatter(
                    x=df2[df2["entry_id"] == e][x_ax],
                    y=df2[df2["entry_id"] == e]["data"],
                    error_y=dict(type="data", array=df[df["entry_id"] == e]["ddata"]),
                    showlegend=True,
                    name=f"{legends[e]['author']}, {legends[e]['year']} [{e}]"
                    if legends.get(e)
                    and legends[e].get("author")
                    and legends[e].get("year")
                    else f"{legends[e]['author']}, 1900 [{e}]"
                    if legends.get(e)
                    else e,
                    marker=dict(size=8, symbol=i),
                    mode="markers",
                )
            )
            i += 1

            if i == 30:
                i = 1
        # ------

    return fig, reac_products, df.to_dict("records"), filter_model


@callback(
    Output("main_fig_fy", "figure", allow_duplicate=True),
    [
        Input("xaxis_type", "value"),
        Input("yaxis_type", "value"),
    ],
    State("main_fig_fy", "figure"),
    prevent_initial_call=True,
)
def update_axis_fy(xaxis_type, yaxis_type, fig):
    ## Switch the axis type
    fig.get("layout").get("yaxis").update({"type": yaxis_type})
    fig.get("layout").get("xaxis").update({"type": xaxis_type})

    return fig


# @callback(
#     Output("index_table_fy", "filterModel", allow_duplicate=True),
#     Input("energy_unit_fy", "value"),
#     prevent_initial_call=True,
# )
# def fileter_by_en_range_fy(energy_unit):
#     if energy_unit:
#         filter_model = {
#             "e_inc_min": {
#                 "filterType": "number",
#                 "type": "greaterThan",
#                 "filter": float( ENERGIES[energy_unit][0] ),
#             },
#             "e_inc_max": {
#                 "filterType": "number",
#                 "type": "lessThan",
#                 "filter": float( ENERGIES[energy_unit][1] ),
#             },
#         }
#         return filter_model
#     else:
#         return no_update


@callback(
    [
        Output("main_fig_fy", "figure", allow_duplicate=True),
        Output("index_table_fy", "filterModel", allow_duplicate=True),
    ],
    Input("year_range_fy", "value"),
    State("main_fig_fy", "figure"),
    prevent_initial_call=True,
)
def fileter_by_year_range_fy(year_range, fig):
    return filter_by_year_range(year_range, fig)


@callback(
    Output("main_fig_fy", "figure", allow_duplicate=True),
    Input("index_table_fy", "selectedRows"),
    State("main_fig_fy", "figure"),
    prevent_initial_call=True,
)
def highlight_data_fy(selected, fig):
    return highlight_data(selected, fig)


@callback(
    Output("main_fig_fy", "figure", allow_duplicate=True),
    Input("index_table_fy", "cellValueChanged"),
    State("main_fig_fy", "figure"),
    prevent_initial_call=True,
)
def scale_data_fy(selected, fig):
    return scale_data(selected, fig)


@callback(
    [
        Output("main_fig_fy", "figure", allow_duplicate=True),
        Output("index_table_fy", "rowTransaction"),
    ],
    Input("del_btn_fy", "n_clicks"),
    [
        State("main_fig_fy", "figure"),
        State("index_table_fy", "selectedRows"),
    ],
    prevent_initial_call=True,
)
def del_rows_fy(n1, fig, selected):
    if n1:
        if selected is None:
            return no_update, no_update
        return del_rows_fig(selected, fig)


@callback(
    [
        Output("index_table_fy", "exportDataAsCsv"),
        Output("index_table_fy", "csvExportParams"),
    ],
    [
        Input("btn_csv_index_fy", "n_clicks"),
        Input("btn_csv_index_selct_fy", "n_clicks"),
        Input("input_store_fy", "data"),
    ],
    prevent_initial_call=True,
)
def export_index_fy(n1, n2, input_store):
    # return export_index(n_clicks_all, n_clicks_slctd, input_store)
    if not input_store:
        raise PreventUpdate

    if ctx.triggered_id == "btn_csv_index_fy":
        return export_index(False, input_store)

    elif ctx.triggered_id == "btn_csv_index_selct_fy":
        return export_index(True, input_store)

    else:
        return no_update, no_update


@callback(
    [
        Output("exfor_table_fy", "exportDataAsCsv"),
        Output("exfor_table_fy", "csvExportParams"),
    ],
    [
        Input("btn_csv_exfor_fy", "n_clicks"),
        Input("btn_csv_exfor_selct_fy", "n_clicks"),
        Input("input_store_fy", "data"),
    ],
    prevent_initial_call=True,
)
def export_data_fy(n1, n2, input_store):
    # return export_data(n_clicks_all, n_clicks_slctd, input_store)
    if not input_store:
        raise PreventUpdate

    if ctx.triggered_id == "btn_csv_exfor_fy":
        return export_data(False, input_store)

    elif ctx.triggered_id == "btn_csv_exfor_selct_fy":
        return export_data(True, input_store)

    else:
        return no_update, no_update


@callback(
    [
        Output("btn_api_fy", "href"),
        Output("btn_api_data_fy", "href"),
    ],
    Input("location_fy", "search"),
)
def generate_api_links_fy(search_str):
    return generate_api_link(pageparam, search_str)


@callback(
    [
        Output("exfiles_link_fy", "children"),
        Output("libfiles_link_fy", "children"),
    ],
    Input("input_store_fy", "data"),
)
def generate_file_links_fy(input_store):
    if not input_store:
        raise PreventUpdate

    dir_ex, files_ex = generate_exfortables_file_path(input_store)
    dir_lib, files_lib = generate_endftables_file_path(input_store)

    return list_link_of_files(dir_ex, files_ex), list_link_of_files(dir_lib, files_lib)
