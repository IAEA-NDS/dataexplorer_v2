####################################################################
#
# This file is part of libraries-2021 dataexplorer, https://nds.iaea.org/dataexplorer/.
# Copyright (C) 2022 International Atomic Energy Agency (IAEA)
#
# Contact:    nds.contact-point@iaea.org
#
####################################################################

import pandas as pd
import datetime

import dash
from dash import html, dcc, callback, Input, dash_table, Output
from dash.dash_table.Format import Format, Scheme
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

from libraries2023.datahandle.list import (
    PARTICLE,
    elemtoz_nz,
)
from common import sidehead, page_urls, exfor_navbar, footer, input_check, energy_range_conversion
from config import session, engines, BASE_URL
from exfor.exfor_stat import stat_right_layout
from sql.models import Exfor_Reactions, Exfor_Bib
from sql.queries import reaction_query_simple
from exfor.datahandle.list import reaction_list, get_institutes, MAPPING

## Registory of the page
dash.register_page(__name__, path="/exfor/search")

today = datetime.date.today()
year = today.year


def input_ex(**query_strings):
    return [
        html.Label("Reaction search"),
        dcc.Dropdown(
            id="reaction_category_ex",
            options=[{"label": j, "value": i} for i, j in sorted(MAPPING["top_category"].items())],
            placeholder="Reaction Category",
            persistence=True,
            persistence_type="memory",
            value=query_strings["type"] if query_strings.get("type") else None,
            style={"font-size": "small", "width": "100%"},
        ),
        dcc.Input(
            id="target_elem_ex",
            placeholder="Target element: C, c, Pd, pd, PD",
            persistence=True,
            persistence_type="memory",
            value=query_strings["target_elem"]
            if query_strings.get("target_elem")
            else None,
            style={"font-size": "small", "width": "100%"},
        ),
        dcc.Input(
            id="target_mass_ex",
            placeholder="Target mass: 0:natural, m:metastable",
            persistence=True,
            persistence_type="memory",
            value=query_strings["target_mass"]
            if query_strings.get("target_mass")
            else None,
            style={"font-size": "small", "width": "100%"},
            type="text",
        ),
        dcc.Dropdown(
            id="reaction_ex",
            options=[
                {"label": f"{proj.lower()},{reac.lower()}", "value": f"{proj.lower()},{reac.lower()}"}
                for proj in PARTICLE for reac in reaction_list.keys() 
            ]+[{"label": "Other", "value": "other"}],
            placeholder="Reaction e.g. (n,g)",
            persistence=True,
            persistence_type="memory",
            value=query_strings["reaction"] if query_strings.get("reaction") else None,
            style={"font-size": "small", "width": "100%"},
        ),
        dcc.Dropdown(
            id="reac_branch_ex",
            placeholder="Options",
            persistence=True,
            persistence_type="memory",
            style={"font-size": "small", "width": "100%"},
        ),
        html.Label("More search options"),
        dbc.Accordion([
            dbc.AccordionItem([
                dcc.Input(
                    id="sf4",
                    placeholder="exfor sf4",
                    persistence=True,
                    persistence_type="memory",
                    style={"font-size": "small", "width": "100%"},
                ),
                dcc.Dropdown(
                    placeholder="Measureed at",
                    options=[{"label": inst + ":" + desc["description"], "value": inst} for inst, desc in get_institutes().items() ],
                    persistence=True,
                    persistence_type="memory",
                    style={"font-size": "small", "width": "100%"},
                    multi=True,
                ),
                dcc.Input(
                    id="sf5",
                    placeholder="exfor sf5",
                    persistence=True,
                    persistence_type="memory",
                    style={"font-size": "small", "width": "100%"},
                ),  
                dcc.Input(
                    id="sf7",
                    placeholder="exfor sf7",
                    persistence=True,
                    persistence_type="memory",
                    style={"font-size": "small", "width": "100%"},
                ),  
                dcc.Input(
                    id="sf8",
                    placeholder="exfor sf8",
                    persistence=True,
                    persistence_type="memory",
                    style={"font-size": "small", "width": "100%"},
                ),  
            ], title="More options"),
        ],start_collapsed=True),
        html.Br(),
        html.Label("Energy Range"),
        dcc.RangeSlider(
            id="energy_range_ex",
            min=0,
            max=9,
            marks={0: "eV", 3: "keV", 6: "MeV", 9: "GeV"},
            value=[0, 9],
            vertical=False,
        ),
        html.Br(),
        html.Label("Year Range"),
        dcc.RangeSlider(
            id="year_range_ex",
            min=1930,
            max=2023,
            marks={
                i: f"Label {i}" if i == 1 else str(i) for i in range(1930, 2025, 40)
            },
            value=[1930, year],
            tooltip={"placement": "bottom", "always_visible": True},
            vertical=False,
        ),
        html.Br(),
        dcc.Link(html.Label("Entry search"), href=BASE_URL + "/exfor"),
    ]


