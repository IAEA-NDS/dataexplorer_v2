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
import json
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import dash_daq as daq
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate
import re

from common import (
    PARTICLE,
    sidehead,
    footer,
    libs_navbar,
    url_basename,
    page_urls,
    lib_selections,
    lib_page_urls,
    input_check,
    energy_range_conversion,
    generate_reactions,
    remove_query_parameter,
    limit_number_of_datapoints,
)

# from config import BASE_URL
from libraries.datahandle.list import reaction_list, mt50_list, LIB_LIST_MAX
from libraries.datahandle.tabs import create_tabs
from libraries.datahandle.figs import default_chart, default_axis
from libraries.datahandle.queries import (
    lib_query,
    lib_xs_data_query,
)
from libraries.datahandle.library_cs import read_libs, create_libdf
from exfor.datahandle.queries import (
    reaction_query,
    get_entry_bib,
    data_query,
)


## Registration of page
dash.register_page(__name__, path="/reactions/xs", redirect_from=["/xs"])


## Input layout
def input_lib(**query_strings):
    # if query_strings["type"] == "SIG":
    return [
        dcc.Dropdown(
            id="reaction_category",
            # options=[{"label": j, "value": i} for i, j in sorted(WEB_CATEGORY.items())],
            options=lib_selections,
            placeholder="Select reaction",
            persistence=True,
            persistence_type="memory",
            value="XS",
            style={"font-size": "small", "width": "100%"},
        ),
        html.Label("Target"),
        dcc.Input(
            id="target_elem",
            placeholder="Target element: C, c, Pd, pd, PD",
            persistence=True,
            persistence_type="memory",
            value=query_strings["target_elem"]
            if query_strings.get("target_elem")
            else "Al",
            style={"font-size": "small", "width": "100%"},
        ),
        dcc.Input(
            id="target_mass",
            placeholder="Target mass: 0:natural, m:metastable",
            persistence=True,
            persistence_type="memory",
            value=query_strings["target_mass"]
            if query_strings.get("target_mass")
            else "27",
            style={"font-size": "small", "width": "100%"},
        ),
        html.Label("Reaction"),
        dcc.Dropdown(
            id="reaction",
            options=generate_reactions(),
            placeholder="Reaction e.g. (n,g)",
            persistence=True,
            persistence_type="memory",
            value=query_strings["reaction"] if query_strings.get("reaction") else "n,p",
            style={"font-size": "small", "width": "100%"},
        ),
        dcc.Dropdown(
            id="reac_branch",
            options=[],
            placeholder="Options",
            persistence=True,
            persistence_type="memory",
            value=query_strings["branch"] if query_strings.get("branch") else None,
            style={"font-size": "small", "width": "100%"},
        ),
        html.Br(),
        html.Br(),
        html.P("EXFOR Data Options", style={"font-size": "small"}),
        html.Label("Filter by Energy Range", style={"font-size": "small"}),
        dcc.RangeSlider(
            id="energy_range",
            min=0,
            max=9,
            marks={0: "eV", 3: "keV", 6: "MeV", 9: "GeV"},
            value=[0, 9],
            vertical=False,
        ),
        html.Br(),
        html.Label("Year Range", style={"font-size": "small"}),
        dcc.RangeSlider(
            id="year_range",
            min=1930,
            max=2023,
            step=1,
            marks={
                i: f"Label {i}" if i == 1 else str(i) for i in range(1930, 2025, 40)
            },
            value=[1930, 2023],
            tooltip={"placement": "bottom", "always_visible": True},
            vertical=False,
        ),
        html.Br(),
        dbc.Row([
            dbc.Col(
                daq.ToggleSwitch(
                id='reduce_data_switch',
                size=25,
                value=True)
            , width=3),
            dbc.Col(html.Div("Reduced data points", style={"font-size": "smaller", "color": "gray"}))
        ]
        ),
        html.Br(),
        html.Br(),
        html.P("Evaluated Data Options", style={"font-size": "small"}),
        html.Label("Evaluated Data", style={"font-size": "small"}),
        dcc.Dropdown(
            id="endf_selct",
            options=LIB_LIST_MAX,
            placeholder="Evaluated files",
            persistence=True,
            persistence_type="memory",
            multi=True,
            value=["endfb8.0", "tendl.2021", "jendl5.0", "jeff3.3"],
            style={"font-size": "small", "width": "100%"},
        ),
        html.Label("Groupwise data"),
        dcc.Dropdown(
            id="endf_gropewise",
            options=[{"label": "PENDF", "value": "PENDF"}, {"label": "1109", "value": "1109","disabled": True},  {"label": "640", "value": "640", "disabled": True}],
            persistence=True,
            persistence_type="memory",
            value="PENDF",
            style={"font-size": "small", "width": "100%"},
            clearable=False,
        ),
        dcc.Store(id="input_store"),
    ]


