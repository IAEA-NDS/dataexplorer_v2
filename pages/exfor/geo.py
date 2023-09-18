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
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import plotly.express as px

from common import (
    sidehead,
    url_basename,
    page_urls,
    exfor_navbar,
    footer,
    lib_selections,
    generate_reactions
)
from exfor.datahandle.queries import index_query_by_bib
from exfor.datahandle.list import MAPPING, get_facility_type
from exfor.geo import reactions_df, geo_fig
from exfor.aggrid import aggrid_layout_bib, aggrid_layout


dash.register_page(__name__, path="/exfor/geo")



def input_ge(**query_strings):
    return dbc.Row(
        [
        html.Label("Geological search"),
        # dcc.Link(html.Label("Reaction search"), href= url_basename + "exfor/geo"),
        html.Br(),
        html.Label("Observables"),
        dcc.Dropdown(
            id="reaction_category_geo",
            # options=[{"label": j, "value": i} for i, j in sorted(WEB_CATEGORY.items())],
            options=[
                {"label": j, "value": i}
                for i, j in sorted(MAPPING["top_category"].items())
            ],
            placeholder="Select reaction",
            persistence=True,
            persistence_type="memory",
            multi=True,
            style={"font-size": "small", "width": "100%"},
        ),
        html.Label("Reaction"),
        dcc.Dropdown(
            id="reaction_geo",
            options=generate_reactions(),
            placeholder="Reaction e.g. (n,g)",
            persistence=True,
            multi=True,
            persistence_type="memory",
            # value=query_strings["reaction"] if query_strings.get("reaction") else "n,p",
            style={"font-size": "small", "width": "100%"},
        ),
        html.Label("Facility type"),
        dcc.Dropdown(
            id="facility_type",
            options=get_facility_type(),
            placeholder="Facility type e.g. Accelerator",
            persistence=True,
            multi=True,
            persistence_type="memory",
            # value=query_strings["reaction"] if query_strings.get("reaction") else "n,p",
            style={"font-size": "small", "width": "100%"},
        ),
        html.Br(),
        html.Br(),
        html.Label("Energy Range", style={"font-size": "small"}),
        dcc.RangeSlider(
            id="energy_range_geo",
            min=0,
            max=9,
            marks={0: "eV", 3: "keV", 6: "MeV", 9: "GeV"},
            value=[0, 9],
            vertical=False,
        ),
        html.Br(),
        html.Label("Year Range", style={"font-size": "small"}),
        dcc.RangeSlider(
            id="year_range_geo",
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
        dcc.Store(id="input_store_geo"),
        ],
    )



geo_right_layout = [
        exfor_navbar,
        # taxonomy
        # html.Hr(style={"border": "3px", "border-top": "1px solid"}),
        # html.Label("EXFOR Taxonomy"),
        # dbc.Row(cyto_layout),
        # geo
        html.Hr(style={"border": "3px", "border-top": "1px solid"}),
        html.Label(
            "Nuclear Reaction Experimental Facilities (Based on EXFOR FACILITY)"
        ),
        dbc.Row([
            dbc.Col(html.Label("Color by "), width="auto"),
            dbc.Col(
                dcc.RadioItems(
                    id="grouping",
                    options=['Country', 'Facility Type'], 
                    value = 'Country', 
                    labelStyle={"display": "inline-block"}
                ),
                width="auto",
            )
        ]),
        dcc.Loading(
            children=dbc.Row(dcc.Graph(id="geo_map")),
            type="circle",
        ),
        html.Hr(style={"border": "3px", "border-top": "1px solid"}),
        html.Label("EXFOR entries from selected facility:", id="result_bib"),
        dbc.Row(aggrid_layout_bib),
        html.Label("Reaction indexes"),
        dbc.Row(aggrid_layout("geo")),
        html.Hr(style={"border": "3px", "border-top": "1px solid"}),
        html.Div(id="test"),
        footer,
]


## EXFOR page layout
def layout():
    return html.Div(
        [
            dcc.Location(id="location_sch"),
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
                                        value="EXFOR",
                                        style={"font-size": "small"},
                                        persistence=True,
                                        persistence_type="memory",
                                    ),
                                    html.Div(input_ge()),
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
                                children=geo_right_layout,
                                style={"margin-right": "20px"},
                            ),
                            html.P("test", id="ppp"),
                        ],
                        width=10,
                    ),
                ]
            ),
        ],
        style={"height": "100vh"},
    )



@callback(
    [
        Output("geo_map", "figure"), 
        Output("input_store_geo", "data"),
    ],
    [
        Input("grouping", "value"),
        Input("facility_type", "value"),
        Input("reaction_category_geo", "value"),
        Input("reaction_geo", "value"),
        Input("energy_range_geo", "value"),
        Input("year_range_geo", "value"),
    ]
    )
