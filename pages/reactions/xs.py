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
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate


from pages_common import (
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
    input_general,
    input_partial,
    generate_reactions,
    remove_query_parameter,
    limit_number_of_datapoints,
    exfor_energy_filter,
    exfor_year_filter,
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
    generate_api_link,
    generate_file_link,
)

# from config import BASE_URL
from modules.reactions.list import color_libs
from modules.reactions.tabs import create_tabs
from modules.reactions.figs import default_chart, default_axis, update_axis
from submodules.utilities.reaction import get_mt
from submodules.reactions.queries import lib_xs_data_query
from submodules.exfor.queries import data_query
from submodules.utilities.util import get_number_from_string


## Registration of page
dash.register_page(
    __name__,
    path="/reactions/xs",
    title="Nuclear Reaction Cross Section",
    redirect_from=["/xs", "/cs", "/crosssection", "/reactions/cs", "/reactions", "/reactions/"],
)
pageparam = "xs"


## Input layout
def input_lib(**query_strings):
    # if query_strings["type"] == "SIG":
    return [
        html.Br(),
        html.Div(children=input_obs(pageparam)),
        html.Div(children=input_target(pageparam, **query_strings)),
        html.Div(children=input_general(pageparam, **query_strings)),
        html.Div(children=input_partial(pageparam, **query_strings)),
        html.Br(),
        html.P("EXFOR Filter Options"),
        html.Div(children=exfor_energy_filter(pageparam)),
        html.Div(children=exfor_year_filter(pageparam)),
        html.Br(),
        html.Div(children=reduce_data_switch(pageparam)),
        html.Div(children=excl_mxw_switch(pageparam)),
        html.Br(),
        html.Br(),
        html.Div(children=libs_filter_opt(pageparam)),
        dcc.Store(id="input_store_xs"),
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
    html.Div(id="search_result_txt"),
    # Log/Linear switch
    html.Div(children=input_lin_log_switch(pageparam)),
    # main_fig,
    dcc.Loading(
        children=main_fig(pageparam),
        type="circle",
    ),
    dcc.Store(id="entries_store"),
    dcc.Store(id="libs_store"),
    html.Hr(style={"border": "3px", "border-top": "1px solid"}),
    create_tabs(pageparam),
    footer,
]


## Main layout of libraries-2023 page
# layout = html.Div(
def layout(**query_strings):
    return html.Div(
        [
            dcc.Location(id="location"),
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
                                    html.Div(children=input_lib(**query_strings)),
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
        Output("location", "href", allow_duplicate=True),
        Output("location", "refresh", allow_duplicate=True),
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
        Output("location", "href", allow_duplicate=True),
        Output("location", "refresh", allow_duplicate=True),
    ],
    Input("observable_xs", "value"),
    prevent_initial_call=True,
)
def redirect_to_subpages(type):
    if type:
        return lib_page_urls[type], True  # , dict({"type": type})

    else:
        raise PreventUpdate


@callback(
    Output("reaction_xs", "options"),
    Input("incident_particle_xs", "value"),
)
def update_reaction_list(proj):
    if not proj:
        raise PreventUpdate

    else:
        return generate_reactions(proj)


@callback(
    Output("reac_branch_xs", "options"),
    [
        Input("observable_xs", "value"),
        Input("reaction_xs", "value"),
    ],
)
def update_branch_list(type, reaction):
    if type != "XS":
        raise PreventUpdate

    if not reaction:
        raise PreventUpdate

    return [{"label": "Partial", "value": "PAR"}]


@callback(
    Output("input_store_xs", "data"),
    [
        Input("observable_xs", "value"),
        Input("target_elem_xs", "value"),
        Input("target_mass_xs", "value"),
        Input("reaction_xs", "value"),
        Input("reac_branch_xs", "value"),
        Input("exclude_mxw_switch_xs", "value"),
    ],
)
def input_store_xs(type, elem, mass, reaction, branch, excl_junk_switch):
    if type != "XS":
        return dict({"type": type})

    elem, mass, reaction = input_check(type, elem, mass, reaction)
    mt = get_mt(reaction)

    if reaction.split(",")[1][-1].isdigit():
        ## such as n,n1, n,n2 but not n,2n
        level_num = int(get_number_from_string(reaction.split(",")[1]))
    else:
        level_num = None

    return dict(
        {
            "type": type,
            "target_elem": elem,
            "target_mass": mass,
            "reaction": reaction,
            "inc_pt": reaction.split(",")[0].upper() if reaction else None,
            "rp_elem": None,
            "rp_mass": None,
            "level_num": level_num,
            "branch": branch,
            "mt": mt,
            "excl_junk_switch": excl_junk_switch,
        }
    )