## main figure
main_fig = dcc.Graph(
    id="main_fig_xs",
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


## Layout of right panel
right_layout_lib = [
    libs_navbar,
    html.Hr(style={"border": "3px", "border-top": "1px solid", "margin-top": "5px", "margin-bottom": "5px"}),
    html.Div(id="search_result_txt"),
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
    main_fig,
    # dcc.Loading(
    #     children=main_fig,
    #     type="circle",
    # ),
    dcc.Store(id="entries_store"),
    dcc.Store(id="libs_store"),
    html.Hr(style={"border": "3px", "border-top": "1px solid"}),
    create_tabs("xs"),
    html.Hr(style={"border": "3px", "border-top": "1px solid"}),
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
        Output("location", "href", allow_duplicate=True),
        Output("location", "refresh", allow_duplicate=True),
    ],
    Input("dataset", "value"),
    prevent_initial_call=True,
)
def redirect_to_pages(dataset):
    # print("redirect_to_pages")
    if dataset:
        return page_urls[dataset], True

    else:
        raise PreventUpdate



@callback(
    [
        Output("location", "href", allow_duplicate=True),
        Output("location", "refresh", allow_duplicate=True)
    ],
    Input("reaction_category", "value"),
    prevent_initial_call=True,
)
def redirect_to_subpages(type):
    print("redirect_to_subpages")
    if type:
        return lib_page_urls[type], True #, dict({"type": type})

    else:
        raise PreventUpdate



@callback(
    [
        Output("reac_branch", "options"),
        Output("reac_branch", "value"),
    ],
    [
        Input("reaction_category", "value"),
        Input("reaction", "value"),
    ]
)
def update_branch_list(type, reaction):
    print("update_branch_list")
    if type != "XS":
        raise PreventUpdate
    
    if not reaction:
        raise PreventUpdate

    if reaction.split(",")[1].upper() == "INL":
        return [{"label": "L" + str(n), "value": n} for n in range(0, 40)], None

    else:
        return [{"label": "Partial", "value": "PAR"}], None



@callback(
    Output("input_store", "data"),
    [
        Input("reaction_category", "value"),
        Input("target_elem", "value"),
        Input("target_mass", "value"),
        Input("reaction", "value"),
        Input("reac_branch", "value"),
    ],
    # prevent_initial_call=True,
)
def input_store(type, elem, mass, reaction, branch):
    print("input_store", type)
    if type != "XS":
        return dict({"type": type})

    input_check(type, elem, mass, reaction)
    # print("#### ", type, elem, mass, reaction, branch)
    if not branch:
        if (reaction.split(",")[0].upper() != "N" and reaction.split(",")[1].upper() == "N"):
            #     ## in case if it is not neutron induced reaction then
            #     ## INL (MT=4) is for the production of one neutron which
            #     ## is the sum of the MT=50-90
                ## such as g,n
            mt = "004"

        else:
            mt = reaction_list[reaction.split(",")[1].upper()]["mt"].zfill(3)

    elif branch == "PAR":
        mt = None

    else:
        mt = mt50_list[f"N{branch}"]["mt"].zfill(3)

    return dict(
        {
            "type": type,
            "elem": elem,
            "mass": mass,
            "reaction": reaction,
            "branch": branch,
            "mt": mt,
        }
    )



@callback(
    [
        Output("location", "search", allow_duplicate=True),
        Output("location", "refresh", allow_duplicate=True),
    ],
        Input("input_store", "data"),
    prevent_initial_call=True,
)
def update_url(input_store):
    print("update_url")

    if input_store:
        type, elem, mass, reaction, branch, mt = input_store.values()
    else:
        raise PreventUpdate
    
    if type == "XS" and elem and mass and reaction:
        # print("SIG in url generation:", type, elem, mass, reaction, branch)
        search = ""
        if elem:
            search += "?&target_elem=" + elem

        if mass:
            search += "&target_mass=" + mass

        if reaction:
            search += "&reaction=" + reaction.replace("+", "%2B")

            if reaction.split(",")[1].upper() == "INL":
                if not branch:
                    pass

                elif isinstance(branch, int):
                    search += "&branch=" + str(branch)

            elif reaction.split(",")[1].upper() != "INL":
                if branch == "PAR":
                    search += "&branch=" + str(branch)

                else:
                    search = remove_query_parameter(search, "branch")

        return search, False
    
    else:
        return None, False



