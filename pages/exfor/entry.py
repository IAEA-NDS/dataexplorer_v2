####################################################################
#
# This file is part of libraries-2021 dataexplorer, https://nds.iaea.org/dataexplorer/.
# Copyright (C) 2022 International Atomic Energy Agency (IAEA)
#
# Contact:    nds.contact-point@iaea.org
#
####################################################################

import re
import pandas as pd

import dash
from dash import html, dcc, callback, Input, dash_table, Output, State
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go

# from app import app
from config import BASE_URL, API_BASE_URL, MASTER_GIT_REPO_URL
from common import (
    sidehead,
    page_urls,
    exfor_navbar,
    footer,
    dict_merge,
    data_length_unify,
)
from exfor.exfor_record import get_record, get_git_history_api
from exfor_dictionary import Diction
from exfor.exfor_stat import stat_right_layout


dash.register_page(__name__, path="/exfor", path_template="/exfor/entry/<entry_id>")

D = Diction()


def input_ex(entry_id=None):
    return dbc.Row(
        [
            html.Label("Entry search"),
            dcc.Input(
                id="exfor_entid",
                type="text",
                placeholder="Entry number",
                persistence=True,
                persistence_type="memory",
                # size="md",
                style={"font-size": "small", "width": "95%", "margin-left": "6px"},
                value=entry_id,
            ),
            dcc.Link(html.Label("Reaction search"), href=BASE_URL + "/exfor/search"),
        ]
    )


# See https://dash.plotly.com/dash-core-components/graph
main_fig = dcc.Graph(
    id="main_graph_ex",
    config={
        "displayModeBar": True,
        "scrollZoom": True,
        "modeBarButtonsToAdd": ["drawline", "drawopenpath", "eraseshape"],
        "modeBarButtonsToRemove": ["lasso2d"],
    },
    figure={
        "layout": {
            "height": 550,
        }
    },
)


def generate_fig(df):
    colnames = df.keys()
    null_x = dict(
        method="update",
        label="",
        visible=True,
        args=[
            {"x": ["" for _ in range(len(df))]},
            {"xaxis": {"title": ""}},
        ],
    )
    null_y = dict(
        method="update",
        label="",
        visible=True,
        args=[
            {"y": ["" for _ in range(len(df))]},
            {"yaxis": {"title": ""}},
        ],
    )
    button_x_list = []
    button_y_list = []
    button_x_list.append(null_x)
    button_y_list.append(null_y)

    for col in colnames:
        button_x_list.append(
            dict(
                method="update",
                label=col,
                visible=True,
                args=[
                    {"x": [df[col]]},
                    {"xaxis": {"title": col}},
                ],
            )
        )

        button_y_list.append(
            dict(
                method="update",
                label=col,
                visible=True,
                args=[
                    {"y": [df[col]]},
                    {"yaxis": {"title": col}},
                ],
            )
        )

    button_x_dict = dict(
        direction="down",
        showactive=True,
        xanchor="left",
        yanchor="top",
        visible=True,
        buttons=button_x_list,
        pad={"r": 15, "t": 10},
        x=0.03,
        y=1.15,
    )
    button_y_dict = dict(
        direction="down",
        showactive=True,
        xanchor="left",
        yanchor="top",
        visible=True,
        buttons=button_y_list,
        pad={"r": 15, "t": 10},
        x=0.33,
        y=1.15,
    )
    annotation_x = dict(
        text="X:",
        showarrow=False,
        x=0,
        y=1.12,
        xanchor="left",
        xref="paper",
        yref="paper",
        align="left",
        yanchor="top",
    )
    annotation_y = dict(
        text="Y:",
        showarrow=False,
        x=0.3,
        y=1.12,
        xanchor="left",
        xref="paper",
        yref="paper",
        align="left",
        yanchor="top",
    )
    fig = go.Figure(
        go.Scatter(
            x=pd.Series(dtype=object), y=pd.Series(dtype=object), mode="lines+markers"
        )
    )
    fig.update_layout(
        updatemenus=[button_x_dict, button_y_dict],
        annotations=[annotation_x, annotation_y],
        xaxis={"title": ""},
        yaxis={"title": ""},
    )
    return fig


