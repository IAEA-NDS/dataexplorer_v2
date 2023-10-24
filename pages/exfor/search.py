####################################################################
#
# This file is part of libraries-2023 dataexplorer, https://nds.iaea.org/dataexplorer/.
# Copyright (C) 2022 International Atomic Energy Agency (IAEA)
#
# Contact:    nds.contact-point@iaea.org
#
####################################################################

import pandas as pd
import datetime

import dash
from dash import Dash, html, dcc, Input, Output, State, ctx, no_update, callback
from dash.dash_table.Format import Format, Scheme
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

## from dataexplorer modules
from common import (
    PARTICLE,
    PARTICLE_FY,
    sidehead,
    URL_PATH,
    page_urls,
    exfor_navbar,
    footer,
    input_general,
    input_check,
    exfor_filter_opt,
)
from exfor.list import get_institutes, MAPPING
from exfor.stat import stat_right_layout
from exfor.aggrid import aggrid_layout
from submodules.exfor.queries import index_query_simple, join_index_bib
from libraries.list import reaction_list

## Registory of the page
dash.register_page(__name__, path="/exfor/search")

today = datetime.date.today()
year = today.year
pageparam = "ex"


def input(**query_strings):
    return [
        html.Label("Entry number/Entry id search"),
        dcc.Input(
            id="entid_ex",
            type="text",
            placeholder="e.g. 12345, 12345-003-0",
            persistence=True,
            persistence_type="memory",
            # size="md",
            style={"font-size": "small", "width": "95%", "margin-left": "6px"},
        ),
        html.Br(),
        html.Br(),
        html.Label("Reaction index search"),
        html.Div(children=input_general(pageparam, **query_strings)),
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
                            style={"font-size": "small", "width": "100%"},
                        ),
                        dcc.Input(
                            id="authors",
                            placeholder="One of the authors",
                            persistence=True,
                            persistence_type="memory",
                            style={"font-size": "small", "width": "100%"},
                        ),
                        dcc.Input(
                            id="sf4",
                            placeholder="EXFOR SF4",
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
                            placeholder="EXFOR SF5",
                            persistence=True,
                            persistence_type="memory",
                            style={"font-size": "small", "width": "100%"},
                        ),
                        dcc.Input(
                            id="sf7",
                            placeholder="EXFOR SF7",
                            persistence=True,
                            persistence_type="memory",
                            style={"font-size": "small", "width": "100%"},
                        ),
                        dcc.Input(
                            id="sf8",
                            placeholder="EXFOR SF8",
                            persistence=True,
                            persistence_type="memory",
                            style={"font-size": "small", "width": "100%"},
                        ),
                        html.Button("Apply", id="apply_btn", n_clicks=0),
                    ],
                    title="More options",
                ),
            ],
            start_collapsed=True,
        ),
        dcc.Store(id="input_store_ex"),
        html.Br(),
        html.Div(children=exfor_filter_opt("ex")),
        html.Br(),
        html.Br(),
        html.Label("Other search options"),
        # dcc.Link(html.Label("Entry search"), href=URL_PATH + "exfor"),
        dcc.Link(html.Label("Geo search"), href=URL_PATH + "exfor/geo"),
        dcc.Link(
            html.Label("Search from all reaction index"), href=URL_PATH + "exfor/index"
        ),
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
            ## Aggrid version
            aggrid_layout("result"),
            ## Dash table version
            # dash_table.DataTable(
            #     id="index-all-result",
            #     columns=[
            #         {"name": "Author", "id": "first_author"},
            #         {"name": "Year", "id": "year"},
            #         {"name": "#Entry", "id": "entry_id", "presentation": "markdown"},
            #         {
            #             "name": "E_min[eV]",
            #             "id": "e_inc_min",
            #             "type": "numeric",
            #             "format": Format(precision=3, scheme=Scheme.exponent),
            #         },
            #         {
            #             "name": "E_max[eV]",
            #             "id": "e_inc_max",
            #             "type": "numeric",
            #             "format": Format(precision=3, scheme=Scheme.exponent),
            #         },
            #         {"name": "Points", "id": "points"},
            #         {"name": "Reaction Code", "id": "x4_code"},
            #         {"name": "level", "id": "level_num"},
            #         {"name": "Facility", "id": "main_facility_type"},
            #     ],
            #     filter_action="native",
            #     sort_action="native",
            #     sort_mode="single",
            #     markdown_options={"html": True},
            #     page_action="native",
            #     page_current=0,
            #     page_size=10,
            #     row_selectable="multi",
            #     row_deletable=True,
            #     selected_columns=[],
            #     selected_rows=[],
            # ),
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
                                        value="EXFOR Viewer",
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
                                children=search_result_layout
                                if query_strings
                                else stat_right_layout,
                                style={"margin-right": "20px"},
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
    url = URL_PATH + "exfor/entry/"
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
        Input("observable_ex", "value"),
        Input("reaction_ex", "value"),
    ],
)
def update_branch_list_ex(type, reaction):
    print("update_branch_list")
    if not reaction or not type:
        raise PreventUpdate

    if type == "FY":
        reactions = [f"{pt.lower()},f" for pt in PARTICLE_FY]

        return (
            reactions,
            [
                {"label": "Independent", "value": "IND"},
                {"label": "Cumulative", "value": "CUM"},
                {"label": "Primary", "value": "PRE"},
            ],
            None,
        )

    else:
        reactions = [
            {
                "label": f"{proj.lower()},{reac.lower()}",
                "value": f"{proj.lower()},{reac.lower()}",
            }
            for proj in PARTICLE
            for reac in reaction_list.keys()
        ]  # + [{"label": "Other", "value": "other"}]

        if reaction.split(",")[1].upper() == "INL":
            return (
                reactions,
                [{"label": "L" + str(n), "value": n} for n in range(0, 40)],
                None,
            )

        else:
            return reactions, [{"label": "Partial", "value": "PAR"}], None


