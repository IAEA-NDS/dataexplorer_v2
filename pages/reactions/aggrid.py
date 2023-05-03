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
import dash_ag_grid as dag
import re
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from collections import OrderedDict
from dash.exceptions import PreventUpdate

from common import sidehead, footer, libs_navbar, page_urls, lib_selections, lib_page_urls, input_check, energy_range_conversion
from libraries2023.datahandle.list import (
    PARTICLE,
    read_mt_json,
    elemtoz_nz,
    read_mass_range,
)

from config import BASE_URL
from libraries2023.datahandle.tabs import create_tabs
from libraries2023.datahandle.figs import default_chart, default_axis
from sql.queries import reaction_query, get_entry_bib, data_query, lib_query, lib_xs_data_query

## Registration of page
dash.register_page(__name__, path="/reactions/agtest", image='iaea.png')


## Initialize common data
reaction_list = read_mt_json()
mass_range = read_mass_range()


## Input layout
def input_ag(**query_strings):
    return [
        dcc.Dropdown(
            id="reaction_category_ag",
            # options=[{"label": j, "value": i} for i, j in sorted(WEB_CATEGORY.items())],
            options=lib_selections,
            placeholder="Select reaction",
            persistence=True,
            persistence_type="memory",
            value="AGTEST",
            style={"font-size": "small", "width": "100%"},
        ),
        dcc.Input(
            id="target_elem_ag",
            placeholder="Target element: C, c, Pd, pd, PD",
            persistence=True,
            persistence_type="memory",
            value=query_strings["target_elem"]
                if query_strings.get("target_elem")
                else "Ag",
            style={"font-size": "small", "width": "100%"},
        ),
        dcc.Input(
            id="target_mass_ag",
            placeholder="Target mass: 0:natural, m:metastable",
            persistence=True,
            persistence_type="memory",
            value=query_strings["target_mass"]
                if query_strings.get("target_mass")
                else "109",
            style={"font-size": "small", "width": "100%"},
        ),
        dcc.Dropdown(
            id="reaction_ag",
            options=[
                {"label": f"{proj.lower()},{reac.lower()}", "value": f"{proj.lower()},{reac.lower()}"}
                for proj in PARTICLE for reac in reaction_list.keys() 
            ],
            placeholder="Reaction e.g. (n,g)",
            persistence=True,
            persistence_type="memory",
            value=query_strings["reaction"] if query_strings.get("reaction") else "n,p",
            style={"font-size": "small", "width": "100%"},
        ),
    ]

