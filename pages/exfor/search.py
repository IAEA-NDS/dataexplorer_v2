####################################################################
#
# This file is part of libraries-2023 dataexplorer, https://nds.iaea.org/dataexplorer/.
# Copyright (C) 2022 International Atomic Energy Agency (IAEA)
#
# Contact:    nds.contact-point@iaea.org
#
####################################################################

import datetime
from urllib.parse import urlencode
import numpy as np

import dash
from dash import Dash, html, dcc, Input, Output, State, ctx, no_update, callback
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

## from dataexplorer modules
from pages_common import (
    URL_PATH,
    sidehead,
    page_urls,
    exfor_navbar,
    footer,
    generate_exfor_reactions,
    remove_query_parameter,
    entry_id_check,
    input_check_elem,
    input_check_mass,
    input_entry,
    input_target,
    input_general,
    exfor_filter_opt,
    energy_range_conversion,
)
from modules.exfor.list import (
    MAPPING,
    get_institutes,
    get_facility_types,
    get_sf5,
    get_sf8,
)
from modules.exfor.aggrid import aggrid_search_result
from submodules.exfor.queries import entries_query


## Registory of the page
dash.register_page(__name__, path="/exfor/search")
pageparam = "sch"

today = datetime.date.today()
year = today.year


def input_sch(**query_strings):
    return [
        html.Br(),
        html.Div(children=input_entry(pageparam, None)),
        html.Br(),
        html.Br(),
        html.Label("Search from reaction index"),
        dcc.Dropdown(
            id="observable_sch",
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
        html.Div(children=input_target(pageparam, **query_strings)),
        html.Div(children=input_general(pageparam, **query_strings)),
        # html.Div(children=input_residual(pageparam, **query_strings)),
        html.Br(),
        html.Label("More search options"),
        dbc.Accordion(
            [
                dbc.AccordionItem(
                    [
                        dcc.Input(
                            id="first_author",
                            placeholder="First author",
                            persistence=True,
                            persistence_type="memory",
                            value=query_strings["first_author"]
                            if query_strings.get("first_author")
                            else None,
                            style={"font-size": "small", "width": "100%"},
                        ),
                        dcc.Input(
                            id="authors",
                            placeholder="One of the authors",
                            persistence=True,
                            persistence_type="memory",
                            value=query_strings["authors"]
                            if query_strings.get("authors")
                            else None,
                            style={"font-size": "small", "width": "100%"},
                        ),
                        dcc.Dropdown(
                            id="facilities",
                            placeholder="Measureed at",
                            options=[
                                {
                                    "label": inst + ": " + desc["description"],
                                    "value": inst,
                                }
                                for inst, desc in get_institutes().items()
                            ],
                            persistence=True,
                            persistence_type="memory",
                            value=[q for q in query_strings["facilities"]]
                            if query_strings.get("facilities")
                            else None,
                            style={"font-size": "small", "width": "100%"},
                            multi=True,
                        ),
                        dcc.Dropdown(
                            id="facility_types",
                            placeholder="Type of facility",
                            options=[
                                {
                                    "label": fact + ": " + desc["description"],
                                    "value": fact,
                                }
                                for fact, desc in get_facility_types().items()
                            ],
                            persistence=True,
                            persistence_type="memory",
                            value=query_strings["facility_types"]
                            if query_strings.get("facility_types")
                            else None,
                            style={"font-size": "small", "width": "100%"},
                            multi=True,
                        ),
                        dcc.Input(
                            id="sf4",
                            placeholder="EXFOR SF4",
                            persistence=True,
                            persistence_type="memory",
                            value=query_strings["sf4"]
                            if query_strings.get("sf4")
                            else None,
                            style={"font-size": "small", "width": "100%"},
                        ),
                        dcc.Dropdown(
                            id="sf5",
                            placeholder="EXFOR SF5",
                            options=[
                                {
                                    "label": fact + ": " + desc["description"],
                                    "value": fact,
                                }
                                for fact, desc in get_sf5().items()
                            ],
                            persistence=True,
                            persistence_type="memory",
                            value=query_strings["sf5"]
                            if query_strings.get("sf5")
                            else None,
                            style={"font-size": "small", "width": "100%"},
                            multi=True,
                        ),
                        dcc.Input(
                            id="sf7",
                            placeholder="EXFOR SF7",
                            persistence=True,
                            persistence_type="memory",
                            value=query_strings["sf7"]
                            if query_strings.get("sf7")
                            else None,
                            style={"font-size": "small", "width": "100%"},
                        ),
                        dcc.Dropdown(
                            id="sf8",
                            placeholder="EXFOR SF8",
                            options=[
                                {
                                    "label": fact + ": " + desc["description"],
                                    "value": fact,
                                }
                                for fact, desc in get_sf8().items()
                            ],
                            persistence=True,
                            persistence_type="memory",
                            value=query_strings["sf8"]
                            if query_strings.get("sf8")
                            else None,
                            style={"font-size": "small", "width": "100%"},
                            multi=True,
                        ),
                    ],
                    title="More options",
                ),
            ],
            start_collapsed=False,
        ),
        dbc.Col(
            [
                dbc.Button(
                    "Search",
                    color="primary",
                    id="apply_btn",
                    className="me-2",
                    n_clicks=0,
                ),
                dbc.Button(
                    "Clear",
                    color="success",
                    id="clear_btn",
                    className="me-1",
                    n_clicks=0,
                ),
            ]
        ),
        html.Br(),
        html.Br(),
        html.Div(children=exfor_filter_opt(pageparam)),
        dcc.Store(id="input_store_sch"),
        html.Br(),
        html.Br(),
        html.Label("Other Search Options"),
        dcc.Link(html.Label("Geo search"), href=URL_PATH + "exfor/geo"),
    ]


search_result_layout = [
    exfor_navbar,
    html.Hr(style={"border": "3px", "border-top": "1px solid"}),
    dbc.Row(
        [
            dbc.Col(html.Div(id="search_result_count"), width="auto"),
            dbc.Col(html.A(id="dataeplorer_link", href="#")),
        ]
    ),
    # Main content
    # html.Div(children=stat_content),
    html.Div(
        [
            ## Aggrid version
            aggrid_search_result(pageparam),
        ],
        style={"margin": "20px"},
    ),
    # html.Hr(style={"border": "3px", "border-top": "1px solid"}),
    footer,
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
                                        value="EXFOR Viewer",
                                        style={"font-size": "small"},
                                        persistence=True,
                                        persistence_type="memory",
                                    ),
                                    html.Div(input_sch(**query_strings)),
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
                                children=search_result_layout,
                                # children=stat_right_layout+search_result_layout
                                # if not query_strings
                                # else search_result_layout,
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
        Output("location_sch", "href", allow_duplicate=True),
        Output("location_sch", "refresh", allow_duplicate=True),
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
    Output("reaction_sch", "options"),
    Input("incident_particle_sch", "value"),
)
def update_reaction_list_sch(proj):
    print("update_branch_list")

    if not proj:
        raise PreventUpdate

    else:
        return generate_exfor_reactions(proj)