serch_result_layout = [
    exfor_navbar,
    html.Hr(style={"border": "3px", "border-top": "1px solid"}),
    dbc.Row([
        dbc.Col(html.Div(id="search_result_count"), width="auto"),
        dbc.Col(dcc.Link(html.Label("Plot in Dataexplorer"), id="dataeplorer_link", href="")),     
        ]),
    # Main content
    html.Div(
        [
            dash_table.DataTable(
                id="search_result_table",
                columns=[
                    {"name": "Author", "id": "first_author"},
                    {"name": "Year", "id": "year"},
                    {"name": "#Entry", "id": "entry_id", "presentation": "markdown"},
                    {
                        "name": "E_min[eV]",
                        "id": "e_inc_min",
                        "type": "numeric",
                        "format": Format(precision=3, scheme=Scheme.exponent),
                    },
                    {
                        "name": "E_max[eV]",
                        "id": "e_inc_max",
                        "type": "numeric",
                        "format": Format(precision=3, scheme=Scheme.exponent),
                    },
                    {"name": "Points", "id": "points"},
                    {"name": "Reaction Code", "id": "x4_code"},
                    {"name": "Facility", "id": "main_facility_type"},
                ],
                filter_action="native",
                sort_action="native",
                sort_mode="single",
                markdown_options={"html": True},
                page_action="native",
                page_current=0,
                page_size=10,
                row_selectable="multi",
                row_deletable=True,
                selected_columns=[],
                selected_rows=[],
            ),
            html.Br(),
            html.Label("By data points:"),
            html.Div(id="datatable-interactivity-container"),
        ],
        style={"margin": "20px"},
    ),
    html.Hr(style={"border": "3px", "border-top": "1px solid"}),
    footer,
    dcc.Store(id="stored-data"),
]


## EXFOR page layout
def layout(**query_strings):

    if not query_strings:
        right_layout = stat_right_layout
    else:
        right_layout = serch_result_layout

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
                                    html.Div(input_ex(**query_strings)),
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
                                id="right_layout",
                                children=right_layout,
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




###------------------------------------------------------------------------------------
### App Callback
###------------------------------------------------------------------------------------
@callback(
    Output("location_sch", "href", allow_duplicate=True),
    Input("dataset", "value"),
    prevent_initial_call=True,
)
def redirect_to_pages(dataset):
    return page_urls[dataset]



@callback(
    Output("location_sch", "href", allow_duplicate=True),
    [
        Input("reaction_category_ex", "value"),
        Input("target_elem_ex", "value"),
        Input("target_mass_ex", "value"),
        Input("reaction_ex", "value"),
    ],
    prevent_initial_call=True,
)
def update_url_ex(type, elem, mass, reaction):
    print(type, elem, mass, reaction)
    input_check(type, elem, mass, reaction)

    url = BASE_URL + "/exfor/search?"
    if type:
        url += "&type=" + type
    if elem:
        url += "&target_elem=" + elem
    if mass:
        url += "&target_mass=" + mass
    if reaction:
        url += "&reaction=" + reaction


    return url




@callback(
    [
        Output("reac_branch_ex", "options"),
        Output("reac_branch_ex", "value"),
    ],
    Input("reaction_ex", "value"),
)
def update_branch_list(reaction):
    # if not reaction:
    #     return [""]
    if reaction:
        if reaction.split(",")[1] == "inl":
            return [{"label": "L"+str(n), "value": n} for n in range(0,40)], 1
    else:
        return [{"label": "Partial", "value": "PAR"}], ""





@callback(
        Output("dataeplorer_link", "href"),
    [
        Input("reaction_category_ex", "value"),
        Input("target_elem_ex", "value"),
        Input("target_mass_ex", "value"),
        Input("reaction_ex", "value"),
    ],
)
def update_url_ex(type, elem, mass, reaction):

    input_check(type, elem, mass, reaction)
    if type == "SIG":
        type = "xs"
        
    plot_link = BASE_URL + f"/reactions/{type.lower()}?target_elem={elem}&target_mass={mass}&reaction={reaction}"
    
    return plot_link




@callback(
    [
        Output("search_result_count", "children"), 
        Output("stored-data", "data")],
    [
        Input("reaction_category_ex", "value"),
        Input("target_elem_ex", "value"),
        Input("target_mass_ex", "value"),
        Input("reaction_ex", "value"),
        Input("reac_branch_ex", "value"),
    ],
)
def search_exfor_record_by_reaction(type, elem, mass, reaction, branch):
    print(type, elem, mass, reaction)
    input_check(type, elem, mass, reaction)

    df = reaction_query_simple(type, elem, mass, reaction, branch)
    df["entry_id"] = (
        "[" + df["entry_id"] + "](" + BASE_URL + "/exfor/entry/" + df["entry_id"] + ")"
    )

    search_result = f"Search results for {type} {elem}-{mass}({reaction}): {len(df.index)}"

    return search_result, df.to_dict("records")



@callback(
    Output("search_result_table", "data"),
    Input("stored-data", "data"),
)
def search_exfor_record_by_reaction(df_dict):
    return df_dict



@callback(
    Output("datatable-interactivity-container", "children"),
    [
        Input("stored-data", "data"),
        Input("search_result_table", "derived_virtual_data"),
        Input("search_result_table", "derived_virtual_selected_rows"),
    ],
)
def update_graphs(df_dict, rows, derived_virtual_selected_rows):
    df = pd.DataFrame.from_dict(df_dict)
    dff = df if rows is None else pd.DataFrame(rows)
    if derived_virtual_selected_rows is None:
        derived_virtual_selected_rows = []

    return [
        dcc.Graph(
            id=column,
            figure={
                "data": [
                    {
                        "x": dff[column],
                        "y": dff["points"],
                        "type": "bar",
                    }
                ],
                "layout": {
                    "xaxis": {"automargin": True, "title": {"text": column}},
                    "yaxis": {"automargin": True, "title": {"text": "data points"}},
                    "height": 250,
                    "margin": {"t": 10, "l": 10, "r": 10},
                },
            },
        )
        for column in [
            "year",
            "e_inc_min",
            "main_facility_type",
            "main_facility_institute",
            "first_author_institute",
        ]
        if column in dff
    ]


