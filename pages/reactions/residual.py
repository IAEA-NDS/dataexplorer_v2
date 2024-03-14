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
from dash import Dash, html, dcc, Input, Output, State, ctx, no_update, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate

from pages_common import (
    PARTICLE,
    sidehead,
    footer,
    libs_navbar,
    page_urls,
    lib_page_urls,
    def_inp_values,
    URL_PATH,
    main_fig,
    input_check,
    input_obs,
    input_target,
    input_residual,
    input_check_elem,
    exfor_filter_opt,
    limit_number_of_datapoints,
    libs_filter_opt,
    input_lin_log_switch,
    reduce_data_switch,
    excl_mxw_switch,
    get_indexes,
    scale_data,
    del_rows_fig,
    highlight_data,
    filter_by_year_range,
    fileter_by_en_range,
    export_index,
    export_data,
    list_link_of_files,
    generate_api_link,
)

from modules.reactions.list import color_libs
from modules.reactions.tabs import create_tabs
from modules.reactions.figs import default_chart

from submodules.utilities.util import split_by_number
from submodules.common import (
    generate_exfortables_file_path,
    generate_endftables_file_path,
)
from submodules.reactions.queries import (
    lib_residual_data_query,
    lib_residual_nuclide_list,
)
from submodules.exfor.queries import data_query


## Registration of page
dash.register_page(
    __name__,
    path="/reactions/residual",
    redirect_from=["/residual", "/rp", "/reactions/rp"],
)
pageparam = "rp"


## Input layout
def input_lib(**query_strings):
    return [
        html.Br(),
        html.Div(children=input_obs(pageparam)),
        html.Div(children=input_target(pageparam, **query_strings)),
        html.P("Reaction"),
        dcc.Dropdown(
            id="inc_pt_rp",
            options=[
                {"label": f"{pt.lower()},x", "value": pt.upper()} for pt in PARTICLE
            ],
            placeholder="Reaction e.g. (p,x)",
            persistence=True,
            persistence_type="memory",
            value=query_strings["inc_pt"].upper()
            if query_strings.get("inc_pt")
            else def_inp_values[pageparam.upper()]["inc_pt"],
            style={"font-size": "small", "width": "100%"},
        ),
        html.Div(children=input_residual(pageparam, **query_strings)),
        html.Br(),
        html.Br(),
        html.Div(children=exfor_filter_opt(pageparam)),
        html.Br(),
        html.Div(children=reduce_data_switch(pageparam)),
        html.Div(children=excl_mxw_switch(pageparam)),
        html.Br(),
        html.Br(),
        html.Div(children=libs_filter_opt(pageparam)),
        dcc.Store(id="input_store_rp"),
    ]


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
    html.Div(id="search_result_txt_rp"),
    # Log/Linear switch
    html.Div(children=input_lin_log_switch(pageparam)),
    main_fig(pageparam),
    dcc.Store(id="entries_store_rp"),
    dcc.Store(id="libs_store_rp"),
    html.Hr(style={"border": "3px", "border-top": "1px solid"}),
    create_tabs(pageparam),
    footer,
]


