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
from collections import OrderedDict
from operator import getitem
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
dash.register_page(__name__, path="/reactions/de")

## Initialize common data
reaction_list = read_mt_json()
mass_range = read_mass_range()


def input_lib(**query_strings):
    return [
        dcc.Dropdown(
            id="reaction_category",
            # options=[{"label": j, "value": i} for i, j in sorted(WEB_CATEGORY.items())],
            options=lib_selections,
            placeholder="Select reaction",
            persistence=True,
            persistence_type="memory",
            value="DE",
            style={"font-size": "small", "width": "100%"},
        ),
        dcc.Input(
            id="target_elem_de",
            placeholder="Target element: C, c, Pd, pd, PD",
            persistence=True,
            persistence_type="memory",
            value=query_strings["target_elem"]
                if query_strings.get("target_elem")
                else "Fe",
            style={"font-size": "small", "width": "100%"},
        ),
        dcc.Input(
            id="target_mass_de",
            placeholder="Target mass: 0:natural, m:metastable",
            persistence=True,
            persistence_type="memory",
            value=query_strings["target_mass"]
                if query_strings.get("target_mass")
                else "56",
            style={"font-size": "small", "width": "100%"},
        ),
        dcc.Dropdown(
            id="reaction_de",
            options=[
                {"label": f"{proj.lower()},{reac.lower()}", "value": f"{proj.lower()},{reac.lower()}"}
                for proj in PARTICLE for reac in reaction_list.keys() 
            ],
            placeholder="Reaction e.g. (n,g)",
            persistence=True,
            persistence_type="memory",
            value=query_strings["reaction"] if query_strings.get("reaction") else "n,x",
            style={"font-size": "small", "width": "100%"},
        ),
        html.Br(),
        html.Br(),
        html.P("Fileter EXFOR records by"),
        html.Label("Energy Range"),
        dcc.RangeSlider(
            id="energy_range_de",
            min=0,
            max=9,
            marks={0: "eV", 3: "keV", 6: "MeV", 9: "GeV"},
            value=[0, 9],
            # tooltip={"placement": "bottom", "always_visible": True},
            vertical=False,
        ),
        html.Br(),
        html.Label("Year Range"),
        dcc.RangeSlider(
            id="year_range_de",
            min=1930,
            max=2023,
            marks={
                i: f"Label {i}" if i == 1 else str(i) for i in range(1930, 2025, 40)
            },
            value=[1930, 2023],
            tooltip={"placement": "bottom", "always_visible": True},
            vertical=False,
        ),
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
                    options=[{"label": i, "value": i.lower()} for i in ["Linear", "Log"]],
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
                    options=[{"label": i, "value": i.lower()} for i in ["Linear", "Log"]],
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
    create_tabs("DE"),
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
    Input("reaction_category", "value"),
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
        Input("reaction_category", "value"),
        Input("target_elem_de", "value"),
        Input("target_mass_de", "value"),
        Input("reaction_de", "value"),
    ],
    prevent_initial_call=True,
)
def update_url_de(type, elem, mass, reaction):
    input_check(type, elem, mass, reaction)

    if type=="DE" and (elem and mass and reaction):

        url = BASE_URL + "/reactions/de"

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
        Output("index_table_de", "data"),
        Output("exfor_table_de", "data"),
    ],
    [
        Input("reaction_category", "value"),
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
                    "title": "Outgoing particle energy [MeV]",
                    "type": "linear",
                    "rangeslider": {
                        "bgcolor": "White",
                        "autorange": True,
                        "thickness": 0.15,
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


    entids, entries = reaction_query(type, elem, mass, reaction, branch=None, rp_elem=None, rp_mass=None)
    search_result = f"Search results for {type} {elem}-{mass}({reaction}): {len(entids)}"


    if not entids:
        return search_result, fig, None, None

    if entries:
        legend = get_entry_bib(entries)
        legend = {
            t: dict(**i, **v)
            for k, i in legend.items()
            for t, v in entids.items()
            if k == t[:5]
        }
        df = data_query(entids.keys(), branch=None)

        i = 0
        for e in legend.keys():
            fig.add_trace(
                go.Scattergl(
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
        index_df["entry_id"] = (
            "["
            + index_df["entry_id"]
            + "](http://127.0.0.1:8050/dataexplorer/exfor/entry/"
            + index_df["entry_id"]
            + ")"
        )
        df['bib'] = df["entry_id"].map(legend)
        df = pd.concat([df,df["bib"].apply(pd.Series)], axis=1)
        df = df.drop(columns=["bib"])
        df["entry_id"] = (
            "["
            + df["entry_id"]
            + "](http://127.0.0.1:8050/dataexplorer/exfor/entry/"
            + df["entry_id"]
            + ")"
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
    fig.get("layout").get("yaxis").update({"type":yaxis_type})
    fig.get("layout").get("xaxis").update({"type":xaxis_type})

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
        if len(records.get("name").split(","))>1:
            author, year = records.get("name").split(",") 

            sum_x = sum([float(x) for x in records["x"] if x is not None])
            lower, upper = energy_range_conversion(energy_range)

            filter = "{year} ge " + str(year_range[0]) + " && {year} le " + str(year_range[1])
            filter +=  " && {e_inc_min} ge " + str(lower) + " && {e_inc_max} le " + str(upper)

            if not lower < sum_x/len(records["x"]) < upper or not year_range[0] < int(year) < year_range[1] :
                records.update({"visible":"legendonly"})

            if lower < sum_x/len(records["x"]) < upper and year_range[0] < int(year) < year_range[1]:
                records.update({"visible":"true"})


    return fig, filter