@callback(
    [
        Output("location", "search"),
        Output("location", "refresh", allow_duplicate=True),
    ],
    Input("input_store_xs", "data"),
    prevent_initial_call=True,
)
def update_url(input_store):
    if input_store:
        type = input_store.get("type").upper()
        elem = input_store.get("target_elem")
        mass = input_store.get("target_mass")
        reaction = input_store.get("reaction")
        branch = input_store.get("branch")
    else:
        raise PreventUpdate

    if type == "XS" and elem and mass and reaction:
        query_string = ""
        if elem:
            query_string += "?&target_elem=" + elem

        if mass:
            query_string += "&target_mass=" + mass

        if reaction:
            query_string += "&reaction=" + reaction.replace("+", "%2B")

            if reaction.split(",")[1].upper() == "INL":
                if not branch:
                    pass

                elif isinstance(branch, int):
                    query_string += "&branch=" + str(branch)

            elif reaction.split(",")[1].upper() != "INL":
                if branch == "PAR":
                    query_string += "&branch=" + str(branch)

                else:
                    query_string = remove_query_parameter(query_string, "branch")

        return query_string, False

    else:
        return no_update, False


@callback(
    [
        Output("search_result_txt", "children"),
        Output("index_table_xs", "rowData"),
        Output("entries_store", "data"),
        Output("libs_store", "data"),
    ],
    [
        Input("input_store_xs", "data"),
        Input("rest_btn_xs", "n_clicks"),
    ],
    prevent_initial_call=True,
)
def initial_data_xs(input_store, r_click):
    if input_store:
        if ctx.triggered_id != "rest_btn_xs":
            no_update
        return get_indexes(input_store)

    else:
        raise PreventUpdate