@callback(
    Output("input_store_ex", "data"),
    [
        Input("observable_ex", "value"),
        Input("target_elem_ex", "value"),
        Input("target_mass_ex", "value"),
        Input("reaction_ex", "value"),
        Input("reac_branch_ex", "value"),
        State("first_author", "value"),
        State("authors", "value"),
        State("sf4", "value"),
        State("facility", "value"),
        State("sf5", "value"),
        State("sf7", "value"),
        State("sf8", "value"),
        Input("apply_btn", "n_clicks"),
    ],
    prevent_initial_call=True,
)
def input_store_ex(
    type,
    elem,
    mass,
    reaction,
    branch,
    author,
    authors,
    sf4,
    facility,
    sf5,
    sf7,
    sf8,
    apply_btn,
):
    input_check(type, elem, mass, reaction)
    print("#### search for ", type, elem, mass, reaction, branch)

    if apply_btn:
        return {
            "type": type,
            "elem": elem,
            "mass": mass,
            "reaction": reaction,
            "branch": branch,
            "first_author": author,
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
            "first_author": None,
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
        first_author = input_store.get("author")
        authors = input_store.get("authors")
        sf4 = input_store.get("sf4")
        sf5 = input_store.get("sf5")
        sf7 = input_store.get("sf7")
        sf8 = input_store.get("sf8")
        facility = input_store.get("facility")

    else:
        raise PreventUpdate

    url = URL_PATH + "exfor/search?"

    if type:
        url += "type=" + type

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
    Input("input_store_ex", "data"),
)
def create_plot_link(input_store):
    if input_store:
        type = input_store.get("type")
        elem = input_store.get("elem")
        mass = input_store.get("mass")
        reaction = input_store.get("reaction")
        branch = input_store.get("branch")

    if any(type == t for t in ["DA", "FY", "XS", "DE", "FIS"]):
        if type == "SIG":
            type = "XS"
        plot_link = f"{URL_PATH}reactions/{type.lower()}?target_elem={elem}&target_mass={mass}&reaction={reaction}"

        return "Plot in IAEA Nuclear Reaction Data Explorer", plot_link

    else:
        return no_update, no_update


@callback(
    [Output("search_result_count", "children"), Output("index-all-result", "rowData")],
    Input("input_store_ex", "data"),
)
def search_exfor_record_by_reaction(input_store):
    if input_store:
        type = input_store.get("type")
        elem = input_store.get("elem")
        mass = input_store.get("mass")
        reaction = input_store.get("reaction")
        branch = input_store.get("branch")

    df = index_query_simple(type, elem, mass, reaction, branch)
    df["entry_id"] = (
        "[" + df["entry_id"] + "](" + URL_PATH + "exfor/entry/" + df["entry_id"] + ")"
    )

    search_result = f"Search results for {elem}-{mass}({reaction}): {len(df.index)}"

    return search_result, df.to_dict("records")


# @callback(
#     Output("datatable-interactivity-container", "children"),
#     [
#         Input("index-all-result", "data"),
#         Input("index-all-result", "derived_virtual_data"),
#         Input("index-all-result", "derived_virtual_selected_rows"),
#     ],
# )
# def update_graphs_ex(df_dict, rows, derived_virtual_selected_rows):
#     df = pd.DataFrame.from_dict(df_dict)
#     dff = df if rows is None else pd.DataFrame(rows)

#     if derived_virtual_selected_rows is None:
#         derived_virtual_selected_rows = []

#     return [
#         dcc.Graph(
#             id=column,
#             figure={
#                 "data": [
#                     {
#                         "x": dff[column],
#                         "y": dff["points"],
#                         "type": "bar",
#                     }
#                 ],
#                 "layout": {
#                     "xaxis": {"automargin": True, "title": {"text": column}},
#                     "yaxis": {"automargin": True, "title": {"text": "data points"}},
#                     "height": 250,
#                     "margin": {"t": 10, "l": 10, "r": 10},
#                 },
#             },
#         )
#         for column in [
#             "year",
#             "e_inc_min",
#             "main_facility_type",
#             "main_facility_institute",
#             "first_author_institute",
#         ]
#         if column in dff
#     ]


@callback(
    Output("index-all-index", "rowData"),
    Input("target_elem_ex", "value"),
)
def aggrid_data_add(target_elem_ex):
    if not target_elem_ex:
        df = join_index_bib()
        return df.to_dict("records")

    else:
        return pd.DataFrame()