@callback(
    [
        Output("location_sch", "href", allow_duplicate=True),
        Output("location_sch", "refresh", allow_duplicate=True),
    ],
    Input("entid_sch", "value"),
    prevent_initial_call=True,
)
def redirect_to_entry_sch(entry_id):
    entry_id = entry_id_check(entry_id)
    return f"{URL_PATH}exfor/entry/{entry_id}", True


@callback(
    Output("input_store_sch", "data"),
    [
        Input("observable_sch", "value"),
        Input("target_elem_sch", "value"),
        Input("target_mass_sch", "value"),
        Input("incident_particle_sch", "value"),
        Input("reaction_sch", "value"),
        Input("first_author", "value"),
        Input("authors", "value"),
        Input("facilities", "value"),
        Input("facility_types", "value"),
        Input("sf4", "value"),
        Input("sf5", "value"),
        Input("sf7", "value"),
        Input("sf8", "value"),
        Input("apply_btn", "n_clicks"),
        Input("clear_btn", "n_clicks"),
    ],
)
def input_store_sch(
    type,
    elem,
    mass,
    inc_pt,
    reaction,
    author,
    authors,
    facilities,
    facility_types,
    sf4,
    sf5,
    sf7,
    sf8,
    apply_btn,
    clear_btn,
):
    if ctx.triggered_id == "clear_btn":
        return {}

    if ctx.triggered_id == "apply_btn":
        print("#### search for ", type, elem, mass)
        reactions_exfor_format = []
        level_nums = []
        types = []

        if type:
            types = [
                t
                for t, cate in MAPPING["SF6"].items()
                if MAPPING["SF6"][t]["top_category"] == type
            ]

        if elem:
            elem = input_check_elem(elem)

        if mass:
            mass = input_check_mass(mass)

        input_ddd = dict(
            {
                "type": type,
                "types": types if types else None,
                "target_elem": elem,
                "target_mass": mass,
                "inc_pt": inc_pt,
                "reaction": reaction,
                "first_author": author,
                "authors": authors,
                "sf4": sf4,
                "sf5": sf5,
                "sf7": sf7,
                "sf8": sf8,
                "facilities": facilities,
                "facility_types": facility_types,
            }
        )
        return input_ddd

    else:
        raise PreventUpdate


