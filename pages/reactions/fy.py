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
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go


from common import (
    sidehead,
    footer,
    libs_navbar,
    page_urls,
    lib_selections,
    lib_page_urls,
    input_check,
    energy_range_conversion,
)
from libraries.datahandle.list import (
    PARTICLE_FY,
    read_mt_json,
    read_mass_range,
    MT_LIST_FY,
)
from config import BASE_URL
from libraries.datahandle.tabs import create_tabs
from exforparser.sql.queries import (
    reaction_query_fy,
    get_entry_bib,
    data_query,
    lib_query,
    lib_data_query_fy,
)

## Registration of page
dash.register_page(__name__, path="/reactions/fy")


## Initialize common data
reaction_list = read_mt_json()
mass_range = read_mass_range()


## Input layout
def input_fy(**query_strings):
    return [
        dcc.Dropdown(
            id="reaction_category",
            options=lib_selections,
            placeholder="Select reaction",
            persistence=True,
            persistence_type="memory",
            value="FY",
            style={"font-size": "small", "width": "100%"},
        ),
        dcc.Input(
            id="target_elem_fy",
            placeholder="Target element: C, c, Pd, pd, PD",
            persistence=True,
            persistence_type="memory",
            value=query_strings["target_elem"]
            if query_strings.get("target_elem")
            else "U",
            style={"font-size": "small", "width": "100%"},
        ),
        dcc.Input(
            id="target_mass_fy",
            placeholder="Target mass: 0:natural, m:metastable",
            persistence=True,
            persistence_type="memory",
            value=query_strings["target_mass"]
            if query_strings.get("target_mass")
            else "233",
            style={"font-size": "small", "width": "100%"},
        ),
        dcc.Dropdown(
            id="reaction_fy",
            options=[f"{pt.lower()},f" for pt in PARTICLE_FY],
            placeholder="Reaction e.g. (n,f)",
            persistence=True,
            persistence_type="memory",
            value=query_strings["reaction"] if query_strings.get("reaction") else "n,f",
            style={"font-size": "small", "width": "100%"},
        ),
        dcc.Dropdown(
            id="reac_branch_fy",
            options=[
                {"label": "Primary", "value": "PRE"},
                {"label": "Independent", "value": "IND"},
                {"label": "Cumulative", "value": "CUM"},
            ],
            placeholder="Options",
            persistence=True,
            persistence_type="memory",
            value="CUM",
            style={"font-size": "small", "width": "100%"},
        ),
        html.Label("Measured for"),
        dcc.RadioItems(
            id="mesurement_opt_fy",
            options=[
                {"label": "Mass", "value": "A"},
                {"label": "Element", "value": "Z"},
                {"label": "Product", "value": "Product"},
            ],
            value="A",
        ),
        html.Label("Filter by"),
        dcc.Dropdown(
            id="reac_product_fy",
            options=[],
            placeholder="Options",
            persistence=True,
            persistence_type="memory",
            style={"font-size": "small", "width": "100%"},
        ),
        html.Label("Plot by"),
        dcc.RadioItems(["Mass", "Charge", "Energy"], "Mass", id="plot_opt_fy"),
        html.Br(),
        html.P("Fileter EXFOR records by"),
        html.Label("Energy Range"),
        dcc.RangeSlider(
            id="energy_range_fy",
            min=0,
            max=9,
            marks={0: "eV", 3: "keV", 6: "MeV", 9: "GeV"},
            value=[0, 9],
            vertical=False,
        ),
        html.Br(),
        html.Label("Year Range"),
        dcc.RangeSlider(
            id="year_range_fy",
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
    ]


## Default figure
main_fig_fy = dcc.Graph(
    id="main_fig_fy",
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
right_layout_fy = [
    libs_navbar,
    html.Hr(style={"border": "3px", "border-top": "1px solid"}),
    html.Div(id="result_cont_fy"),
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
    dcc.Loading(
        children=main_fig_fy,
        type="circle",
    ),
    html.Hr(style={"border": "3px", "border-top": "1px solid"}),
    create_tabs("fy"),
    html.Hr(style={"border": "3px", "border-top": "1px solid"}),
    footer,
]


def layout(**query_strings):
    return html.Div(
        [
            dcc.Location(id="location_fy"),
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
                                    html.Div(input_fy(**query_strings)),
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
                                children=right_layout_fy,
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
    Output("location_fy", "href", allow_duplicate=True),
    Input("dataset", "value"),
    prevent_initial_call=True,
)
def redirect_to_pages(dataset):
    if dataset:
        return page_urls[dataset]
    else:
        raise PreventUpdate


@callback(
    Output("location_fy", "href", allow_duplicate=True),
    Input("reaction_category", "value"),
    prevent_initial_call=True,
)
def redirect_to_subpages(type):
    if type:
        return lib_page_urls[type]
    else:
        raise PreventUpdate


@callback(
    Output("location_fy", "href", allow_duplicate=True),
    [
        Input("reaction_category", "value"),
        Input("target_elem_fy", "value"),
        Input("target_mass_fy", "value"),
        Input("reaction_fy", "value"),
    ],
    prevent_initial_call=True,
)
def redirection_fy(type, elem, mass, reaction):
    input_check(type, elem, mass, reaction)

    if type == "FY" and (elem and mass and reaction):
        url = BASE_URL + "/reactions/fy"

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
        Output("result_cont_fy", "children"),
        Output("main_fig_fy", "figure"),
        Output("reac_product_fy", "options"),
        Output("index_table_fy", "rowData"),
        Output("exfor_table_fy", "rowData"),
    ],
    [
        Input("reaction_category", "value"),
        Input("target_elem_fy", "value"),
        Input("target_mass_fy", "value"),
        Input("reaction_fy", "value"),
        Input("reac_branch_fy", "value"),
        Input("mesurement_opt_fy", "value"),
        Input("reac_product_fy", "value"),
        Input("plot_opt_fy", "value"),
        Input("energy_range_fy", "value"),
    ],
)
def update_fig_fy(
    type,
    elem,
    mass,
    reaction,
    branch,
    mesurement_opt_fy,
    reac_product_fy,
    plot_opt_fy,
    energy_range,
):
    elem, mass, reaction = input_check(type, elem, mass, reaction)
    print(type, elem, mass, reaction, branch)

    df = pd.DataFrame()
    index_df = pd.DataFrame()
    reac_products = []

    fig = go.Figure(
        layout=go.Layout(
            xaxis={"title": "Mass number", "type": "linear"},
            yaxis={"title": "Fission yields [/fission]", "type": "linear"},
            margin={"l": 40, "b": 40, "t": 30, "r": 0},
        )
    )

    lower, upper = energy_range_conversion(energy_range)

    entries = reaction_query_fy(
        type, elem, mass, reaction, branch, mesurement_opt_fy, energy_range
    )

    mt = MT_LIST_FY[branch]
    libs = lib_query(type, elem, mass, reaction, mt, rp_elem=None, rp_mass=None)
    search_result = f"Search results for {type} {elem}-{mass}({reaction}): {len(entries)} at {lower}-{upper} MeV for {reac_product_fy}"

    if not entries and not libs:
        return search_result, fig, [], None, None

    if libs:
        df_lib = lib_data_query_fy(libs.keys(), lower, upper)

        if plot_opt_fy == "Mass":
            x_ax = "mass"
            dff = df_lib.groupby(["reaction_id", "mass", "en_inc"], as_index=False)[
                "data"
            ].max(numeric_only=True)


        elif plot_opt_fy == "Charge":
            x_ax = "charge"
            fig.update_layout(dict(xaxis={"title": "Charge number"}))

        elif plot_opt_fy == "Energy":
            x_ax = "en_inc"
            fig.update_layout(dict(xaxis={"title": "Incident energy [MeV]"}))

        for l in libs.keys():
            fig.add_trace(
                go.Scattergl(
                    x=dff[dff["reaction_id"] == l]["mass"].astype(float),
                    y=dff[dff["reaction_id"] == l]["data"].astype(float),
                    showlegend=True,
                    # line_color=new_col,
                    name=str(libs[l]),
                    mode="lines",
                )
            )

    if entries:
        legend = get_entry_bib(e[:5] for e in entries.keys())
        legend = {
            t: dict(**i, **v)
            for k, i in legend.items()
            for t, v in entries.items()
            if k == t[:5]
        }

        ## All data
        df = data_query(entries.keys())
        ## Some case like 41084-007-0 contains None in residual
        reac_products = sorted([i for i in df["residual"].unique() if i is not None])

        df2 = df.copy()

        ## Filtered by reaction product
        if reac_product_fy:
            df2 = df2[df2["residual"] == reac_product_fy]

        if mesurement_opt_fy == "A":
            x_ax = "mass"

        elif mesurement_opt_fy == "Z":
            x_ax = "charge"

        else:
            x_ax = "mass"

        if plot_opt_fy == "Mass":
            x_ax = "mass"
            fig.update_layout(dict(xaxis={"title": "Mass number"}))

        elif plot_opt_fy == "Charge":
            x_ax = "charge"
            fig.update_layout(dict(xaxis={"title": "Charge number"}))

        elif plot_opt_fy == "Energy":
            x_ax = "en_inc"
            fig.update_layout(dict(xaxis={"title": "Incident energy [MeV]"}))

        i = 0
        # ------
        for e in legend.keys():
            fig.add_trace(
                go.Scattergl(
                    x=df2[df2["entry_id"] == e][x_ax],
                    y=df2[df2["entry_id"] == e]["data"],
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
        # ------

        index_df = pd.DataFrame.from_dict(legend, orient="index").reset_index()
        index_df.rename(columns={"index": "entry_id"}, inplace=True)
        index_df["entry_id_link"] = (
            "["
            + index_df["entry_id"]
            + "](../exfor/entry/"
            + index_df["entry_id"]
            + ")"
        )
        df["bib"] = df["entry_id"].map(legend)
        df = pd.concat([df, df["bib"].apply(pd.Series)], axis=1)
        df = df.drop(columns=["bib"])
        df["entry_id_link"] = (
            "["
            + df["entry_id"]
            + "](../exfor/entry/"
            + df["entry_id"]
            + ")"
        )

    return (
        search_result,
        fig,
        reac_products,
        index_df.to_dict("records"),
        df.to_dict("records"),
    )


@callback(
    Output("main_fig_fy", "figure", allow_duplicate=True),
    [
        Input("xaxis_type", "value"),
        Input("yaxis_type", "value"),
    ],
    State("main_fig_fy", "figure"),
    prevent_initial_call=True,
)
def update_axis_fy(xaxis_type, yaxis_type, fig):
    ## Switch the axis type
    fig.get("layout").get("yaxis").update({"type": yaxis_type})
    fig.get("layout").get("xaxis").update({"type": xaxis_type})

    return fig


@callback(
    [
        Output("main_fig_fy", "figure", allow_duplicate=True),
        Output("index_table_fy", "filter_query"),
    ],
    Input("year_range_fy", "value"),
    State("main_fig_fy", "figure"),
    prevent_initial_call=True,
)
def fileter_by_range_fy(year_range, fig):
    # print(json.dumps(fig, indent=1))

    filter = "{year} ge " + str(year_range[0]) + " && {year} le " + str(year_range[1])

    for records in fig.get("data"):
        author, year = records.get("name").split(",")

        if not year_range[0] < int(year) < year_range[1]:
            records.update({"visible": "legendonly"})

        if year_range[0] < int(year) < year_range[1]:
            records.update({"visible": "true"})

    return fig, filter
