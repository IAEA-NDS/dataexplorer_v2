####################################################################
#
# This file is part of libraries-2021 dataexplorer, https://nds.iaea.org/dataexplorer/.
# Copyright (C) 2022 International Atomic Energy Agency (IAEA)
#
# Contact:    nds.contact-point@iaea.org
#
####################################################################
import pandas as pd
import numpy as np
import dash
from dash import Dash, html, dcc, Input, Output, State, ctx, no_update, callback
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import plotly.express as px

from pages_common import (
    sidehead,
    page_urls,
    URL_PATH,
    exfor_navbar,
    footer,
    input_check,
    input_obs_all,
    input_general,
    input_target,
    generate_exfor_reactions,
    exfor_filter_opt,
)
from submodules.exfor.queries import reaction_query_by_id
from modules.exfor.list import MAPPING, reactions_df, get_facility_type
from modules.exfor.geofig import get_reactions_geo, geo_fig
from modules.exfor.aggrid import aggrid_layout_bib, aggrid_index_result
from submodules.utilities.util import get_number_from_string, x4style_nuclide_expression
from submodules.utilities.reaction import (
    convert_reaction_to_exfor_style,
    convert_partial_reactionstr_to_inl,
)


dash.register_page(__name__, path="/exfor/geo", redirect_from=["/geo", "/geo/"])
pageparam = "geo"
geo_df = get_reactions_geo(reactions_df)


def input_ge(**query_strings):
    return [
        html.Br(),
        html.Label("Geological Search Option"),
        html.Div(children=input_obs_all(pageparam)),
        html.Div(children=input_target(pageparam, **query_strings)),
        html.Div(children=input_general(pageparam, **query_strings)),
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
        html.Div(children=exfor_filter_opt(pageparam)),
        dcc.Store(id="input_store_geo"),
        html.Br(),
        html.Br(),
        html.Label("Other Search Options"),
        dcc.Link(html.Label("Entry search"), href=URL_PATH + "exfor/search"),
        # dcc.Link(
        #     html.Label("Search from all reaction index"), href= URL_PATH + "exfor/index"
        # ),
    ]


geo_right_layout = [
    exfor_navbar,
    html.Hr(style={"border": "3px", "border-top": "1px solid"}),
    html.Label("Nuclear Reaction Experimental Facilities (Based on EXFOR FACILITY)"),
    dbc.Row(
        [
            dbc.Col(html.Label("Color by "), width="auto"),
            dbc.Col(
                dcc.RadioItems(
                    id="grouping",
                    options=["Country", "Facility Type"],
                    value="Country",
                    labelStyle={"display": "inline-block"},
                ),
                width="auto",
            ),
        ]
    ),
    dcc.Loading(
        children=dbc.Row(dcc.Graph(id="geo_map", figure=geo_fig("Country", geo_df))),
        type="circle",
    ),
    dcc.Store(id="entries_store_geo"),
    html.Hr(style={"border": "3px", "border-top": "1px solid"}),
    html.Label(id="result_bib", children=f"Click the bubble chart to show EXFOR entries from selected facility."),
    dbc.Row(aggrid_layout_bib),
    html.Br(),
    html.Label("Reactions in selected entries"),
    dbc.Row(aggrid_index_result(pageparam)),
    html.Hr(style={"border": "3px", "border-top": "1px solid"}),
    footer,
]


## EXFOR page layout
def layout():
    return html.Div(
        [
            dcc.Location(id="location_geo"),
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
                                        value="EXFOR Viewer",
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
        Output("location_geo", "href", allow_duplicate=True),
        Output("location_geo", "refresh", allow_duplicate=True),
    ],
    Input("dataset", "value"),
    prevent_initial_call=True,
)
def redirect_to_pages_geo(dataset):
    if dataset:
        return page_urls[dataset], True

    else:
        raise PreventUpdate


@callback(
    Output("reaction_geo", "options"),
    Input("incident_particle_geo", "value"),
)
def update_reaction_list(proj):
    print("update_branch_list")

    if not proj:
        raise PreventUpdate

    else:
        return generate_exfor_reactions(proj)