@callback(
    [
        Output("search_result_txt", "children"),
        Output("index_table_xs", "rowData"),
        Output("entries_store", "data"),
        Output("libs_store", "data"),
    ],
    Input("input_store", "data"),
    prevent_initial_call=True,
)
def initial_data_xs(input_store):
    print("initial_data_xs")
    if input_store:
        type, elem, mass, reaction, branch, mt = input_store.values()

        if type != "XS":
            raise PreventUpdate

    else:
        raise PreventUpdate

    index_df = pd.DataFrame()
    legends = {} 
    libs = {}

    entries = reaction_query("SIG", elem, mass, reaction, branch)
    libs = lib_query(type, elem, mass, reaction, mt)
    # libs = read_libs(elem+mass.zfill(3), reaction, mt, "G1102")

    total_points = sum( [ e["points"] for e in entries.values() ] ) if entries else 0
    search_result = html.Div(
                    [html.B(f"Search results for {type} {elem}-{mass}({reaction}), MT={mt}: "
                           ),\
                    f"Number of EXFOR data: {len(entries)} datasets wtih {total_points if entries else 0} data points. Number of Evaluated Data Libraries: {len(libs) if libs else 0}."
                    ])

    if not entries and not libs:
        return search_result, None, None, None
    
    if entries:
        legends =  get_entry_bib(e[:5] for e in entries.keys())
        legends = {
            t: dict(**i, **v)
            for k, i in legends.items()
            for t, v in entries.items()
            if k == t[:5]
        }
        
        index_df = pd.DataFrame.from_dict(legends, orient="index").reset_index()
        index_df.rename(columns={"index": "entry_id"}, inplace=True)
        index_df["entry_id_link"] = (
            "[" + index_df["entry_id"] + "](../exfor/entry/" + index_df["entry_id"] + ")"
        )
        legends["total_points"] = total_points
    

    return (
        search_result,
        index_df.to_dict("records"),
        legends,
        libs,
    )




@callback(
    [
        Output("main_fig_xs", "figure", allow_duplicate=True),
        Output("exfor_table_xs", "rowData"),
    ],
    [
        Input("input_store", "data"),
        Input("entries_store", "data"),
        Input("libs_store", "data"),
        Input("endf_selct", "value"),
        Input("reduce_data_switch", "value")
    ],
    prevent_initial_call=True,
)
def create_fig(input_store, legends, libs, endf_selct, switcher):
    # print("create_fig")
    if input_store:
        type, elem, mass, reaction, branch, mt = input_store.values()

    else:
        raise PreventUpdate

    xaxis_type, yaxis_type = default_axis(str(mt).zfill(3))
    fig = default_chart(xaxis_type, yaxis_type, reaction, str(mt).zfill(3))

    lib_df = pd.DataFrame()
    if libs:
        if endf_selct:
            libs_select = [ k for k, l in libs.items() if l in endf_selct ]
            # libs_select = [ k for k, l in libs.items() if k in endf_selct ]
        else:
            libs_select = libs.keys()

        lib_df = lib_xs_data_query(libs_select)
        # lib_df = create_libdf( {k: i for k, i in libs.items() if k in libs_select} )

        for l in libs_select:
            # line_color = color_libs(l)
            # new_col = next(line_color)
            # new_col = color_libs(l)

            lib_df2 = lib_df[lib_df["reaction_id"] == int(l)]
            # lib_df2 = lib_df[lib_df["lib"] == l]
            fig.add_trace(
                go.Scatter(
                    x=lib_df2["en_inc"].astype(float),
                    y=lib_df2["data"].astype(float),
                    showlegend=True,
                    # line_color=new_col,
                    name=str(libs[l]),
                    # name=l,
                    mode="lines",
                )
            )


    df = pd.DataFrame()
    if legends:

        df = data_query(legends.keys(), branch)
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

            if switcher:
                df2 = limit_number_of_datapoints(
                    legends[e]["points"], df[df["entry_id"] == e]
                )

            else:
                df2 = df[df["entry_id"] == e]


            if legends["total_points"] > 500 and not switcher:
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
                # break


    # print(df)
    return fig, df.to_dict("records")