@callback(
    [
        Output("main_fig_xs", "figure", allow_duplicate=True),
        Output("exfor_table_xs", "rowData"),
    ],
    [
        Input("input_store_xs", "data"),
        Input("entries_store", "data"),
        Input("libs_store", "data"),
        Input("endf_selct_xs", "value"),
        Input("reduce_data_switch_xs", "value"),
    ],
    prevent_initial_call=True,
)
def create_fig(input_store, legends, libs, endf_selct, switcher):
    if input_store:
        reaction = input_store.get("reaction")
        mt = input_store.get("mt")

    else:
        raise PreventUpdate

    if reaction.split(",")[0] == "n":
        xaxis_type, yaxis_type = default_axis(str(mt).zfill(3))

    else:
        xaxis_type = "linear"
        yaxis_type = "linear"

    fig = default_chart(xaxis_type, yaxis_type, reaction)

    lib_df = pd.DataFrame()
    if libs:
        if endf_selct:
            libs_select = [k for k, l in libs.items() if l in endf_selct]
        else:
            libs_select = libs.keys()

        lib_df = lib_xs_data_query(libs_select)

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

        if switcher:
            for e in list(legends.keys()):
                if e == "total_points":
                    continue

                if legends[e]["points"] > 100:
                    index = limit_number_of_datapoints(
                        legends[e]["points"], df[df["entry_id"] == e]
                    )
                    df.drop(index, inplace=True)

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

            df2 = df[df["entry_id"] == e]

            if legends["total_points"] > 1000 and not switcher:
                fig.add_trace(
                    go.Scattergl(
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

            else:
                fig.add_trace(
                    # go.Scattergl(
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

            if i > 30:
                i = 1

    return fig, df.to_dict("records")  # , xaxis_type, yaxis_type


@callback(
    Output("main_fig_xs", "figure", allow_duplicate=True),
    [
        Input("xaxis_type_xs", "value"),
        Input("yaxis_type_xs", "value"),
    ],
    [
        State("main_fig_xs", "figure"),
        State("input_store_xs", "data"),
    ],
    prevent_initial_call=True,
)
def update_axis_xs(xaxis_type, yaxis_type, fig, input_store):
    if input_store and xaxis_type and yaxis_type:
        mt = input_store.get("mt")
        return update_axis(mt, xaxis_type, yaxis_type, fig)
    else:
        return no_update


@callback(
    [
        Output("main_fig_xs", "figure", allow_duplicate=True),
        Output("index_table_xs", "filterModel", allow_duplicate=True),
        Output("output_energy_slider_xs", "children"),
    ],
    Input("energy_range_xs", "value"),
    State("main_fig_xs", "figure"),
    prevent_initial_call=True,
)
def fileter_by_en_range_xs(energy_range, fig):
    range_text = f"1.00e-8 - 1.00e+3 MeV"
    fig, filter_model = fileter_by_en_range(energy_range, fig)
    if filter_model:
        range_text = f"{filter_model['e_inc_min']['filter']:.2e} - {filter_model['e_inc_max']['filter']:.2e} MeV"
    return fig, filter_model, range_text


@callback(
    [
        Output("main_fig_xs", "figure", allow_duplicate=True),
        Output("index_table_xs", "filterModel", allow_duplicate=True),
    ],
    Input("year_range_xs", "value"),
    State("main_fig_xs", "figure"),
    prevent_initial_call=True,
)
def fileter_by_year_range_lib(year_range, fig):
    return filter_by_year_range(year_range, fig)


@callback(
    Output("main_fig_xs", "figure", allow_duplicate=True),
    Input("index_table_xs", "selectedRows"),
    State("main_fig_xs", "figure"),
    prevent_initial_call=True,
)
def highlight_data_xs(selected, fig):
    return highlight_data(selected, fig)


@callback(
    Output("main_fig_xs", "figure", allow_duplicate=True),
    Input("index_table_xs", "cellValueChanged"),
    State("main_fig_xs", "figure"),
    prevent_initial_call=True,
)
def scale_data_xs(selected, fig):
    return scale_data(selected, fig)


@callback(
    [
        Output("main_fig_xs", "figure", allow_duplicate=True),
        Output("index_table_xs", "rowTransaction"),
    ],
    Input("del_btn_xs", "n_clicks"),
    [
        State("main_fig_xs", "figure"),
        State("index_table_xs", "selectedRows"),
    ],
    prevent_initial_call=True,
)
def del_rows(n1, fig, selected):
    if n1:
        if selected is None:
            return no_update, no_update
        return del_rows_fig(selected, fig)


@callback(
    [
        Output("index_table_xs", "exportDataAsCsv"),
        Output("index_table_xs", "csvExportParams"),
    ],
    [
        Input("btn_csv_index_xs", "n_clicks"),
        Input("btn_csv_index_selct_xs", "n_clicks"),
        Input("input_store_xs", "data"),
    ],
    prevent_initial_call=True,
)
def export_index_xs(n1, n2, input_store):
    # return export_index(n_clicks_all, n_clicks_slctd, input_store)
    if not input_store:
        raise PreventUpdate

    if ctx.triggered_id == "btn_csv_index_xs":
        return export_index(False, input_store)

    elif ctx.triggered_id == "btn_csv_index_selct_xs":
        return export_index(True, input_store)

    else:
        return no_update, no_update


@callback(
    [
        Output("exfor_table_xs", "exportDataAsCsv"),
        Output("exfor_table_xs", "csvExportParams"),
    ],
    [
        Input("btn_csv_exfor_xs", "n_clicks"),
        Input("btn_csv_exfor_selct_xs", "n_clicks"),
        Input("input_store_xs", "data"),
    ],
    prevent_initial_call=True,
)
def export_data_xs(n1, n2, input_store):
    # return export_data(n_clicks_all, n_clicks_slctd, input_store)
    if not input_store:
        raise PreventUpdate

    if ctx.triggered_id == "btn_csv_exfor_xs":
        return export_data(False, input_store)

    elif ctx.triggered_id == "btn_csv_exfor_selct_xs":
        return export_data(True, input_store)

    else:
        return no_update, no_update


@callback(
    [
        Output("btn_api_xs", "href"),
        Output("btn_api_data_xs", "href"),
    ],
    Input("location", "search"),
)
def generate_api_links(search_str):
    return generate_api_link(pageparam, search_str)


@callback(
    [
        Output("dl_zip_ex_xs", "data"),
        Output("dl_zip_lib_xs", "data"),
        Output("exfiles_link_xs", "children"),
        Output("libfiles_link_xs", "children"),
    ],
    [
        Input("input_store_xs", "data"),
        Input("btn_zip_ex_xs", "n_clicks"),
        Input("btn_zip_lib_xs", "n_clicks"),
    ],
)
def generate_file_links(input_store, n_clicks_ex, n_clicks_lib):
    if not input_store:
        raise PreventUpdate

    else:
        return generate_file_link(input_store, n_clicks_ex, n_clicks_lib)