@callback(
    [
        Output("location_sch", "search"),
        Output("location_sch", "refresh", allow_duplicate=True),
    ],
    [
        Input("input_store_sch", "data"),
        Input("clear_btn", "n_clicks"),
    ],
    prevent_initial_call=True,
)
def update_url_sch(input_store, clear_btn):
    query_string = "?"
    if input_store:
        for key, item in input_store.items():
            if key == "types":
                continue

            elif isinstance(item, list):
                query_string += f"&{key}=" + f"&{key}=".join(item)

            elif item is not None:
                query_string += f"&{key}={item}"

            elif item is None or not item:
                query_string = remove_query_parameter(query_string, key)

        return query_string, False

    if ctx.triggered_id == "clear_btn":
        query_string = "?"
        return query_string, True

    else:
        raise PreventUpdate


@callback(
    [
        Output("search_result_count", "children"),
        Output("index_search_res_sch", "rowData"),
    ],
    Input("input_store_sch", "data"),
    prevent_initial_call=True,
)
def search_exfor_record_by_reaction(input_store):
    print("search exfor entries")
    if input_store:
        df = entries_query(**input_store)

        ## Create url link to entry and doi
        df["entry_id_link"] = (
            "["
            + df["entry_id"]
            + "]("
            + URL_PATH
            + "exfor/entry/"
            + df["entry_id"]
            + ")"
        )
        df["main_reference_link"] = np.where(
            df["main_doi"],
            "[" + df["main_reference"] + "](https://doi.org/" + df["main_doi"] + ")",
            df["main_reference"],
        )
        ## Number of EXFOR data: 1 datasets wtih 1 data points. Number of Evaluated Data Libraries: 6.
        search_criteria = ""
        for k, i in input_store.items():
            if i is not None and i and k != "types":
                if k == "type":
                    i = MAPPING["top_category"][i]
                search_criteria += f"{k}: {i}, "

        search_result = f"Search results for {search_criteria}. Number of EXFOR subentries: {len(df.index)}."

        return search_result, df.to_dict("records")

    else:
        return "", []


@callback(
    Output("index_search_res_sch", "filterModel", allow_duplicate=True),
    Input("energy_range_sch", "value"),
    prevent_initial_call=True,
)
def fileter_by_en_range_lib(energy_range):
    if energy_range:
        ## get the average energy of the dataset
        lower, upper = energy_range_conversion(energy_range)
        return {
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


@callback(
    Output("index_search_res_sch", "filterModel", allow_duplicate=True),
    Input("year_range_sch", "value"),
    prevent_initial_call=True,
)
def fileter_by_year_range_lib(year_range):
    print(year_range)
    return {
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


@callback(
    [
        Output("dataeplorer_link", "children"),
        Output("dataeplorer_link", "href"),
    ],
    Input("input_store_sch", "data"),
)
def create_plot_link_sch(input_store):
    if input_store:
        type = input_store.get("type")
        elem = input_store.get("target_elem")
        mass = input_store.get("target_mass")
        inc_pt = input_store.get("inc_pt")
        reaction = input_store.get("reaction")

        if any(type == t for t in ["FY", "SIG"]):
            if reaction:
                reaction = reaction[0]
                if type == "SIG":
                    type = "XS"
                plot_link = f"{URL_PATH}reactions/{type.lower()}?target_elem={elem}&target_mass={mass}&inc_pt={inc_pt}&reaction={reaction}"

                return "Plot in IAEA Nuclear Reaction Data Explorer", plot_link

    return no_update, no_update
