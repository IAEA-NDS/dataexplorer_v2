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
from dash import Dash, html, dcc, Input, Output, State, ctx, no_update, callback
import dash_bootstrap_components as dbc
import dash_daq as daq
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate

from common import (
    sidehead,
    footer,
    libs_navbar,
    page_urls,
    lib_page_urls,
    main_fig,
    input_check,
    input_target,
    input_general,
    generate_reactions,
    get_mt,
    remove_query_parameter,
    exfor_filter_opt,
    excl_mxw_switch,
    get_indexes,
    scale_data,
    del_rows_fig,
    highlight_data,
    filter_by_year_range,
    fileter_by_en_range,
    export_index,
    export_data,
    generate_exfortables_file_path,
    generate_endftables_file_path,
)

from libraries.list import color_libs
from libraries.tabs import create_tabs

from submodules.exfor.queries import data_query
from submodules.libraries.queries import lib_da_data_query
from submodules.utilities.util import get_number_from_string

## Registration of page
dash.register_page(__name__, path="/reactions/da", redirect_from=["/angle", "/da", "/reactions/angle"])

pageparam = "da"


def input(**query_strings):
    return [
        html.Div(children=input_target(pageparam, **query_strings)),
        html.Div(children=input_general(pageparam, **query_strings)),
        html.Br(),
        html.Div(children=exfor_filter_opt(pageparam)),
        html.Br(),
        html.Div(children=excl_mxw_switch(pageparam)),
        html.Br(),
        dcc.Store(id="input_store_da"),
    ]