@callback(
    Output("main_fig_xs", "figure", allow_duplicate=True),
    [
        Input("xaxis_type", "value"),
        Input("yaxis_type", "value"),
    ],
    State("main_fig_xs", "figure"),
    prevent_initial_call=True,
)
def update_axis(xaxis_type, yaxis_type, fig):
    # if xaxis_type and yaxis_type and fig:
    fig.get("layout").get("yaxis").update({"type": yaxis_type})
    fig.get("layout").get("xaxis").update({"type": xaxis_type})

    return fig



# https://dash.plotly.com/clientside-callbacks
@callback(
    [
        Output("main_fig_xs", "figure", allow_duplicate=True),
        Output("index_table_xs", "filterModel", allow_duplicate=True),
    ],
    Input("energy_range", "value"),
    State("main_fig_xs", "figure"),
    prevent_initial_call=True,
)
def fileter_by_en_range_lib(energy_range, fig):
    # print(json.dumps(fig, indent=1))
    filter_model = {}
    if energy_range and fig:
        for record in fig.get("data"):
            record.update({"visible": "true"})
            if len(record.get("name").split(",")) > 1:
                if energy_range:
                    ## get the average energy of the dataset
                    sum_x = sum([float(x) for x in record["x"] if x is not None])
                    lower, upper = energy_range_conversion(energy_range)

                    if not lower < sum_x / len(record["x"]) < upper:
                        record.update({"visible": "legendonly"})

                    elif lower < sum_x / len(record["x"]) < upper:
                        record.update({"visible": "true"})

                    filter_model = {
                        "e_inc_min": {
                            "filterType": "number",
                            "type": "greaterThan",
                            "filter": lower,
                        },
                        "e_inc_max": {
                            "filterType": "number",
                            "type": "lessThan",
                            "filter": upper,
                        },
                    }

    return fig, filter_model




@callback(
    [
        Output("main_fig_xs", "figure", allow_duplicate=True),
        Output("index_table_xs", "filterModel", allow_duplicate=True),
    ],
    Input("year_range", "value"),
    State("main_fig_xs", "figure"),
    prevent_initial_call=True,
)
def fileter_by_year_range_lib(year_range, fig):
    
    if not fig or not year_range:
        raise PreventUpdate
    
    if year_range and fig:

        filter_model = {}

        for record in fig.get("data"):
            record.update({"visible": "true"})

            if len(record.get("name").split(",")) > 1:
                legend = re.split(',|\[', record.get("name"))
                # print(record)

                if year_range:
                    if not year_range[0] < int(legend[1].strip()) < year_range[1]:
                        record.update({"visible": "legendonly"})

                    if year_range[0] < int(legend[1].strip()) < year_range[1]:
                        record.update({"visible": "true"})

                    filter_model = {
                        "year": {
                            "filterType": "number",
                            "type": "greaterThan",
                            "filter": year_range[0],
                        },
                        "year": {
                            "filterType": "number",
                            "type": "lessThan",
                            "filter": year_range[1],
                        },
                    }

    return fig, filter_model



@callback(
    Output("main_fig_xs", "figure", allow_duplicate=True),
    [
        Input("index_table_xs", "selectedRows"),
        Input("exfor_table_xs", "rowData"),
    ],
    State("main_fig_xs", "figure"),
    prevent_initial_call=True,
)
def highlight_data(selected, exfor_data, fig):
    # print("highlight_data")
    
    if not fig or not selected:
        raise PreventUpdate
    
    if selected:
        for record in fig.get("data"):
            record.update({ "marker":{"size": 8} })

            if len(record.get("name").split(",")) > 1:
                legend = re.split(',|\[|\]', record.get("name"))

            else:

                continue

            for s in selected:
                if legend[2].strip() == s['entry_id']:
                    record.update({ "marker":{"size": 15} })

                else:
                    continue
    return fig



@callback(
    [
        Output("exfor_table_xs", "exportDataAsCsv"),
        Output("exfor_table_xs", "csvExportParams"),
    ],
    [
        Input("csv-button_xs", "n_clicks"),
        Input("input_store", "data"),
    ],
    prevent_initial_call=True,
)
def export_data_as_csv(n_clicks, input_store):
    if n_clicks and input_store:
        type, elem, mass, _, _, mt = input_store.values()
        filename = f"{elem}{mass}-MT{mt}-exfortables-{type}.csv"
        return True, {"columnKeys": ["author", "year", "entry_id", "en_inc", "den_inc", "data", "ddata"], "fileName": filename}

    return False, None
