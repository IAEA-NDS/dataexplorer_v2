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
from dash import html, dcc, callback, Input, dash_table, Output, State
from dash.dash_table.Format import Format, Scheme
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

## from dataexplorer modules
from common import (
    PARTICLE,
    PARTICLE_FY,
    sidehead,
    url_basename,
    page_urls,
    exfor_navbar,
    footer,
    input_check,
    energy_range_conversion,
)

from exfor.exfor_stat import stat_right_layout
from exfor.datahandle.queries import reaction_query_simple, join_index_bib
from exfor.datahandle.list import get_institutes, MAPPING
from libraries.datahandle.list import reaction_list

## Registory of the page
dash.register_page(__name__, path="/exfor/search")

today = datetime.date.today()
year = today.year


def input_ex(**query_strings):
    return [
        html.Label("Reaction search"),
        dcc.Dropdown(
            id="reaction_category_ex",
            options=[
                {"label": j, "value": i}
                for i, j in sorted(MAPPING["top_category"].items())
            ],
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
                {
                    "label": f"{proj.lower()},{reac.lower()}",
                    "value": f"{proj.lower()},{reac.lower()}",
                }
                for proj in PARTICLE
                for reac in reaction_list.keys()
            ]
            + [{"label": "Other", "value": "other"}],
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
        dbc.Accordion(
            [
                dbc.AccordionItem(
                    [
                        dcc.Input(
                            id="authors",
                            placeholder="one of the authors",
                            persistence=True,
                            persistence_type="memory",
                            style={"font-size": "small", "width": "100%"},
                        ),
                        dcc.Input(
                            id="sf4",
                            placeholder="exfor sf4",
                            persistence=True,
                            persistence_type="memory",
                            style={"font-size": "small", "width": "100%"},
                        ),
                        dcc.Dropdown(
                            id="facility",
                            placeholder="Measureed at",
                            options=[
                                {
                                    "label": inst + ":" + desc["description"],
                                    "value": inst,
                                }
                                for inst, desc in get_institutes().items()
                            ],
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
                        html.Button('Apply', id='apply_btn', n_clicks=0),
                    ],
                    title="More options",
                ),
            ],
            start_collapsed=True,
        ),
        dcc.Store(id="input_store_ex"),
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

        html.Label("Entry search"),
        dcc.Input(
            id="entid_ex",
            type="text",
            placeholder="Entry number",
            persistence=True,
            persistence_type="memory",
            # size="md",
            style={"font-size": "small", "width": "95%", "margin-left": "6px"},
        ),

        html.Br(),
        # dcc.Link(html.Label("Entry search"), href=url_basename + "exfor"),
        dcc.Link(html.Label("Geo search"), href=url_basename + "exfor/geo"),
    ]


search_result_layout = [
    exfor_navbar,
    html.Hr(style={"border": "3px", "border-top": "1px solid"}),
    dbc.Row(
        [
            dbc.Col(html.Div(id="search_result_count"), width="auto"),
            dbc.Col(dcc.Link(id="dataeplorer_link", href="")),
        ]
    ),
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
                    {"name": "level", "id": "level_num"},
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
                                children=search_result_layout if query_strings else stat_right_layout,
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
    if dataset:
        return page_urls[dataset]

    else:
        raise PreventUpdate


@callback(
    Output("location_sch", "href", allow_duplicate=True),
    Input("entid_ex", "value"),
    prevent_initial_call=True,
)
def redirect_to_entry(entry_id):
    url = url_basename + "exfor/entry/"
    if not entry_id:
        raise PreventUpdate
    elif len(entry_id) != 5 and len(entry_id) != 11:
        raise PreventUpdate
    else:
        url += entry_id
    return url



@callback(
    [
        Output("reaction_ex", "options"),
        Output("reac_branch_ex", "options"),
        Output("reac_branch_ex", "value"),
    ],
    [
        Input("reaction_category_ex", "value"),
        Input("reaction_ex", "value"),
    ]
)
def update_branch_list_ex(type, reaction):
    print("update_branch_list")
    if not reaction or not type:
        raise PreventUpdate

    if type == "FY":
        reactions = [f"{pt.lower()},f" for pt in PARTICLE_FY]
        
        return reactions, [{"label": "Independent", "value": "IND"}, {"label": "Cumulative", "value": "CUM"}, {"label": "Primary", "value": "PRE"}], None

    else:
        reactions = [
                {
                    "label": f"{proj.lower()},{reac.lower()}",
                    "value": f"{proj.lower()},{reac.lower()}",
                }
                for proj in PARTICLE
                for reac in reaction_list.keys()
            ] + [{"label": "Other", "value": "other"}]

        if reaction.split(",")[1].upper() == "INL":
            return reactions, [{"label": "L" + str(n), "value": n} for n in range(0, 40)], None

        else:
            return reactions, [{"label": "Partial", "value": "PAR"}], None


        
@callback(
    Output("input_store_ex", "data"),
    [
        Input("reaction_category_ex", "value"),
        Input("target_elem_ex", "value"),
        Input("target_mass_ex", "value"),
        Input("reaction_ex", "value"),
        Input("reac_branch_ex", "value"),
        State("authors", "value"),
        State("sf4", "value"),
        State("facility", "value"),
        State("sf5", "value"),
        State("sf7", "value"),
        State("sf8", "value"),
        Input("apply_btn","n_clicks"),
    ],
    prevent_initial_call=True,
)
def input_store_ex(type, elem, mass, reaction, branch, authors, sf4, facility, sf5, sf7, sf8, apply_btn):
    input_check(type, elem, mass, reaction)
    print("#### search for ", type, elem, mass, reaction, branch)

    if apply_btn:
        return {
                "type": type,
                "elem": elem,
                "mass": mass,
                "reaction": reaction,
                "branch": branch,
                "authors": authors,
                "sf4": sf4,
                "sf5": sf5,
                "sf7": sf7,
                "sf8": sf8,
                "facility": facility,
            }
    else:
        return {
                "type": type,
                "elem": elem,
                "mass": mass,
                "reaction": reaction,
                "branch": branch,
                "authors": None,
                "sf4": None,
                "sf5": None,
                "sf7": None,
                "sf8": None,
                "facility": None,
            }




@callback(
    [
        Output("location_sch", "href", allow_duplicate=True),
        Output("location_sch", "refresh", allow_duplicate=True),
    ],
    Input("input_store_ex", "data"),
    prevent_initial_call=True,
)
def update_url_ex(input_store):
    if input_store:
            type = input_store.get("type")
            elem = input_store.get("elem")
            mass = input_store.get("mass")
            reaction = input_store.get("reaction")
            branch = input_store.get("branch")
            authors = input_store.get("authors")
            sf4 = input_store.get("sf4")
            sf5 = input_store.get("sf5")
            sf7 = input_store.get("sf7")
            sf8 = input_store.get("sf8")
            facility = input_store.get("facility")

    else:
        raise PreventUpdate
    
    url = url_basename + "exfor/search?"

    if type:
        url += "&type=" + type

    if elem:
        url += "&target_elem=" + elem

    if mass:
        url += "&target_mass=" + mass

    if reaction:
        url += "&reaction=" + reaction
    
    if branch:
        url += "&branch=" + str(branch)

    return url, False





@callback(
    [
        Output("dataeplorer_link", "children"),
        Output("dataeplorer_link", "href"),
    ],
    [
        Input("reaction_category_ex", "value"),
        Input("target_elem_ex", "value"),
        Input("target_mass_ex", "value"),
        Input("reaction_ex", "value"),
    ],
)
def update_url_ex(type, elem, mass, reaction):
    input_check(type, elem, mass, reaction)

    if any(type == t for t in ["DA", "FY", "SIG", "DE", "FIS"]):
        if type == "SIG":
            type = "xs"
        plot_link = f"{url_basename}reactions/{type.lower()}?target_elem={elem}&target_mass={mass}&reaction={reaction}"

        return "Data plot", plot_link
    
    else:
        return "", ""






@callback(
    [
        Output("search_result_count", "children"), 
        Output("search_result_table", "data")],
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
        "[" + df["entry_id"] + "](" + url_basename + "exfor/entry/" + df["entry_id"] + ")"
    )

    search_result = (
        f"Search results for {type} {elem}-{mass}({reaction}): {len(df.index)}"
    )

    return search_result, df.to_dict("records")





@callback(
    Output("datatable-interactivity-container", "children"),
    [
        Input("search_result_table", "data"),
        Input("search_result_table", "derived_virtual_data"),
        Input("search_result_table", "derived_virtual_selected_rows"),
    ],
)
def update_graphs_ex(df_dict, rows, derived_virtual_selected_rows):
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



@callback(
    Output("index-all", "rowData"),
    Input("target_elem_ex", "value"),
)
def aggrid_data_add(target_elem_ex):
    if not target_elem_ex:
        df = join_index_bib()
        return df.to_dict("records")
    
    else:
        return pd.DataFrame()