## right panel of the EXFOR page layout
record_right_layout = [
    exfor_navbar,
    html.Hr(style={"border": "3px", "border-top": "1px solid"}),
    html.Div(id="exfor_entry_links"),
    html.Br(),
    html.Div(id="exfor_entry_bib"),
    html.Br(),
    html.Div(id="exfor_entry_exp"),
    html.Hr(style={"border": "3px", "border-top": "1px solid"}),
    dbc.Row(
        [
            dbc.Col(
                [
                    html.Div(
                        children=[
                            dbc.Badge(
                                "Download CSV",
                                id="btn_csv",
                                href="#",
                                color="secondary",
                            ),
                            dcc.Download(id="download-dataframe-csv"),
                        ],
                        style={"textAlign": "right", "margin-bottom": "10px"},
                    ),
                    html.Div(id="data-table"),
                ]
            ),
            dbc.Col(main_fig),
        ]
    ),
    dcc.Store(id="entry_store"),
    html.Hr(style={"border": "3px", "border-top": "1px solid"}),
    footer,
]


## EXFOR page layout
def layout(entry_id=None):
    if entry_id:
        if len(entry_id) == 5:
            right_layout = record_right_layout

        elif len(entry_id) == 11:
            right_layout = record_right_layout

        else:
            raise PreventUpdate

    else:
        right_layout = stat_right_layout

    return html.Div(
        [
            dcc.Location(id="location_ex"),
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
                                    html.Div(
                                        input_ex(entry_id if entry_id else None),
                                        id="sidebar_input",
                                    ),
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
        id="main_layout_ex",
        style={"height": "100vh"},
    )


def show_compile_history(entry_json):
    hist_data = []
    for history in entry_json["histories"]:
        hist_data += [
            dbc.Row([dbc.Col(history["x4_code"]), dbc.Col(history["free_txt"])])
        ]
    return hist_data


def show_entry_links(entnum, entry_json):
    # get history from Github REST API
    gitlog_json = get_git_history_api(entnum)

    # get EXFOR comiplation history from dataexplorer API
    tooltip = dbc.Tooltip(
        show_compile_history(entry_json),
        target=f"exfor_compile_history",
        placement="bottom",
        style={
            "font-size": "small",
            "max-width": 400,
            "min-width": 400,
            "word-break": "break-all",
            "word-wrap": "break-word",
        },  # , "white-space": "normal"},
    )

    return dbc.Row(
        [
            dbc.Col(
                [
                    f"Entry number: {entnum}: " "Last updated on ",
                    html.A(gitlog_json[0]["message"], href=gitlog_json[0]["html_url"]),
                    f" (Rev. {len(gitlog_json)})",
                    "  ",
                    html.A(
                        "Compilation history",
                        href=f"{API_BASE_URL}exfor/entry/{entnum}/histories",
                        id="exfor_compile_history",
                    ),
                    tooltip,
                    "  ",
                    dbc.Badge(
                        "EXFOR",
                        href=f"https://nds.iaea.org/EXFOR/{entnum}",
                        color="primary",
                        className="me-1",
                    ),
                    dbc.Badge(
                        "Git",
                        href=f"{MASTER_GIT_REPO_URL}/blob/main/exforall/{entnum[0:3]}/{entnum}.x4",
                        color="warning",
                        className="me-1",
                    ),
                    dbc.Badge(
                        "JSON",
                        href=f"{API_BASE_URL}exfor/entry/{entnum}",
                        color="success",
                        className="me-1",
                    ),
                ],
                style={"textAlign": "right"},
            )
        ]
    )


def show_entry_bib(entry_json):
    tooltips_inst = []

    ## Loop for institute information
    for inst in entry_json["bib_record"]["institutes"]:
        x4_code = inst["x4_code"]
        # freetext = "\n".join( inst["free_txt"] )

        if x4_code:
            tooltips_inst += make_tooltip("institutes", x4_code)

    ## Put bib_record info together to the html row
    bib_row_data = [
        dbc.Row(
            [
                dbc.Col(html.P("Title:"), width=2),
                dbc.Col(html.P(entry_json["bib_record"]["title"])),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(html.P("Autors:"), width=2),
                dbc.Col(
                    html.P(
                        [v["name"] + ", " for v in entry_json["bib_record"]["authors"]]
                    )
                ),
            ]
        ),
        dbc.Row([dbc.Col(html.P("Institute:"), width=2), dbc.Col(tooltips_inst)]),
        dbc.Row(
            [
                dbc.Col(html.P("References:"), width=2),
                dbc.Col(
                    html.P(
                        [
                            v["x4_code"] + ", "
                            for v in entry_json["bib_record"]["references"]
                        ]
                    )
                ),
            ]
        ),
    ]

    ## Get reactions and put all reactions into dropdown menue
    reac = {}

    for sub in entry_json["reactions"].keys():
        for p, dic in entry_json["reactions"][sub].items():
            ## add reaction code to entry_id e.g. 11111-002-0: (92-U-235(N,F),,SIG)
            reac[entry_json["entry"] + "-" + sub + "-" + p] = dic["x4_code"]

    reac_dropdown = [
        dbc.Row(
            [
                dbc.Col(html.P("Reactions:"), width=2),
                dbc.Col(
                    dcc.Dropdown(
                        id="selected_reaction",
                        options=[
                            {"label": k + ": " + v, "value": k} for k, v in reac.items()
                        ],
                        value=list(reac.keys())[0],
                    )
                ),
            ]
        )
    ]

    data = dbc.Row(bib_row_data + reac_dropdown)

    return data


def show_entry_experimental_condition(entid, entry_json):
    entnum, subent, pointer = entid.split("-")
    exp_conditions = []
    tooltips = []

    if pointer != "0":
        pointers = ["0", pointer]

    else:
        pointers = [pointer]

    ## get experimental conditions from SUBENT 001 and this subentry
    for s in ["001", subent]:
        if not entry_json["experimental_conditions"].get(s):
            continue
        for p in pointers:
            if not entry_json["experimental_conditions"][s].get(p):
                continue

            for key, item in entry_json["experimental_conditions"][s][p].items():
                x4_code = None
                tooltips = None
                freetext = None
                cols = []

                for i in item:
                    x4_code = i["x4_code"]
                    freetext = html.Div(children="\n".join(i["free_txt"]))

                    if x4_code:
                        tooltips = make_tooltip(key, x4_code)

                    if tooltips:
                        cols += [
                            dbc.Col(tooltips, width=3),
                            dbc.Col(
                                freetext, width=7, style={"whiteSpace": "pre-wrap"}
                            ),
                        ]

                    else:
                        cols += [dbc.Col(x4_code, width=3), dbc.Col(freetext, width=7)]

                exp_conditions += [
                    dbc.Row(
                        [dbc.Col(html.P(key.upper()), width=2), dbc.Col(dbc.Row(cols))]
                    )
                ]

    return dbc.Accordion(
        [
            dbc.AccordionItem(exp_conditions, title="Experimental conditions"),
        ],
        start_collapsed=True,
    )


def make_tooltip(key, x4_code):
    if not x4_code:
        return

    codes = x4_code.replace("(", "").replace(")", "").split(",")
    tooltips = []

    if key == "facility":
        if len(codes) == 1:
            descript = D.get_facility(codes[0])
            descript_inst = ""

        if len(codes) == 2:
            descript = D.get_facility(codes[0])
            descript_inst = D.get_institute(codes[1])

        tooltip = dbc.Tooltip(
            descript + ":  " + descript_inst,
            target=f"tooltip-target-{x4_code}",
            placement="auto",
            style={"font-size": "medium"},
        )

        tooltips = [html.A(f"{x4_code}", id=f"tooltip-target-{x4_code}"), tooltip]

    elif key == "references":
        try:
            descript = D.get_journal(codes[1])
        except:
            try:
                descript = D.get_report(codes[1])
            except:
                descript = ""

        tooltip = dbc.Tooltip(
            descript,
            target=f"tooltip-target-{codes[1]}",
            placement="auto",
            style={"font-size": "medium"},
        )

        tooltips = [html.A(f"({codes[1]})", id=f"tooltip-target-{codes[1]}"), tooltip]

    elif key == "err-analys":
        descript = D.get_err_analysis(codes[0])

        tooltip = dbc.Tooltip(
            descript,
            target=f"tooltip-target-{codes[0]}",
            placement="auto",
            style={"font-size": "medium"},
        )

        tooltips = [html.A(f"({codes[0]})", id=f"tooltip-target-{codes[0]}"), tooltip]

    else:
        for code in codes:
            descript = ""
            if key == "institutes":
                descript = D.get_institute(code)

            elif key == "method":
                descript = D.get_method(code)

            elif key == "detector":
                descript = D.get_detectors(code)

            elif key == "inc-source":
                descript = D.get_inc_sources(code)

            else:
                continue

            tooltip = dbc.Tooltip(
                descript,
                target=f"tooltip-target-{code}",
                placement="auto",
                style={"font-size": "medium"},
            )

            tooltips += [html.A(f"({code}) ", id=f"tooltip-target-{code}"), tooltip]

    return tooltips


def generate_data_table(entry_id, entry_json):
    entnum, subent, pointer = entry_id.split("-")
    #### -----------------------------------------------------
    # This part is taken by tabulated.py from exforparser
    #### -----------------------------------------------------
    common_main_dict = {}
    data_tables_dict = entry_json["data_tables"]
    data_dict = {}

    if not data_tables_dict.get(subent):
        # for deleted entry
        return pd.DataFrame()

    ## get SUBENT 001 COMMON block
    if data_tables_dict["001"].get("common"):
        common_main_dict = data_tables_dict["001"]["common"]

    common_sub_dict = {}

    ## get SUBENT 002 COMMON block
    if data_tables_dict[subent].get("common"):
        common_sub_dict = entry_json["data_tables"][subent]["common"]

    ## get SUBENT 002 DATA block
    if data_tables_dict[subent].get("data"):
        data_dict = dict_merge(
            [
                common_main_dict,
                common_sub_dict,
                entry_json["data_tables"][subent]["data"],
            ]
        )

    if pointer != "0":
        i = 0
        locs = []
        op = []
        for head in data_dict["heads"]:
            ## all columns with any pointers
            if re.match(r"[A-Z1-9-]{1,}\s+[0-9]$", head):
                op += [i]

            ## column with the specific pointer
            if re.match(r"[A-Z1-9-]{1,}\s+" + pointer, head):
                locs += [i]
            i += 1

        ## index of the list with other pointer
        del_locs = [i for i in op if i not in locs]

        ## delete other pointer column from the dictionary
        data_dict["heads"] = [
            v for i, v in enumerate(data_dict["heads"]) if i not in del_locs
        ]
        data_dict["units"] = [
            v for i, v in enumerate(data_dict["units"]) if i not in del_locs
        ]
        data_dict["data"] = [
            v for i, v in enumerate(data_dict["data"]) if i not in del_locs
        ]

    data_dict_conv = data_length_unify(data_dict)

    df = pd.DataFrame.from_dict(data_dict_conv["data"])
    df = df.transpose()

    header = [f"{h} ({u})" for h, u in zip(data_dict["heads"], data_dict["units"])]
    df.columns = header

    return df


###------------------------------------------------------------------------------------
### App Callback
###------------------------------------------------------------------------------------
@callback(
    Output("location_ex", "href", allow_duplicate=True),
    Input("dataset", "value"),
    prevent_initial_call=True,
)
def redirect_to_pages(dataset):
    return page_urls[dataset]


@callback(
    Output("location_ex", "href", allow_duplicate=True),
    Input("exfor_entid", "value"),
    prevent_initial_call=True,
)
def redirect_to_url(entry_id):
    url = BASE_URL + "/exfor/entry/"
    if not entry_id:
        raise PreventUpdate
    elif len(entry_id) != 5 and len(entry_id) != 11:
        raise PreventUpdate
    else:
        url += entry_id
    return url


## Get JSON and store it
@callback(Output("entry_store", "data"), Input("exfor_entid", "value"))
def entry_store(entry_id):
    if not entry_id:
        raise PreventUpdate

    elif len(entry_id) != 5 and len(entry_id) != 11:
        raise PreventUpdate
    else:
        return get_record(entry_id[0:5])


## Generate links
@callback(
    Output("exfor_entry_links", "children"),
    [Input("exfor_entid", "value"), Input("entry_store", "data")],
)
def entnumexfor_entid(entry_id, entry_json):
    if not entry_id:
        raise PreventUpdate

    elif len(entry_id) != 5 and len(entry_id) != 11:
        raise PreventUpdate

    else:
        return show_entry_links(entry_id[0:5], entry_json)


## EXFOR experimental BIB
@callback(
    Output("exfor_entry_bib", "children"),
    [Input("exfor_entid", "value"), Input("entry_store", "data")],
)
def get_entry_bib(entry_id, entry_json):
    if not entry_id:
        raise PreventUpdate

    elif len(entry_id) != 5 and len(entry_id) != 11:
        raise PreventUpdate

    else:
        return show_entry_bib(entry_json)


## input
@callback(
    Output("selected_reaction", "value"),
    Input("exfor_entid", "value"),
)
def get_entry_exp(entry_id):
    if not entry_id:
        raise PreventUpdate

    elif len(entry_id) != 11:
        raise PreventUpdate

    if len(entry_id) == 11:
        return entry_id


## EXFOR experimental condition
@callback(
    Output("exfor_entry_exp", "children"),
    [Input("selected_reaction", "value"), Input("entry_store", "data")],
)
def get_entry_exp(selected_id, entry_json):
    if not selected_id:
        raise PreventUpdate

    if len(selected_id) != 11:
        raise PreventUpdate

    if selected_id and entry_json:
        return show_entry_experimental_condition(selected_id, entry_json)
    else:
        raise PreventUpdate


# Get table and update data
@callback(
    [Output("data-table", "children"), Output("main_graph_ex", "figure")],
    [Input("selected_reaction", "value"), Input("entry_store", "data")],
)
def update_fig_data(selected_id, entry_json):
    if not selected_id:
        raise PreventUpdate

    if len(selected_id) != 11:
        raise PreventUpdate

    df = generate_data_table(selected_id, entry_json)
    fig = generate_fig(df)

    table = (
        dash_table.DataTable(
            id="data-column",
            data=df.to_dict("records"),
            columns=[{"id": c, "name": c} for c in df.columns],
            sort_action="native",
            sort_mode="single",
            row_selectable="multi",
            # column_selectable="single",
            page_action="native",
            page_current=0,
            page_size=20,
            filter_action="native",
        ),
    )

    if len(df.index) == 0:
        return None, fig

    data_col = [col for col in df.keys() if "DATA" in col and not "ERR" in col]
    en_col = [col for col in df.keys() if "EN" in col and not "ERR" in col]
    ang_col = [col for col in df.keys() if "ANG" in col and not "ERR" in col]

    if data_col and en_col:
        fig.add_trace(
            go.Scatter(
                x=df[en_col[0]],
                y=df[data_col[0]],
            )
        )
        fig.update_layout(xaxis={"title": en_col[0]}, yaxis={"title": data_col[0]})

    if data_col and ang_col:
        fig.add_trace(
            go.Scatter(
                x=df[ang_col[0]],
                y=df[data_col[0]],
            )
        )
        fig.update_layout(xaxis={"title": ang_col[0]}, yaxis={"title": data_col[0]})

    return table, fig


@callback(
    Output("download-dataframe-csv", "data"),
    Input("btn_csv", "n_clicks"),
    State("data-column", "data"),
    prevent_initial_call=True,
)
def func(n_clicks, data):
    df = pd.DataFrame.from_dict(data)
    return dcc.send_data_frame(df.to_csv, "data.csv")


# if __name__ == "__main__":
#     app.run_server(use_reloader=True)
#     # app.run_server(debug=True, use_reloader=True)