def select_geo_node(grouping, facility_type, type, reaction, energy_range, year_range):
    df = reactions_df

    if facility_type:
        df = df[ df["main_facility_type"].isin([r.upper() for r in facility_type]) ]

    if type:
        sf6s = []
        for sf6, desc in MAPPING["SF6"].items():
            if any(t == desc["top_category"] for t in type):
                sf6s += [sf6]

        df = df[ df["sf6"].isin(sf6s) ]

    if reaction:
        df = df[ df["process"].isin([r.upper() for r in reaction]) ]

    if energy_range:
        df = df[ (df["e_inc_min"] > energy_range[0]) & (df["e_inc_max"] < energy_range[1]) ]

    if year_range:
        df = df[ (df["year"] > year_range[0]) & (df["year"] < year_range[1]) ]

    input_dict = {
            "type": type,
            "reaction": reaction,
            "energy_range": energy_range,
            "year_range": year_range,
            }
    
    return geo_fig(grouping, df), input_dict



@callback(
    [
        Output("result_bib", "children"), 
        Output("bib_index", "rowData"), 
    ],
    [
        Input("input_store_geo", "data"),
        Input("geo_map", "clickData")
    ]
    )
def select_geo_node(input_store, selected_data):
    if input_store:
        type, reaction, energy_range, year_range = input_store.values()
    
    if selected_data:
        ## e.g. {'points': [{'curveNumber': 67, 'pointNumber': 291, 'pointIndex': 291, 'lon': -84.3101161, 'lat': 35.9311679, 'marker.size': 211, 'bbox': {'x0': 499.53913841741746, 'x1': 518.7052499914713, 'y0': 362.7159697002503, 'y1': 381.88208127430414}, 'customdata': ['Oak Ridge National Laboratory, Oak Ridge, TN', '1USAORL', 'SPECC', 'Crystal spectrometer']}]}
        facility_name, facility_code, facility_type, facility_type_desc = selected_data[ "points"][0]["customdata"]

        bib_df = reactions_df[ ( reactions_df["main_facility_institute"] == facility_code ) & ( reactions_df["main_facility_type"] == facility_type )]

        if type:
            sf6s = []
            for sf6, desc in MAPPING["SF6"].items():
                if any(t == desc["top_category"] for t in type):
                    sf6s += [sf6]
            bib_df = bib_df[ bib_df["sf6"].isin(sf6s) ]

        if reaction:
            bib_df = bib_df[ bib_df["process"].isin([r.upper() for r in reaction]) ]

        if energy_range:
            bib_df = bib_df[ (bib_df["e_inc_min"] > energy_range[0]) & (bib_df["e_inc_max"] < energy_range[1]) ]

        if year_range:
            bib_df = bib_df[ (bib_df["year"] > year_range[0]) & (bib_df["year"] < year_range[1]) ]

        bib_df = bib_df[["entry", "main_facility_type_desc",  "authors", "title", "main_reference", "year"]].drop_duplicates()
        bib_df["entry_id_link"] = (
            "[" + bib_df["entry"] + "](../exfor/entry/" + bib_df["entry"] + ")"
        )

        return f"EXFOR entries from {facility_type_desc} ({facility_type}) in {facility_name} ({facility_code})", bib_df.to_dict("records")
    
    else:

        return None, None





@callback(
    Output("index-all-geo", "rowData"), 
    Input("bib_index", "selectedRows"),
    )
def selected_index(selected_rows):
    ## e.g. [{'entry': '33146', 'authors': 'I.Pasha, B.Rudraswamy, S.V.Suryanarayana, H.Naik, S.P.Ram, L.S.Danu, T.Patel, S.Bishnoi, M.P.Karantha', 'title': 'Measurement of neutron induced reaction cross sections of palladium isotopes at the neutron energy of 14.54 +/- 0.24 MeV with covariance analysis', 'main_reference': '(J,JRN,325,175,2020)', 'year': 2020}]

    if selected_rows:
        entries = [s['entry'] for s in selected_rows]
        df = index_query_by_bib(entries)
        print(df)
        df["entry_id_link"] = (
            "[" + df["entry_id"] + "](../exfor/entry/" + df["entry_id"] + ")"
        )

        return df.to_dict("records")
    
    else:
        # raise PreventUpdate
        return None




# @callback(
#     [
#         Output("result_bib", "children"), 
#         Output("bib_index", "rowData"), 
#         Output("geo_map", "figure"), 
#     ],
#     [
#         Input("geo_map", "clickData"),
#         Input("reaction_category_geo", "value"),
#     ]
#     )
# def select_geo_node(selected_data, type, reaction, energy_range, year_range):

#     if type:
#         df = reactions_df[ reactions_df["sf6"].isin(type) ]
#         pd.set_option('display.max_rows', None)
#         print(df)
#         return geo_fig(df)
    
#     else:
#         return geo_fig(reactions_df)
