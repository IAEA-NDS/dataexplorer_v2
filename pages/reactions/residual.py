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
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate

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
)
from submodules.utilities.elem import elemtoz_nz
from submodules.utilities.mass import mass_range


from libraries.datahandle.list import reaction_list, mt50_list, LIB_LIST_MAX
from libraries.datahandle.tabs import create_tabs
from libraries.datahandle.figs import default_chart
from libraries.datahandle.queries import lib_query, lib_residual_data_query
from exfor.datahandle.queries import (
    reaction_query,
    get_entry_bib,
    data_query,
)


## Registration of page
dash.register_page(__name__, path="/reactions/residual")


## Input layout
def input_lib(**query_strings):
    return [
        dcc.Dropdown(
            id="reaction_category_rp",
            # options=[{"label": j, "value": i} for i, j in sorted(WEB_CATEGORY.items())],
            options=lib_selections,
            placeholder="Select reaction",
            persistence=True,
            persistence_type="memory",
            value="Residual",
            style={"font-size": "small", "width": "100%"},
        ),
        dcc.Input(
            id="target_elem_rp",
            placeholder="Target element: C, c, Pd, pd, PD",
            persistence=True,
            persistence_type="memory",
            value=query_strings["target_elem"]
            if query_strings.get("target_elem")
            else "Mo",
            style={"font-size": "small", "width": "100%"},
        ),
        dcc.Input(
            id="target_mass_rp",
            placeholder="Target mass: 0:natural, m:metastable",
            persistence=True,
            persistence_type="memory",
            value=query_strings["target_mass"]
            if query_strings.get("target_mass")
            else "100",
            style={"font-size": "small", "width": "100%"},
        ),
        dcc.Dropdown(
            id="reaction_rp",
            options=[{"label": f"{pt.lower()},x", "value": pt} for pt in PARTICLE],
            placeholder="Reaction e.g. (p,x)",
            persistence=True,
            persistence_type="memory",
            value=query_strings["inc_pt"].upper()
            if query_strings.get("inc_pt")
            else "P",
            style={"font-size": "small", "width": "100%"},
        ),
        html.P("Residual product"),
        dcc.Input(
            id="rp_elem",
            placeholder="e.g. F, f, Mo, mo, MO",
            # multi=False,
            persistence=True,
            persistence_type="memory",
            value=query_strings["rp_elem"] if query_strings.get("rp_elem") else "Tc",
            style={"font-size": "small", "width": "100%"},
        ),
        dcc.Input(
            id="rp_mass",
            placeholder="e.g. 56, 99g (ground), 99m(metastable)",
            # multi=False,
            persistence=True,
            persistence_type="memory",
            value=query_strings["rp_mass"] if query_strings.get("rp_mass") else "99m",
            style={"font-size": "small", "width": "100%"},
        ),
        html.Br(),
        html.Br(),
        html.P("Fileter EXFOR records by"),
        html.Label("Energy Range"),
        dcc.RangeSlider(
            id="energy_range_rp",
            min=0,
            max=9,
            marks={0: "eV", 3: "keV", 6: "MeV", 9: "GeV"},
            value=[0, 9],
            vertical=False,
        ),
        html.Br(),
        html.Label("Year Range"),
        dcc.RangeSlider(
            id="year_range_rp",
            min=1930,
            max=2023,
            marks={
                i: f"Label {i}" if i == 1 else str(i) for i in range(1930, 2025, 40)
            },
            value=[1930, 2023],
            tooltip={"placement": "bottom", "always_visible": True},
            vertical=False,
        ),
        html.Br(),
        html.Br(),
        html.P("Evaluated Data Options", style={"font-size": "small"}),
        html.Label("Evaluated Data", style={"font-size": "small"}),
        dcc.Dropdown(
            id="endf_selct_rp",
            options=LIB_LIST_MAX,
            placeholder="Evaluated files",
            persistence=True,
            persistence_type="memory",
            multi=True,
            value=["endfb8.0", "tendl.2021"],
            style={"font-size": "small", "width": "100%"},
        ),
        html.Label("Groupwise data"),
        dcc.Dropdown(
            id="endf_gropewise_rp",
            options=[{"label": "PENDF", "value": "PENDF"}, {"label": "1109", "value": "1109","disabled": True},  {"label": "640", "value": "640", "disabled": True}],
            persistence=True,
            persistence_type="memory",
            value="PENDF",
            style={"font-size": "small", "width": "100%"},
            clearable=False,
        ),
        dcc.Store(id="input_store_rp"),
    ]