@callback(
    [
        # Output("geo_map", "figure", allow_duplicate=True),
        Output("input_store_geo", "data"),
        Output("entries_store_geo", "data"),
    ],
    [
        Input("reaction_category_geo", "value"),
        Input("incident_particle_geo", "value"),
        Input("reaction_geo", "value"),
        Input("target_elem_geo", "value"),
        Input("target_mass_geo", "value"),
        Input("facility_type", "value"),
        Input("energy_range_geo", "value"),
        Input("year_range_geo", "value"),
    ],
    prevent_initial_call=True,
)
def input_store_geo(
    type, inc_pt, reactions, elem, mass, facility_types, energy_range, year_range
):
    # print("input_store_geo")
    df = geo_df
    
    reactions_exfor_format = []
    level_num = None
    # df = df[ df["projectile"] == "D"]

    if facility_types:
        df = df[df["main_facility_type"].isin([r.upper() for r in facility_types])]

    if type:
        sf6s = []
        for sf6, desc in MAPPING["SF6"].items():
            if any(t == desc["top_category"] for t in type):
                sf6s += [sf6]

        df = df[df["sf6"].isin(sf6s)]


    if elem:
        df = df[
            (df["target"].str.contains(f"-{elem.upper()}-"))
        ]


    if elem and mass:
        elem, mass, reaction = input_check(type if type else "SIG", elem, mass, reactions[0] if reactions else "N,G")
        df = df[
            (df["target"] == x4style_nuclide_expression(elem, mass))
        ]


    if inc_pt:
        df = df[
            df["projectile"] == inc_pt.upper()
            if inc_pt.upper() != "H"
            else df["projectile"] == "HE3"
        ]

    if reactions:
        rr = []
        for r in reactions:
            ## bacause here only EXFOR data is treated
            r = convert_reaction_to_exfor_style(r)

            if r.split(",")[1][-1].isdigit():
                ## such as n,n1, n,n2 but not n,2n
                level_num += int(get_number_from_string(r.split(",")[1]))

                if isinstance(level_num, int):
                    rr += [convert_partial_reactionstr_to_inl(r)]

            else:
                rr += [r.upper()]
                level_num = None

        reactions_exfor_format = list(dict.fromkeys(rr))

        df = df[df["process"].isin([r.upper() for r in reactions_exfor_format])]


    if energy_range:
        df = df[
            (df["e_inc_min"] > energy_range[0]) & (df["e_inc_max"] < energy_range[1])
        ]

    if year_range:
        df = df[(df["year"] > year_range[0]) & (df["year"] < year_range[1])]


    input_dict = {
        "type": type,
        "inc_pt": inc_pt,
        "reaction": reactions_exfor_format,
        "target_elem": elem,
        "target_mass": mass,
        "level_num": level_num if level_num else None,
        "energy_range": energy_range,
        "year_range": year_range,
    }

    return input_dict, df.to_dict("records")




@callback(
    Output("geo_map", "figure", allow_duplicate=True),
    [
        Input("grouping", "value"),
        Input("entries_store_geo", "data"),
    ],
    # State("entries_store_geo", "data"),
    prevent_initial_call=True,
)
def change_grouping(grouping, entries_store):
    if grouping:

        if entries_store:
            df = pd.DataFrame(entries_store)

        else:
            df = geo_df

        return geo_fig(grouping, df)

    raise PreventUpdate





@callback(
    [
        Output("result_bib", "children"),
        Output("bib_index", "rowData"),
    ],
    [
        Input("entries_store_geo", "data"),
        Input("geo_map", "clickData"),
        # State("grouping", "value"),
    ],
)
def select_geo_node(entries_store, selected_data):
    if not entries_store and not selected_data:
        # raise PreventUpdate
        return f"Click the bubble chart to show EXFOR entries from selected facility:", no_update

    if selected_data:
        if entries_store:
            df = pd.DataFrame(entries_store)

        else:
            df = geo_df

        ## e.g. {'points': [{'curveNumber': 67, 'pointNumber': 291, 'pointIndex': 291, 'lon': -84.3101161, 'lat': 35.9311679, 'marker.size': 211, 'bbox': {'x0': 499.53913841741746, 'x1': 518.7052499914713, 'y0': 362.7159697002503, 'y1': 381.88208127430414}, 'customdata': ['Oak Ridge National Laboratory, Oak Ridge, TN', '1USAORL', 'SPECC', 'Crystal spectrometer']}]}
        facility_name, facility_code, facility_type, facility_type_desc = selected_data[
            "points"
        ][0]["customdata"]

        bib_df = df[
            (df["main_facility_institute"] == facility_code)
            & (df["main_facility_type"] == facility_type)
        ]

        bib_df = bib_df[
            [
                "entry",
                "main_facility_type_desc",
                "authors",
                "title",
                "main_reference",
                "main_doi",
                "year",
            ]
        ].drop_duplicates()
        bib_df["entry_id_link"] = (
            "[" + bib_df["entry"] + "](../exfor/entry/" + bib_df["entry"] + ")"
        )
        bib_df["main_reference_link"] = np.where(
            bib_df["main_doi"],
            "["
            + bib_df["main_reference"]
            + "](https://doi.org/"
            + bib_df["main_doi"]
            + ")",
            bib_df["main_reference"],
        )
        return (
            f"EXFOR entries from {facility_type_desc} ({facility_type}) in {facility_name} ({facility_code})",
            bib_df.to_dict("records"),
        )

    else:
        return f"Click the bubble chart to show EXFOR entries from selected facility:", no_update



@callback(
    Output("index_all_geo", "rowData"),
    Input("bib_index", "selectedRows"),
)
def selected_index(selected_rows):
    ## e.g. [{'entry': '33146', 'authors': 'I.Pasha, B.Rudraswamy, S.V.Suryanarayana, H.Naik, S.P.Ram, L.S.Danu, T.Patel, S.Bishnoi, M.P.Karantha', 'title': 'Measurement of neutron induced reaction cross sections of palladium isotopes at the neutron energy of 14.54 +/- 0.24 MeV with covariance analysis', 'main_reference': '(J,JRN,325,175,2020)', 'year': 2020}]

    if selected_rows:
        # print(selected_rows)
        entries = [s["entry"] for s in selected_rows]
        df = reaction_query_by_id(entries)

        df["entry_id_link"] = (
            "[" + df["entry_id"] + "](../exfor/entry/" + df["entry_id"] + ")"
        )

        return df.to_dict("records")

    else:
        # raise PreventUpdate
        return None