## Main layout of libraries-2023 page
# layout = html.Div(
def layout(**query_strings):
    return html.Div(
        [
            dcc.Location(id="location_rp"),
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


###------------------------------------------------------------------------------------
### App Callback
###------------------------------------------------------------------------------------
@callback(
    [
        Output("location_rp", "href", allow_duplicate=True),
        Output("location_rp", "refresh", allow_duplicate=True),
    ],
    Input("dataset", "value"),
    prevent_initial_call=True,
)
def redirect_to_pages_rp(dataset):
    if dataset:
        return page_urls[dataset], True

    else:
        raise PreventUpdate


@callback(
    [
        Output("location_rp", "href", allow_duplicate=True),
        Output("location_rp", "refresh", allow_duplicate=True),
    ],
    Input("observable_rp", "value"),
    prevent_initial_call=True,
)
def redirect_to_subpages_rp(type):
    if type:
        return lib_page_urls[type], True

    else:
        raise PreventUpdate


@callback(
    [
        Output("rp_elem_rp", "placeholder"),
        Output("rp_mass_rp", "placeholder"),
        # Output('list-suggested-inputs', 'children'),
        # Output('list-suggested-inputs2', 'children'),
    ],
    [
        Input("target_elem_rp", "value"),
        Input("target_mass_rp", "value"),
        Input("inc_pt_rp", "value"),
        Input("rp_elem_rp", "value"),
    ],
)
def list_rp(elem, mass, inc_pt, rp_elem_rp):
    elem, mass, _ = input_check(type, elem, mass, f"{inc_pt.lower()},x")

    # run query to get list of possible residual nuclide
    rp_list = lib_residual_nuclide_list(elem, mass, inc_pt)

    if not rp_list:
        raise PreventUpdate

    rp_dict = {}
    for rp in rp_list:
        nuclide = split_by_number(rp)

        if not rp_dict.get(nuclide[0]):
            rp_dict[nuclide[0]] = ["".join(nuclide[1:])]

        else:
            rp_dict[nuclide[0]].append("".join(nuclide[1:]))

    if rp_elem_rp:
        rp_elem_rp = input_check_elem(rp_elem_rp)

        return (
            "e.g, " + ", ".join(rp_dict.keys()),
            "e.g, " + ", ".join([m.lstrip("0") for m in rp_dict[rp_elem_rp]])
            if rp_dict.get(rp_elem_rp)
            else "",
        )

    else:
        return "e.g, " + ", ".join(rp_dict.keys()), ""



@callback(
    Output("input_store_rp", "data"),
    [
        Input("observable_rp", "value"),
        Input("target_elem_rp", "value"),
        Input("target_mass_rp", "value"),
        Input("inc_pt_rp", "value"),
        Input("rp_elem_rp", "value"),
        Input("rp_mass_rp", "value"),
        Input("exclude_mxw_switch_rp", "value"),
    ],
    # prevent_initial_call=True,
)
def input_store_rp(type, elem, mass, inc_pt, rp_elem, rp_mass, excl_junk_switch):
    elem, mass, _ = input_check(type, elem, mass, f"{inc_pt.lower()},x")

    rp_elem, rp_mass, _ = input_check(type, rp_elem, rp_mass, f"{inc_pt.lower()},x")

    if type != "RP":
        return dict(
            {
                "type": type,
                "target_elem": elem,
                "target_mass": mass,
                "reaction": f"{inc_pt.lower()},x",
            }
        )
    else:
        return dict(
            {
                "type": type,
                "target_elem": elem,
                "target_mass": mass,
                "reaction": f"{inc_pt.lower()},x",
                "inc_pt": inc_pt,
                "rp_elem": rp_elem,
                "rp_mass": rp_mass,
                "level_num": None,
                "branch": None,
                "mt": None,
                "excl_junk_switch": excl_junk_switch,
            }
        )




@callback(
    [
        Output("location_rp", "search"),
        Output("location_rp", "refresh", allow_duplicate=True),
    ],
    Input("input_store_rp", "data"),
    prevent_initial_call=True,
)
def update_url_rp(input_store):

    if input_store:
        type = input_store.get("type").upper()
        elem = input_store.get("target_elem")
        mass = input_store.get("target_mass")
        inc_pt = input_store.get("inc_pt")
        rp_elem = input_store.get("rp_elem")
        rp_mass = input_store.get("rp_mass")

    else:
        raise PreventUpdate

    if type == "RP" and elem and mass and inc_pt and rp_elem and rp_mass:
        query_string = ""
        if elem:
            query_string += "?&target_elem=" + elem

        if mass:
            query_string += "&target_mass=" + mass

        if inc_pt:
            query_string += "&inc_pt=" + inc_pt

        if rp_elem:
            query_string += "&rp_elem=" + rp_elem

        if rp_mass:
            query_string += "&rp_mass=" + rp_mass

        return query_string, False

    else:
        return no_update, False
        # raise PreventUpdate




@callback(
    [
        Output("search_result_txt_rp", "children"),
        Output("index_table_rp", "rowData"),
        Output("entries_store_rp", "data"),
        Output("libs_store_rp", "data"),
    ],
    [
        Input("input_store_rp", "data"),
        Input("rest_btn_rp", "n_clicks"),
    ],
    prevent_initial_call=True,
)
def initial_data_rp(input_store, r_click):
    # print("initial_data_rp", input_store)
    if input_store:
        if ctx.triggered_id != "rest_btn_rp":
            no_update

        return get_indexes(input_store)

    else:
        raise PreventUpdate


@callback(
    [
        Output("main_fig_rp", "figure", allow_duplicate=True),
        Output("exfor_table_rp", "rowData"),
        Output("xaxis_type_rp", "value"),
        Output("yaxis_type_rp", "value"),
    ],
    [
        Input("input_store_rp", "data"),
        Input("entries_store_rp", "data"),
        Input("libs_store_rp", "data"),
        Input("endf_selct_rp", "value"),
        Input("reduce_data_switch_rp", "value"),
    ],
    prevent_initial_call=True,
)
def create_fig_rp(input_store, legends, libs, endf_selct, switcher):
    # print("create_fig_rp")
    if input_store:
        inc_pt = input_store.get("inc_pt")

    else:
        raise PreventUpdate

    if inc_pt == "n":
        xaxis_type, yaxis_type = "log", "log"

    else:
        xaxis_type, yaxis_type = "linear", "linear"

    fig = default_chart(xaxis_type, yaxis_type, reaction=inc_pt)

    lib_df = pd.DataFrame()
    if libs:
        if endf_selct:
            libs_select = [k for k, l in libs.items() if l in endf_selct]
        else:
            libs_select = libs.keys()

        lib_df = lib_residual_data_query(inc_pt, libs_select)

        for l in libs_select:
            line_color = color_libs(libs[l])
            new_col = next(line_color)

            fig.add_trace(
                go.Scatter(
                    x=lib_df[lib_df["reaction_id"] == int(l)]["en_inc"].astype(float),
                    y=lib_df[lib_df["reaction_id"] == int(l)]["data"].astype(float),
                    showlegend=True,
                    line_color=new_col,
                    name=str(libs[l]),
                    mode="lines",
                )
            )

    df = pd.DataFrame()
    if legends:
        df = data_query(input_store, legends.keys())
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
        i = 0
        for e in list(legends.keys()):
            if e == "total_points":
                continue

            if switcher:
                df2 = limit_number_of_datapoints(
                    legends[e]["points"], df[df["entry_id"] == e]
                )

            else:
                df2 = df[df["entry_id"] == e]

            fig.add_trace(
                go.Scatter(
                    x=df2["en_inc"],
                    y=df2["data"],
                    error_x=dict(type="data", array=df2["den_inc"]),
                    error_y=dict(type="data", array=df2["ddata"]),
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

    return fig, df.to_dict("records"), xaxis_type, yaxis_type



@callback(
    Output("main_fig_rp", "figure", allow_duplicate=True),
    [
        Input("xaxis_type_rp", "value"),
        Input("yaxis_type_rp", "value"),
    ],
    State("main_fig_rp", "figure"),
    prevent_initial_call=True,
)
def update_axis_rp(xaxis_type, yaxis_type, fig):
    ## Switch the axis type
    fig.get("layout").get("yaxis").update({"type": yaxis_type})
    fig.get("layout").get("xaxis").update({"type": xaxis_type})

    return fig



@callback(
    [
        Output("main_fig_rp", "figure", allow_duplicate=True),
        Output("index_table_rp", "filterModel", allow_duplicate=True),
        Output("output_energy_slider_rp", "children"),
    ],
    Input("energy_range_rp", "value"),
    State("main_fig_rp", "figure"),
    prevent_initial_call=True,
)
def fileter_by_en_range_rp(energy_range, fig):
    range_text = ""
    fig, filter_model = fileter_by_en_range(energy_range, fig)
    if filter_model:
        range_text = f"{filter_model['e_inc_min']['filter']:.2e} - {filter_model['e_inc_max']['filter']:.2e} MeV"
    return fig, filter_model, range_text



@callback(
    [
        Output("main_fig_rp", "figure", allow_duplicate=True),
        Output("index_table_rp", "filterModel", allow_duplicate=True),
    ],
    Input("year_range_rp", "value"),
    State("main_fig_rp", "figure"),
    prevent_initial_call=True,
)
def fileter_by_year_range_rp(year_range, fig):
    return filter_by_year_range(year_range, fig)


@callback(
    Output("main_fig_rp", "figure", allow_duplicate=True),
    Input("index_table_rp", "selectedRows"),
    State("main_fig_rp", "figure"),
    prevent_initial_call=True,
)
def highlight_data_rp(selected, fig):
    return highlight_data(selected, fig)


@callback(
    Output("main_fig_rp", "figure", allow_duplicate=True),
    Input("index_table_rp", "cellValueChanged"),
    State("main_fig_rp", "figure"),
    prevent_initial_call=True,
)
def scale_data_rp(selected, fig):
    return scale_data(selected, fig)



@callback(
    [
        Output("main_fig_rp", "figure", allow_duplicate=True),
        Output("index_table_rp", "rowTransaction"),
    ],
    Input("del_btn_rp", "n_clicks"),
    [
        State("main_fig_rp", "figure"),
        State("index_table_rp", "selectedRows"),
    ],
    prevent_initial_call=True,
)
def del_rows_rp(n1, fig, selected):
    if n1:
        if selected is None:
            return no_update
        return del_rows_fig(selected, fig)



@callback(
    [
        Output("index_table_rp", "exportDataAsCsv"),
        Output("index_table_rp", "csvExportParams"),
    ],
    [
        Input("btn_csv_index_rp", "n_clicks"),
        Input("btn_csv_index_selct_rp", "n_clicks"),
        Input("input_store_rp", "data"),
    ],
    prevent_initial_call=True,
)
def export_index_rp(n1, n2, input_store):
    # return export_index(n_clicks_all, n_clicks_slctd, input_store)
    if not input_store:
        raise PreventUpdate

    if ctx.triggered_id == "btn_csv_index_rp":
        return export_index(False, input_store)

    elif ctx.triggered_id == "btn_csv_index_selct_rp":
        return export_index(True, input_store)

    else:
        return no_update, no_update



@callback(
    [
        Output("exfor_table_rp", "exportDataAsCsv"),
        Output("exfor_table_rp", "csvExportParams"),
    ],
    [
        Input("btn_csv_exfor_rp", "n_clicks"),
        Input("btn_csv_exfor_selct_rp", "n_clicks"),
        Input("input_store_rp", "data"),
    ],
    prevent_initial_call=True,
)
def export_data_rp(n1, n2, input_store):
    # return export_data(n_clicks_all, n_clicks_slctd, input_store)
    if not input_store:
        raise PreventUpdate

    if ctx.triggered_id == "btn_csv_exfor_rp":
        return export_data(False, input_store)

    elif ctx.triggered_id == "btn_csv_exfor_selct_rp":
        return export_data(True, input_store)

    else:
        return no_update, no_update



@callback(
    [
        Output("btn_api_rp", "href"),
        Output("btn_api_data_rp", "href"),
    ],
    Input("location_rp", "search"),
)
def generate_api_links_rp(search_str):
    return generate_api_link(pageparam, search_str)



@callback(
    [
        Output("exfiles_link_rp", "children"),
        Output("libfiles_link_rp", "children"),
    ],
    Input("input_store_rp", "data"),
)
def generate_file_links_rp(input_store):
    if not input_store:
        raise PreventUpdate

    dir_ex, files_ex = generate_exfortables_file_path(input_store)
    dir_lib, files_lib = generate_endftables_file_path(input_store)

    return list_link_of_files(dir_ex, files_ex), list_link_of_files(dir_lib, files_lib)