right_layout_de = [
    libs_navbar,
    html.Hr(
        style={
            "border": "3px",
            "border-top": "1px solid",
            "margin-top": "5px",
            "margin-bottom": "5px",
        }
    ),
    html.Div(id="search_result_txt_da"),
    # Log/Linear switch
    dbc.Row(
        [
            dbc.Col(html.Label("X:"), width="auto"),
            dbc.Col(
                dcc.RadioItems(
                    id="xaxis_type_da",
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
                    id="yaxis_type_da",
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
    main_fig(pageparam),
    # dcc.Loading(
    #     children=main_fig(pageparam),
    #     type="circle",
    # ),
    dcc.Store(id="entries_store_da"),
    dcc.Store(id="libs_store_da"),
    html.Hr(style={"border": "3px", "border-top": "1px solid"}),
    create_tabs(pageparam),
    html.Hr(style={"border": "3px", "border-top": "1px solid"}),
    footer,
]


def layout(**query_strings):
    return html.Div(
        [
            dcc.Location(id="location_da"),
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
    [
        Output("location_da", "href", allow_duplicate=True),
        Output("location_da", "refresh", allow_duplicate=True),
    ],
    Input("dataset_da", "value"),
    prevent_initial_call=True,
)
def redirect_to_pages_da(dataset):
    if dataset:
        return page_urls[dataset], True

    else:
        raise PreventUpdate


@callback(
    [
        Output("location_da", "href", allow_duplicate=True),
        Output("location_da", "refresh", allow_duplicate=True),
    ],
    Input("observable_da", "value"),
    prevent_initial_call=True,
)
def redirect_to_subpages(type):
    print("redirect_to_subpages")
    if type:
        return lib_page_urls[type], True  # , dict({"type": type})

    else:
        raise PreventUpdate





@callback(
    Output("reaction_da", "options"),
    Input("incident_particle_da", "value"),
)
def update_reaction_list(proj):
    print("update_reaction_list")

    if not proj:
        raise PreventUpdate

    else:
        return generate_reactions(proj)





@callback(
    Output("reac_branch_da", "options"),
    [
        Input("observable_da", "value"),
        Input("reaction_da", "value"),
    ],
)
def update_branch_list(type, reaction):
    print("update_branch_list")
    if type != "DA":
        raise PreventUpdate

    if not reaction:
        raise PreventUpdate

    return [{"label": "Partial", "value": "PAR"}]





@callback(
    Output("input_store_da", "data"),
    [
        Input("observable_da", "value"),
        Input("target_elem_da", "value"),
        Input("target_mass_da", "value"),
        Input("reaction_da", "value"),
        Input("reac_branch_da", "value"),
        Input("exclude_mxw_switch_da", "value"),
    ],
    # prevent_initial_call=True,
)
def input_store_da(type, elem, mass, reaction, branch, excl_junk_switch):
    print("input_store_da", type)
    if type != "DA":
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
        Output("location_da", "search"),
        Output("location_da", "refresh", allow_duplicate=True),
    ],
    Input("input_store_da", "data"),
    prevent_initial_call=True,
)
def update_url_da(input_store):
    print("update_url")

    if input_store:
        type = input_store.get("type").upper()
        elem = input_store.get("target_elem")
        mass = input_store.get("target_mass")
        reaction = input_store.get("reaction")
        branch = input_store.get("branch")
    else:
        raise PreventUpdate

    if type == "DA" and elem and mass and reaction:
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
        Output("search_result_txt_da", "children"),
        Output("index_table_da", "rowData"),
        Output("entries_store_da", "data"),
        Output("libs_store_da", "data"),
    ],
    [
        Input("input_store_da", "data"),
        Input("rest_btn_da", "n_clicks"),
    ],
    # prevent_initial_call=True,
)
def initial_data_da(input_store, r_click):
    print("initial_data_da")
    if input_store:
        if ctx.triggered_id != "rest_btn_da":
            no_update
        return get_indexes(input_store)

    else:
        raise PreventUpdate




@callback(
    [
        Output("main_fig_da", "figure", allow_duplicate=True),
        Output("exfor_table_da", "rowData"),
    ],
    [
        Input("input_store_da", "data"),
        Input("entries_store_da", "data"),
        Input("libs_store_da", "data"),
        # Input("endf_selct_da", "value"),
    ],
    prevent_initial_call=True,
)
def create_fig_da(input_store, legends, libs):
    if input_store:
        reaction = input_store.get("reaction")

    else:
        raise PreventUpdate
    
    df = pd.DataFrame()
    index_df = pd.DataFrame()

    fig = go.Figure(
        layout=go.Layout(
            xaxis={
                "title": "Angle [Degree]",
                "type": "linear",
                "rangeslider": {
                    "bgcolor": "White",
                    "autorange": True,
                    "thickness": 0.15,
                },
            },
            yaxis={
                "title": "Angular distribution [mb/sr]",
                "type": "linear",
                "fixedrange": False,
            },
            margin={"l": 40, "b": 40, "t": 30, "r": 0},
        )
    )

    lib_df = pd.DataFrame()
    if libs:
        print(libs)
        lib_df = lib_da_data_query(libs)

        for l in libs:
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
            "[" + df["entry_id"] + "](../exfor/entry/" + df["entry_id"] + ")"
        )

        i = 0
        for e in list(legends.keys()):
            if e == "total_points":
                continue
            
            fig.add_trace(
                go.Scatter(
                    x=df[df["entry_id"] == e]["angle"],
                    y=df[df["entry_id"] == e]["data"],
                    error_x=dict(type="data", array=df[df["entry_id"] == e]["dangle"]),
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

    return  fig, df.to_dict("records")








@callback(
    Output("main_fig_da", "figure", allow_duplicate=True),
    [
        Input("xaxis_type_da", "value"),
        Input("yaxis_type_da", "value"),
    ],
    State("main_fig_da", "figure"),
    prevent_initial_call=True,
)
def update_axis(xaxis_type, yaxis_type, fig):
    ## Switch the axis type
    fig.get("layout").get("yaxis").update({"type": yaxis_type})
    fig.get("layout").get("xaxis").update({"type": xaxis_type})

    return fig


@callback(
    [
        Output("main_fig_da", "figure", allow_duplicate=True),
        Output("index_table_da", "filter_query"),
    ],
    Input("energy_range_da", "value"),
    State("main_fig_da", "figure"),
    prevent_initial_call=True,
)
def fileter_by_range_lib(energy_range, fig):
    return fileter_by_en_range(energy_range, fig)



@callback(
    [
        Output("main_fig_da", "figure", allow_duplicate=True),
        Output("index_table_da", "filterModel", allow_duplicate=True),
    ],
    Input("year_range_da", "value"),
    State("main_fig_da", "figure"),
    prevent_initial_call=True,
)
def fileter_by_year_range_lib(year_range, fig):
    return filter_by_year_range(year_range, fig)



@callback(
    Output("main_fig_da", "figure", allow_duplicate=True),
    Input("index_table_da", "selectedRows"),
    State("main_fig_da", "figure"),
    prevent_initial_call=True,
)
def highlight_data_xs(selected, fig):
    return highlight_data(selected, fig)



@callback(
    Output("main_fig_da", "figure", allow_duplicate=True),
    Input("index_table_da", "cellValueChanged"),
    State("main_fig_da", "figure"),
    prevent_initial_call=True,
)
def scale_data_xs(selected, fig):
    return scale_data(selected, fig)





@callback(
    [
        Output("main_fig_da", "figure", allow_duplicate=True),
        Output("index_table_da", "rowTransaction"),
    ],
    Input("del_btn_da", "n_clicks"),
    [
        State("main_fig_da", "figure"),
        State("index_table_da", "selectedRows"),
    ],
    prevent_initial_call=True,
)
def del_rows_da(n1, fig, selected):
    if n1:
        if selected is None:
            return no_update, no_update
        return del_rows_fig(selected, fig)


@callback(
    [
        Output("index_table_da", "exportDataAsCsv"),
        Output("index_table_da", "csvExportParams"),
    ],
    [
        Input("btn_csv_index_da", "n_clicks"),
        Input("btn_csv_index_selct_da", "n_clicks"),
        Input("input_store_da", "data"),
    ],
    prevent_initial_call=True,
)
def export_index_xs(n1, n2, input_store):
    # return export_index(n_clicks_all, n_clicks_slctd, input_store)
    if not input_store:
        raise PreventUpdate
    
    if ctx.triggered_id == "btn_csv_index_da":
        return export_index(False, input_store)
    
    elif ctx.triggered_id == "btn_csv_index_selct_da":
        return export_index(True, input_store)
    
    else:
        return no_update, no_update



@callback(
    [
        Output("exfor_table_da", "exportDataAsCsv"),
        Output("exfor_table_da", "csvExportParams"),
    ],
    [
        Input("btn_csv_exfor_da", "n_clicks"),
        Input("btn_csv_exfor_selct_da", "n_clicks"),
        Input("input_store_da", "data"),
    ],
    prevent_initial_call=True,
)
def export_data_xs(n1, n2, input_store):
    # return export_data(n_clicks_all, n_clicks_slctd, input_store)
    if not input_store:
        raise PreventUpdate

    if ctx.triggered_id == "btn_csv_exfor_da":
        return export_data(False, input_store)
    
    elif ctx.triggered_id == "btn_csv_exfor_selct_da":
        return export_data(True, input_store)
    
    else:
        return no_update, no_update







@callback(
    [
        Output("btn_api_da", "href"),
        Output("btn_api_data_da", "href"),
    ],
    Input("location", "search"),
)
def generate_api_links(search_str):
    if search_str:
        return f"/api/reactions/{pageparam}{search_str}", f"/api/reactions/{pageparam}{search_str}&data=True"
    else:
        return no_update, no_update



@callback(
    [
        Output("exfiles_link_da", "children"),
        Output("libfiles_link_da", "children"),
    ],
    Input("input_store_da", "data"),
)
def generate_file_links(input_store):
    if not input_store:
        raise PreventUpdate

    return generate_exfortables_file_path(
        input_store
    ), generate_endftables_file_path(input_store)