## main figure
main_fig = dcc.Graph(
    id="main_fig_rp",
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
    html.Hr(style={"border": "3px", "border-top": "1px solid"}),
    html.Div(id="search_result_txt_rp"),
    # Log/Linear switch
    dbc.Row(
        [
            dbc.Col(html.Label("X:"), width="auto"),
            dbc.Col(
                dcc.RadioItems(
                    id="xaxis_type_rp",
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
                    id="yaxis_type_rp",
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
    main_fig,
    dcc.Store(id="entries_store_rp"),
    dcc.Store(id="libs_store_rp"),
    html.Hr(style={"border": "3px", "border-top": "1px solid"}),
    create_tabs("rp"),
    html.Hr(style={"border": "3px", "border-top": "1px solid"}),
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
    Input("reaction_category_rp", "value"),
    prevent_initial_call=True,
)
def redirect_to_subpages_rp(type):
    if type:
        return lib_page_urls[type], True

    else:
        raise PreventUpdate






@callback(
    Output("input_store_rp", "data"),
    [
        Input("reaction_category_rp", "value"),
        Input("target_elem_rp", "value"),
        Input("target_mass_rp", "value"),
        Input("reaction_rp", "value"),
        Input("rp_elem", "value"),
        Input("rp_mass", "value"),
    ],
    # prevent_initial_call=True,
)
def input_store_rp(type, elem, mass, inc_pt, rp_elem, rp_mass):
    input_check(type, elem, mass, inc_pt)
    input_check(type, rp_elem, rp_mass, inc_pt)

    return dict(
        {
            "type": type,
            "elem": elem,
            "mass": mass,
            "inc_pt": inc_pt,
            "rp_elem": rp_elem,
            "rp_mass": rp_mass,
        }
    )



@callback(
    [
        Output("location_rp", "search", allow_duplicate=True),
        Output("location_rp", "refresh", allow_duplicate=True),
    ],
    Input("input_store_rp", "data"),
    prevent_initial_call=True,
)
def update_url_rp(input_store):
    print("update_url_rp")
    if input_store:
        type, elem, mass, inc_pt, rp_elem, rp_mass = input_store.values() 

    else:
        raise PreventUpdate

    if type == "Residual" and elem and mass and inc_pt and rp_elem and rp_mass:
        search = ""
        if elem:
            search += "?&target_elem=" + elem

        if mass:
            search += "&target_mass=" + mass

        if inc_pt:
            search += "&inc_pt=" + inc_pt

        if rp_elem:
            search += "&rp_elem=" + rp_elem

        if rp_mass:
            search += "&rp_mass=" + rp_mass

        return search, False

    else:
        return None, False
        # raise PreventUpdate





@callback(
    [
        Output("search_result_txt_rp", "children"),
        Output("index_table_rp", "rowData"),
        Output("entries_store_rp", "data"),
        Output("libs_store_rp", "data"),
    ],
    Input("input_store_rp", "data"),
    prevent_initial_call=True,
)
def initial_data_rp(input_store):
    print("initial_data_rp", input_store)
    if input_store:
        type, elem, mass, inc_pt, rp_elem, rp_mass = input_store.values() 

        if type != "Residual":
            raise PreventUpdate

    else:
        raise PreventUpdate
    
    index_df = pd.DataFrame()
    legends = {}
    libs = {}

    entries = reaction_query(
        type, elem, mass, reaction=inc_pt, branch=None, rp_elem=rp_elem, rp_mass=rp_mass
    )
    libs = lib_query(
        type,
        elem,
        mass,
        reaction=f"{inc_pt.upper()},X",
        mt=None,
        rp_elem=rp_elem,
        rp_mass=rp_mass,
    )

    total_points = sum( [ e["points"] for e in entries.values() ] ) if entries else 0
    search_result = html.Div(
                    [html.B(f"Search results for {type} {elem}-{mass}({inc_pt.lower()},x)-->{rp_elem}-{rp_mass}: "
                           ),\
                    f"Number of EXFOR data: {len(entries)} datasets wtih {total_points if entries else 0} data points. Number of Evaluated Data Libraries: {len(libs) if libs else 0}."
                    ])

    if not entries and not libs:
        return search_result, None, None, None
    
    if entries:
        legends = get_entry_bib(e[:5] for e in entries.keys())
        legends = {
            t: dict(**i, **v)
            for k, i in legends.items()
            for t, v in entries.items()
            if k == t[:5]
        }

        index_df = pd.DataFrame.from_dict(legends, orient="index").reset_index()
        index_df.rename(columns={"index": "entry_id"}, inplace=True)
        index_df["entry_id_link"] = (
            "["
            + index_df["entry_id"]
            + "](../exfor/entry/"
            + index_df["entry_id"]
            + ")"
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
        Output("main_fig_rp", "figure", allow_duplicate=True),
        Output("exfor_table_rp", "rowData"),
    ],
    [
        Input("input_store_rp", "data"),
        Input("entries_store_rp", "data"),
        Input("libs_store_rp", "data"),
        Input("endf_selct_rp", "value"),
    ],
    prevent_initial_call=True,
)
def create_fig_rp(input_store, legends, libs, endf_selct):
    print("create_fig_rp", input_store)
    if input_store:
        type, elem, mass, inc_pt, rp_elem, rp_mass = input_store.values() 

    else:
        raise PreventUpdate

    xaxis_type, yaxis_type = ["linear", "linear'"]
    fig = default_chart(
        xaxis_type="linear", yaxis_type="linear", reaction=inc_pt, mt=None
    )

    lib_df = pd.DataFrame()
    if libs:
        lib_df = lib_residual_data_query(inc_pt, libs.keys())
        print(lib_df)
        for l in libs.keys():
            # line_color = color_libs(l)
            # new_col = next(line_color)
            # new_col = color_libs(l)
            # lib_df2 = lib_df[lib_df["reaction_id"] == l]
            fig.add_trace(
                go.Scattergl(
                    x=lib_df[lib_df["reaction_id"] == l]["en_inc"].astype(float),
                    y=lib_df[lib_df["reaction_id"] == l]["data"].astype(float),
                    showlegend=True,
                    # line_color=new_col,
                    name=str(libs[l]),
                    mode="lines",
                )
            )

    df = pd.DataFrame()
    if legends:
        df = data_query(legends.keys(), None)
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
                go.Scattergl(
                    x=df[df["entry_id"] == e]["en_inc"],
                    y=df[df["entry_id"] == e]["data"],
                    error_x=dict(type="data", array=df[df["entry_id"] == e]["den_inc"]),
                    error_y=dict(type="data", array=df[df["entry_id"] == e]["ddata"]),
                    showlegend=True,
                    name=f"{legends[e]['author']}, {legends[e]['year']}"
                    if legends[e].get("year")
                    else legends[e]["author"],
                    marker=dict(size=8, symbol=i),
                    mode="markers",
                )
            )
            i += 1

            if i == 30:
                i = 1

    return fig, df.to_dict("records")




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
    ],
    Input("energy_range", "value"),
    State("main_fig_rp", "figure"),
    prevent_initial_call=True,
)
def fileter_by_en_range_rp(energy_range, fig):
    # print(json.dumps(fig, indent=1))

    if energy_range and fig:
        for record in fig.get("data"):
            record.update({"visible": "true"})
            if len(record.get("name").split(",")) > 1:
                if energy_range:
                    ## get the average energy of the dataset
                    sum_x = sum([float(x) for x in record["x"] if x is not None])
                    lower, upper = energy_range_conversion(energy_range)
                    print(lower, upper)

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
        Output("main_fig_rp", "figure", allow_duplicate=True),
        Output("index_table_rp", "filterModel", allow_duplicate=True),
    ],
    Input("year_range", "value"),
    State("main_fig_rp", "figure"),
    prevent_initial_call=True,
)
def fileter_by_year_range_rp(year_range, fig):
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
    Output("main_fig_rp", "figure", allow_duplicate=True),
    [
        Input("index_table_rp", "selectedRows"),
        Input("exfor_table_rp", "rowData"),
    ],
    State("main_fig_rp", "figure"),
    prevent_initial_call=True,
)
def highlight_data_rp(selected, exfor_data, fig):
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
        Output("exfor_table_rp", "exportDataAsCsv"),
        Output("exfor_table_rp", "csvExportParams"),
    ],
    [
        Input("csv-button_rp", "n_clicks"),
        Input("input_store_rp", "data"),
    ],
    prevent_initial_call=True,
)
def export_data_as_csv(n_clicks, input_store):
    if n_clicks and input_store:
        type, elem, mass, _, _, mt = input_store.values()
        filename = f"{elem}{mass}-MT{mt}-exfortables-{type}.csv"
        return True, {"columnKeys": ["author", "year", "entry_id", "en_inc", "den_inc", "data", "ddata"], "fileName": filename}

    return False, None