## main figure
main_fig = dcc.Graph(
    id="main_fig_ag",
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

def return_html(entid):
    return f"<a href=http://127.0.0.1:8050/dataexplorer/exfor/entry/{entid}>{entid}</a>"

columnDefs = [
    {
        "headerName": "entry_id",
        "field": "entry_id",
        "filter": "agTextColumnFilter",
        "checkboxSelection": True,
        "headerCheckboxSelection": True,
        # "cellRenderer": {"function": "return_html(params.value)" },
    },
    {
        "headerName": "author",
        "field": "author",
        "type": "rightAligned",
        "filter": "agTextColumnFilter",
        "editable": True,
    },
    {
        "headerName": "year",
        "field": "year",
        "type": "rightAligned",
        "filter": "agTextColumnFilter",
        "editable": True,
    },
    {
        "headerName": "x4_code",
        "field": "x4_code",
        "type": "rightAligned",
        "filter": "agTextColumnFilter",
        "editable": True,
    },
]


defaultColDef = {
    "flex": 1,
    # set the default column width
    "width": 50,
    # make every column editable
    "editable": False,
    # make every column use 'text' filter by default
    # enable floating filters by default
    "floatingFilter": True,
    # make columns resizable
    "resizable": True,
    'sortable': True,    
}


grid = dag.AgGrid(
    id="grid-test",
    # className="ag-theme-alpine-dark",
    columnDefs=columnDefs,
    rowData=[],
    columnSize="sizeToFit",
    defaultColDef=defaultColDef,
    rowMultiSelectWithClick=True,
    dashGridOptions={"undoRedoCellEditing": True, 
                     "rowSelection": "multiple",
                     },
    # selectedRows={}
    
)


## Layout of right panel
right_layout_ag = [
    libs_navbar,
    html.Hr(style={"border": "3px", "border-top": "1px solid"}),
    html.Div(id="result_cont_ag"),
    # Log/Linear switch
    dbc.Row(
        [
            dbc.Col(html.Label("X:"), width="auto"),
            dbc.Col(
                dcc.RadioItems(
                    id="xaxis_type_ag",
                    options=[{"label": i, "value": i.lower()} for i in ["Linear", "Log"]],
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
                    id="yaxis_type_ag",
                    options=[{"label": i, "value": i.lower()} for i in ["Linear", "Log"]],
                    value="log",
                    persistence=True,
                    persistence_type="memory",
                    labelStyle={"display": "inline-block"},
                ),
                width="auto",
            ),
        ]
    ),
    dcc.Loading(
        children=main_fig,
        type="circle",
    ),
    html.Hr(style={"border": "3px", "border-top": "1px solid"}),
    html.Div(id="selections-checkbox-output"),
    grid,
    dcc.Store(id="exp-data_store"),
    html.Hr(style={"border": "3px", "border-top": "1px solid"}),
    footer,
]


## Main layout of libraries-2023 page
# layout = html.Div(
def layout(**query_strings):
    return html.Div(
        [
            dcc.Location(id="location_ag"),
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
                                    html.Div(input_ag(**query_strings)),
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
                                children=right_layout_ag,
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
    Output("location_ag", "href", allow_duplicate=True),
    Input("dataset", "value"),
    prevent_initial_call=True,
)
def redirect_to_pages_ag(dataset):
    return page_urls[dataset]



@callback(
    Output("location_ag", "href", allow_duplicate=True),
    Input("reaction_category", "value"),
    prevent_initial_call=True,
)
def redirect_to_subpages_ag(type):
    return lib_page_urls[type]




@callback(
    Output("location_ag", "href", allow_duplicate=True), 
    Input("grid-test", "cellClicked"),
    prevent_initial_call=True,
)
def display_cell_clicked_on(cell):
    if cell is None:
        return "Click on a cell"
    if cell['colId'] == "entry_id":
        return "http://127.0.0.1:8050/dataexplorer/exfor/entry/" + cell['value']




@callback(
    Output("location_ag", "href", allow_duplicate=True),
    [
        Input("reaction_category_ag", "value"),
        Input("target_elem_ag", "value"),
        Input("target_mass_ag", "value"),
        Input("reaction_ag", "value"),
    ],
    prevent_initial_call=True,
)
def update_url_ag(type, elem, mass, reaction):
    input_check(type, elem, mass, reaction)

    if type=="SIG" and (elem and mass and reaction):

        url = BASE_URL + "/reactions/xs"

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
        Output("result_cont_ag", "children"),
        Output("main_fig_ag", "figure"),
        Output("grid-test", "rowData"),
    ],
    [
        Input("reaction_category_ag", "value"),
        Input("target_elem_ag", "value"),
        Input("target_mass_ag", "value"),
        Input("reaction_ag", "value"),
    ],
    # prevent_initial_call=True,
)
def update_fig_ag(type, elem, mass, reaction):
    print(type, elem, mass, reaction)
    input_check(type, elem, mass, reaction)

    df = pd.DataFrame()
    index_df = pd.DataFrame()

    mt = reaction_list[reaction.split(",")[1].upper()]["mt"].zfill(3)
    xaxis_type, yaxis_type = default_axis(mt)
    fig =  default_chart(xaxis_type, yaxis_type, reaction, mt)


    entids, entries = reaction_query(type, elem, mass, reaction, branch=None)
    libs = lib_query(type, elem, mass, reaction, mt)
    search_result = f"Search results for {type} {elem}-{mass}({reaction}): {len(entids)}"


    if not entids and not libs:
        return search_result, fig, df.to_dict("records")

    if libs:
        df_ag = lib_xs_data_query(libs.keys())

        for l in libs.keys():
            # line_color = color_ags(l)
            # new_col = next(line_color)
            # new_col = color_ags(l)
            fig.add_trace(
                go.Scatter(
                    x=df_ag[df_ag["reaction_id"] == l]["en_inc"].astype(float),
                    y=df_ag[df_ag["reaction_id"] == l]["data"].astype(float),
                    showlegend=True,
                    # line_color=new_col,
                    name=str(libs[l]),
                    mode="lines",
                )
            )

    if entries:
        legend = get_entry_bib(entries)
        legend = {
            t: dict(**i, **v)
            for k, i in legend.items()
            for t, v in entids.items()
            if k == t[:5]
        }
        df = data_query(entids.keys())

        i = 0
        for e in legend.keys():
            fig.add_trace(
                go.Scatter(
                    x=df[df["entry_id"] == e]["en_inc"],
                    y=df[df["entry_id"] == e]["data"],
                    error_x=dict(type="data", array=df[df["entry_id"] == e]["den_inc"]),
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
        # index_df["entry_id"] = (
        #     "["
        #     + index_df["entry_id"]
        #     + "](http://127.0.0.1:8050/dataexplorer/exfor/entry/"
        #     + index_df["entry_id"]
        #     + ")"
        # )

    return (
        search_result,
        fig,
        index_df.to_dict("records"),
    )


@callback(
    Output("selections-checkbox-output", "children"),
    Input("grid-test", "selectedRows"),
)
def selected(selected):
    if selected:
        selected_athlete = [s["author"] for s in selected]
        return f"You selected athletes: {selected_athlete}"
    return "No selections"


