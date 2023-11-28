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


from pages_common import (

    sidehead,
    footer,
    libs_navbar,
    URL_PATH,
    page_urls,
    lib_selections,
    lib_page_urls,
    input_check,
    energy_range_conversion,
)
from submodules.utilities.elem import elemtoz_nz
from submodules.utilities.mass import mass_range


from submodules.utilities.reaction import reaction_list
from modules.reactions.tabs import create_tabs
from modules.reactions.figs import default_chart, default_axis
from submodules.reactions.queries import (
    lib_query,
    lib_xs_data_query,
)
from submodules.exfor.queries import (
    index_query,
    get_entry_bib,
    data_query,
)


## Registration of page
dash.register_page(__name__, path="/reactions/fission")


## Input layout
def input_fis(**query_strings):
    return [
        html.Label("Observable"),
        dcc.Dropdown(
            id="reaction_category",
            options=lib_selections,
            placeholder="Select reaction",
            persistence=True,
            persistence_type="memory",
            value="FIS",
            style={"font-size": "small", "width": "100%"},
        ),
        dcc.Input(
            id="target_elem_fis",
            placeholder="Target element: C, c, Pd, pd, PD",
            persistence=True,
            persistence_type="memory",
            value=query_strings["target_elem"]
            if query_strings.get("target_elem")
            else "U",
            style={"font-size": "small", "width": "100%"},
        ),
        dcc.Input(
            id="target_mass_fis",
            placeholder="Target mass: 0:natural, m:metastable",
            persistence=True,
            persistence_type="memory",
            value=query_strings["target_mass"]
            if query_strings.get("target_mass")
            else "233",
            style={"font-size": "small", "width": "100%"},
        ),
        dcc.Dropdown(
            id="reaction_fis",
            options=[f"{pt.lower()},f" for pt in PARTICLE_FY],
            placeholder="Reaction e.g. (n,f)",
            persistence=True,
            persistence_type="memory",
            value=query_strings["reaction"] if query_strings.get("reaction") else "n,f",
            style={"font-size": "small", "width": "100%"},
        ),
        dcc.Dropdown(
            id="reac_branch_fis",
            options=[
                {"label": "neutron multiplicity", "value": "nu_n"},
                {"label": "delayed neutron yield", "value": "dn"},
                {"label": "gamma multiplicity", "value": "nu_g"},
                {"label": "neutron spectra", "value": "pfns"},
                {"label": "gamma spectra", "value": "pfgs"},
            ],
            placeholder="Options",
            persistence=True,
            persistence_type="memory",
            value="dn",
            style={"font-size": "small", "width": "100%"},
        ),
        html.P("Fileter EXFOR records by"),
        html.Label("Energy Range"),
        dcc.RangeSlider(
            id="energy_range_fis",
            min=0,
            max=9,
            marks={0: "eV", 3: "keV", 6: "MeV", 9: "GeV"},
            value=[0, 9],
            vertical=False,
        ),
        html.Br(),
        html.Label("Year Range"),
        dcc.RangeSlider(
            id="year_range_fis",
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
    id="main_fig_fis",
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
    html.Div(id="result_cont_fis"),
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
                    id="yaxis_type",
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
    dcc.Loading(
        children=main_fig_fy,
        type="circle",
    ),
    dcc.Store(id="entry_json"),
    html.Hr(style={"border": "3px", "border-top": "1px solid"}),
    create_tabs("FIS"),
    html.Hr(style={"border": "3px", "border-top": "1px solid"}),
    footer,
]


def layout(**query_strings):
    return html.Div(
        [
            dcc.Location(id="location_fis"),
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
                                    html.Div(input_fis(**query_strings)),
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
    Output("location_fis", "href", allow_duplicate=True),
    Input("dataset", "value"),
    prevent_initial_call=True,
)
def redirect_to_pages(dataset):
    if dataset:
        return page_urls[dataset]
    else:
        raise PreventUpdate


@callback(
    Output("location_fis", "href", allow_duplicate=True),
    Input("reaction_category", "value"),
    prevent_initial_call=True,
)
def redirect_to_subpages(type):
    if type:
        return lib_page_urls[type]
    else:
        raise PreventUpdate


@callback(
    Output("location_fis", "href", allow_duplicate=True),
    [
        Input("reaction_category", "value"),
        Input("target_elem_fis", "value"),
        Input("target_mass_fis", "value"),
        Input("reaction_fis", "value"),
    ],
    prevent_initial_call=True,
)
def redirection_fy(type, elem, mass, reaction):
    elem, mass, reaction = input_check(type, elem, mass, reaction)

    if type == "FIS" and (elem and mass and reaction):
        url = URL_PATH + "reactions/fission"

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
        Output("result_cont_fis", "children"),
        Output("main_fig_fis", "figure"),
        Output("index_table_fis", "rowData"),
        Output("exfor_table_fis", "rowData"),
    ],
    [
        Input("reaction_category", "value"),
        Input("target_elem_fis", "value"),
        Input("target_mass_fis", "value"),
        Input("reaction_fis", "value"),
        Input("reac_branch_fis", "value"),
        Input("energy_range_fis", "value"),
    ],
)
def update_fig_fy(type, elem, mass, reaction, branch, energy_range):
    input_check(type, elem, mass, reaction)
    print(type, elem, mass, reaction, branch)

    df = pd.DataFrame()
    index_df = pd.DataFrame()
    reac_products = []

    fig = go.Figure(
        layout=go.Layout(
            xaxis={"title": "Incident neutron energy [MeV]", "type": "linear"},
            yaxis={
                "title": "Fission obserbvable",
                "type": "linear",
            },
            margin={"l": 40, "b": 40, "t": 30, "r": 0},
        )
    )

    lower, upper = energy_range_conversion(energy_range)
    entries = index_query_fission(type, elem, mass, reaction, branch, energy_range)
    search_result = f"Search results for {type} {elem}-{mass}({reaction}): {len(entries)} at {lower}-{upper} MeV "
    print(search_result)

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

        i = 0
        # ------
        for e in legend.keys():
            if any(branch == b for b in ("nu_n", "nu_g", "dn")):
                fig.add_trace(
                    go.Scatter(
                        x=df2[df2["entry_id"] == e]["en_inc"],
                        y=df2[df2["entry_id"] == e]["data"],
                        error_y=dict(
                            type="data", array=df[df["entry_id"] == e]["ddata"]
                        ),
                        showlegend=True,
                        name=f"{legend[e]['author']}, {legend[e]['year']}"
                        if legend[e].get("year")
                        else legend[e]["author"],
                        marker=dict(size=8, symbol=i),
                        mode="markers",
                    )
                )
            elif any(branch == b for b in ("pfns", "pfgs")):
                fig.add_trace(
                    go.Scatter(
                        x=df2[df2["entry_id"] == e]["e_out"],
                        y=df2[df2["entry_id"] == e]["data"],
                        error_y=dict(
                            type="data", array=df[df["entry_id"] == e]["ddata"]
                        ),
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
            + "](http://127.0.0.1:8050/dataexplorer/exfor/entry/"
            + index_df["entry_id"]
            + ")"
        )
        df["bib"] = df["entry_id"].map(legend)
        df = pd.concat([df, df["bib"].apply(pd.Series)], axis=1)
        df = df.drop(columns=["bib"])
        df["entry_id_link"] = (
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
    Output("main_fig_fis", "figure", allow_duplicate=True),
    [
        Input("xaxis_type", "value"),
        Input("yaxis_type", "value"),
    ],
    State("main_fig_fis", "figure"),
    prevent_initial_call=True,
)
def update_axis_fy(xaxis_type, yaxis_type, fig):
    ## Switch the axis type
    fig.get("layout").get("yaxis").update({"type": yaxis_type})
    fig.get("layout").get("xaxis").update({"type": xaxis_type})

    return fig


@callback(
    [
        Output("main_fig_fis", "figure", allow_duplicate=True),
        Output("index_table_fis", "filter_query"),
    ],
    Input("year_range_fis", "value"),
    State("main_fig_fis", "figure"),
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


@callback(
    Output("exfor_table_fis", "exportDataAsCsv"),
    Input("csv-button_fis", "n_clicks"),
)
def export_data_as_csv_fis(n_clicks):
    if n_clicks:
        return True

    return False
