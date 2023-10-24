####################################################################
#
# This file is part of libraries-2021 dataexplorer, https://nds.iaea.org/dataexplorer/.
# Copyright (C) 2022 International Atomic Energy Agency (IAEA)
#
# Contact:    nds.contact-point@iaea.org
#
# Change logs:
#    First release: 2021-08-20
#    Update libraries: 2022-09-05, JENDL4.0 and TENDL2019 have been replced by JENDL5.0 and TENDL2021
#
####################################################################


import os
import re
import json
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
import dash_daq as daq
from dash.exceptions import PreventUpdate
import pandas as pd
import urllib.parse

from config import DATA_DIR, EXFORTABLES_PY_GIT_REPO_PATH, ENDFTABLES_PATH
from man import manual
from submodules.utilities.elem import ELEMS, elemtoz, elemtoz_nz, ztoelem
from submodules.utilities.mass import mass_range
from submodules.utilities.reaction import convert_partial_reactionstr_to_inl
from submodules.utilities.util import get_number_from_string, get_str_from_string
from libraries.list import reaction_list, resid_mt_range, LIB_LIST_MAX

from submodules.libraries.queries import (
    lib_query,
    lib_xs_data_query,
)
from submodules.exfor.queries import (
    index_query,
    # index_query_fy,
    get_entry_bib,
    # data_query,
)

# ------------------------------------------------------------------------------
# Incident particles
# ------------------------------------------------------------------------------

PARTICLE = ["N", "P", "D", "T", "A", "H", "G"]
PARTICLE_FY = ["N", "0", "P", "D", "T", "A", "H", "G"]


# ------------------------------------------------------------------------------
# Isomeric state
# ------------------------------------------------------------------------------

ISOMERIC = ["", "g", "m", "m2"]


# ------------------------------------------------------------------------------
# Name of libraries used in each app
# ------------------------------------------------------------------------------

URL_PATH = dash.get_relative_path("/")

toast = html.Div(
    [
        dbc.Col(
            # dbc.Button("Tips", id="toast-toggle", color="primary", n_clicks=0,)
            [html.Div(html.P("Tips", id="toast-toggle"))]
        ),
        dbc.Col(
            dbc.Toast(
                [html.Div(manual)],
                id="toast",
                header="Tips for Data Explorer",
                icon="primary",
                dismissable=True,
                is_open=False,
                style={
                    "position": "absolute",
                    "top": 10,
                    "left": 10,
                    "width": 850,
                    "maxWidth": "1000px",
                    "zIndex": 1,
                },
                body_style={"background-color": "white", "font-size": "large"},
            )
        ),
    ]
)


sidehead = dbc.Row(
    [
        dbc.Col(
            html.A(
                [
                    html.Img(src=dash.get_asset_url("logo.png"), height="30px"),
                ],
                href="https://nds.iaea.org",
            )
        ),
        dbc.Col(html.P("Docs")),
        dbc.Col(toast),
        # html.Label("Dataexplorer"),
        html.Br(),
        html.Br(),
    ],
)


page_urls = {
    "Libraries-2023": URL_PATH + "reactions/xs",
    "EXFOR Viewer": URL_PATH + "exfor/search",
}


lib_selections = [
    {
        "label": "Cross Section (XS)",
        "value": "XS",
    },
    {
        "label": "Residual Production XS",
        "value": "RP",
    },
    {
        "label": "Fission Yield (FY)", 
        "value": "FY"},
 
]


lib_page_urls = {
    "XS": URL_PATH + "reactions/xs",
    "RP": URL_PATH + "reactions/residual",
    "FY": URL_PATH + "reactions/fy",
    "DA": URL_PATH + "reactions/da",
    "DE": URL_PATH + "reactions/de",
    "FIS": URL_PATH + "reactions/fission",
}


## based on pageparam
def_inp_values = {
    "XS": {"elem": "Al", "mass": "27", "inc_pt": "N", "reaction": "n,p"},
    "RP":{"elem": "Ti", "mass": "0", "inc_pt": "A", "rp_elem": "Cr", "rp_mass": "51"},
    "FY": {"elem": "U", "mass": "235", "inc_pt": "N", "reaction": "n,f"},
    "DA": {"elem": "Fe", "mass": "56", "inc_pt": "N", "reaction": "n,2n"},
    "DE": {"elem": "Nb", "mass": "93", "inc_pt": "N", "reaction": "n,a"},
    "FIS": {"elem": "U", "mass": "238", "inc_pt": "N", "reaction": "n,2n"},
    "EX": {"elem": None, "mass": None, "inc_pt": None, "reaction": None},
}




navbar = html.Div(
    [
        html.H5(html.B("IAEA Nuclear Reaction Data Explorer")),
        html.P(
            "Nuclear Data Section | International Atomic Energy Agency.",
            style={"font-size": "medium"},
        ),
        html.P(
            "Hello, we will update frequentry.",
            style={"font-size": "smaller", "color": "gray"},
        ),
    ]
)


libs_navbar = html.Div(
    [
        html.H5(html.B("IAEA Nuclear Reaction Data Explorer")),
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        [
                            html.A(
                                [
                                    html.Img(
                                        src=dash.get_asset_url("logo.png"),
                                        height="20px",
                                    ),
                                ],
                                href="https://nds.iaea.org",
                            ),
                            " Libraries 2023",
                        ],
                    ),
                    width=2,
                    style={"font-size": "medium"},
                ),
                dbc.Col(
                    html.Div(
                        [
                            "Buildt with ",
                            html.A(
                                "ENDFTABLES",
                                href="https://nds.iaea.org/talys/",
                                # className="text-dark",
                            ),
                            " and ",
                            html.A(
                                "EXFORTABLES",
                                href="https://github.com/shinokumura/endftables_py",
                                # className="text-dark",
                            ),
                            " by ",
                            html.A(
                                "exforparser",
                                href="https://github.com/shinokumura/exforparser",
                                # className="text-dark",
                            ),
                            ".",
                        ],
                        style={
                            "font-size": "smaller",
                            "color": "gray",
                            "text-align": "left",
                        },
                    ),
                ),
            ]
        ),
    ]
)


exfor_navbar = html.Div(
    [
        html.H5(html.B("IAEA Nuclear Reaction Data Explorer")),
        html.P(
            "Experimental Nuclear Reaction Experimental Data (EXFOR) is compiled by the International Network of Nuclear Reaction Data Centres (NRDC) under the auspices of the International Atomic Energy Agency.",
            style={"font-size": "small"},
        ),
        html.P(
            "Number of entry: 2448, Number of dataset: 123456",
            style={"font-size": "smaller", "color": "gray"},
        ),
    ]
)


footer = html.Div(
    [
        html.Br(),
        html.Hr(style={"border": "3px", "border-top": "1px solid"}),
        "Copyright 2022, International Atomic Energy Agency - ",
        html.A(
            "Nuclear Data Section.", href="https://nds.iaea.org/", className="text-dark"
        ),
        html.Br(),
        html.A(
            "Terms of use.",
            href="https://nucleus.iaea.org/Pages/Others/Terms-Of-Use.aspx",
            className="text-dark",
        ),
        html.Br(),
        "email:",
        html.A(
            "nds.contact-point@iaea.org",
            href="mailto:nds.contact-point@iaea.org",
            className="text-dark",
        ),
        html.Br(),
    ],
    style={"text-align": "center"},
    className="text-dark",
)


def main_fig(pageparam):
    return dcc.Graph(
            id="main_fig_"+pageparam,
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




def input_target(pageparam, **query_strings): 
    # pageparam = pageparam.lower()
    return [html.Label("Observable"),
        dcc.Dropdown(
            id="observable_" + pageparam,
            # options=[{"label": j, "value": i} for i, j in sorted(WEB_CATEGORY.items())],
            options=lib_selections,
            placeholder="Select observable",
            persistence=True,
            persistence_type="memory",
            value=pageparam.upper(),
            style={"font-size": "small", "width": "100%"},
        ),
        html.Label("Target"),
        dcc.Input(
            id="target_elem_" + pageparam,
            placeholder="Target element: C, c, Pd, pd, PD",
            persistence=True,
            persistence_type="memory",
            value=query_strings["target_elem"]
            if query_strings.get("target_elem")
            else def_inp_values[pageparam.upper()]["elem"],
            style={"font-size": "small", "width": "100%"},
        ),
        dcc.Input(
            id="target_mass_" + pageparam,
            placeholder="Target mass: 0:natural, m:metastable",
            persistence=True,
            persistence_type="memory",
            value=query_strings["target_mass"]
            if query_strings.get("target_mass")
            else def_inp_values[pageparam.upper()]["mass"],
            style={"font-size": "small", "width": "100%"},
        )]


def input_general(pageparam, **query_strings): 
    pageparam = pageparam.lower()
    return [html.Label("Reaction"),
        dcc.RadioItems(
            id="incident_particle_" + pageparam,
            options=[{"label": f"{pt.lower()}", "value": pt} for pt in PARTICLE],
            value=query_strings["reaction"][0].upper()
            if query_strings.get("reaction")
            else def_inp_values[pageparam.upper()]["inc_pt"],
            persistence=True,
            persistence_type="memory",
            labelStyle={"display": "inline-block", "margin": "4px"},
        ),
        dcc.Dropdown(
            id="reaction_" + pageparam,
            options=generate_reactions("n"),
            placeholder="Reaction e.g. (n,g)",
            persistence=True,
            persistence_type="memory",
            value=query_strings["reaction"] if query_strings.get("reaction") else def_inp_values[pageparam.upper()]["reaction"],
            style={"font-size": "small", "width": "100%"},
        ),
        dcc.Dropdown(
            id="reac_branch_" + pageparam,
            options=[],
            placeholder="Partial",
            persistence=True,
            persistence_type="memory",
            value=query_strings["branch"] if query_strings.get("branch") else None,
            style={"font-size": "small", "width": "100%"},
        ),
        ]




def exfor_filter_opt(pageparam): 
    pageparam = pageparam.lower()
    return [ 
        html.P("EXFOR Filter Options"),
        html.Label("Energy Range", style={"font-size": "small"}),
        dcc.RangeSlider(
            id="energy_range_" + pageparam,
            min=0,
            max=9,
            marks={0: "eV", 3: "keV", 6: "MeV", 9: "GeV"},
            value=[0, 9],
            vertical=False,
        ),
        # html.Br(),
        html.Label("Year Range", style={"font-size": "small"}),
        dcc.RangeSlider(
            id="year_range_"  + pageparam,
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




def libs_filter_opt(pageparam): 
    pageparam = pageparam.lower()
    return [ html.P("Evaluated Data Options"),
        html.Label("Evaluated Data", style={"font-size": "small"}),
        dcc.Dropdown(
            id="endf_selct_" + pageparam,
            options=LIB_LIST_MAX,
            placeholder="Evaluated files",
            persistence=True,
            persistence_type="memory",
            multi=True,
            value=["endfb8.0", "tendl.2021", "jendl5.0"],
            style={"font-size": "small", "width": "100%"},
        ),
        html.Label("Groupwise data", style={"font-size": "small"}),
        dcc.Dropdown(
            id="endf_gropewise_" + pageparam,
            options=[{"label": "PENDF", "value": "PENDF"}, {"label": "1109", "value": "1109","disabled": True},  {"label": "640", "value": "640", "disabled": True}],
            persistence=True,
            persistence_type="memory",
            value="PENDF",
            style={"font-size": "small", "width": "100%"},
            clearable=False,
        ),
    ]


def reduce_data_switch(pageparam):
    return [  dbc.Row(
            [
                dbc.Col(
                    daq.ToggleSwitch(id="reduce_data_switch_"+pageparam, size=30, value=True),
                    width=3,
                ),
                dbc.Col(
                    html.Div(
                        "Use reduced data points",
                        style={"font-size": "smaller", "color": "gray"},
                    )
                ),
            ]
        )]


def excl_mxw_switch(pageparam):
    return  [  dbc.Row(
            [
                dbc.Col(
                    daq.ToggleSwitch(id="exclude_mxw_switch_"+pageparam, size=30, value=True),
                    width=3,
                ),
                dbc.Col(
                    html.Div(
                        "Exclude non pure data",
                        style={"font-size": "smaller", "color": "gray"},
                    )
                ),
            ]
        ),]




def input_check(type, elem, mass, reaction):
    if not type or not elem or not mass or not reaction:
        # if any(not i for i in (type, elem, mass, reaction)):
        raise PreventUpdate

    if elem.capitalize() not in ELEMS:
        raise PreventUpdate

    if elem.isnumeric():
        elem = ztoelem(elem)

    if not mass:
        raise PreventUpdate

    if elem and mass:
        min = mass_range[elemtoz_nz(elem.capitalize())]["min"]
        max = mass_range[elemtoz_nz(elem.capitalize())]["max"]

        if mass == "0":
            pass

        elif not int(min) < int(get_number_from_string(mass)) < int(max):
            raise PreventUpdate

    else:
        raise PreventUpdate

    return elem.capitalize(), mass.lower(), reaction.lower()



def generate_reactions(proj=None):
    reactions = reaction_list(proj)
    options = [ {"label": f"{proj.lower()},{reac.lower()}", "value": f"{proj.lower()},{reac.lower()}" } for reac in reactions.keys() ]
    return options


def get_mt(reac):
    reactions = reaction_list(reac.split(",")[0].upper())
    return reactions[reac.split(",")[1].upper()]["mt"]



def energy_range_conversion(energy_range):
    if len(energy_range) == 2:
        if energy_range[0] <= 1:
            lower = 0
        else:
            lower = 10 ** energy_range[0] / 1e6

        upper = 10 ** energy_range[1] / 1e6

        return lower, upper

    else:
        return None, None




def remove_query_parameter(url, param):
    # クエリ文字列から指定されたパラメータを削除するユーティリティ関数
    url_parts = urllib.parse.urlparse(url)
    query_params = urllib.parse.parse_qs(url_parts.query)
    query_params.pop(param, None)
    updated_query = urllib.parse.urlencode(query_params, doseq=True)
    return url_parts._replace(query=updated_query).geturl()




def limit_number_of_datapoints(points, df):
    if points <= 100:
        return df

    elif 100 < points <= 1000:
        nskip = int(points / 100)

        return df.iloc[::nskip, :]

    elif 1000 < points <= 5000:
        nskip = int(points / 100)
        return df.iloc[::nskip, :]

    elif points > 5000:
        nskip = int(points / 100)
        return df.iloc[::nskip, :]

    else:
        return df




def open_json(file):
    if os.path.exists(file):
        with open(file) as json_file:
            return json.load(json_file)
    else:
        return None



def get_indexes(input_store):

    type = input_store.get("type").upper()
    elem = input_store.get("target_elem")
    mass = input_store.get("target_mass")
    reaction = input_store.get("reaction")
    mt = input_store.get("mt")

    index_df = pd.DataFrame()
    legends = {} 
    libs = {}

    if type == "XS" or type == "DA" or type == "FY":
        entries = index_query(input_store)
        libs = lib_query(input_store)

        total_points = sum( [ e["points"] for e in entries.values() ] ) if entries else 0
        search_result = html.Div(
                        [html.B(f"Search results for {type} {elem}-{mass}({reaction}), MT={str(int(mt)) if mt else '?'}: "
                            ),\
                        f"Number of EXFOR data: {len(entries)} datasets wtih {total_points if entries else 0} data points. Number of Evaluated Data Libraries: {len(libs) if libs else 0}."
                        ])

    elif type == "RP":
        rp_elem = input_store.get("rp_elem")
        rp_mass = input_store.get("rp_mass")

        entries = index_query(input_store)
        libs = lib_query(input_store)
        #     type,
        #     elem,
        #     mass,
        #     reaction=f"{inc_pt.upper()},X",
        #     mt=None,
        #     rp_elem=rp_elem,
        #     rp_mass=rp_mass,
        # )
        total_points = sum( [ e["points"] for e in entries.values() ] ) if entries else 0
        search_result = html.Div(
            [
                html.B(
                    f"Search results for {type} {elem}-{mass}({reaction})-->{rp_elem}-{rp_mass}: "
                ),
                f"Number of EXFOR data: {len(entries)} datasets wtih {total_points if entries else 0} data points. Number of Evaluated Data Libraries: {len(libs) if libs else 0}.",
            ]
        )

    # elif type == "FY":
    #     entries = index_query(input_store)


    if not entries and not libs:
        return search_result, None, None, None
    
    if entries:
        legends =  get_entry_bib(e[:5] for e in entries.keys())
        legends = {
            t: dict(**i, **v)
            for k, i in legends.items()
            for t, v in entries.items()
            if k == t[:5]
        }

        index_df = pd.DataFrame.from_dict(legends, orient="index").reset_index()
        index_df.rename(columns={"index": "entry_id"}, inplace=True)
        index_df["entry_id_link"] = (
            "[" 
            + index_df["entry_id"] 
            + "](../exfor/entry/" 
            + index_df["entry_id"] 
            + ")"
        )
        legends["total_points"] = total_points
    

    return (
        search_result,
        index_df.to_dict("records"),
        legends,
        libs,
    )




def highlight_data(selected, fig):
    # print("highlight_data")
    
    if not fig or not selected:
        raise PreventUpdate
    
    if selected:
        for record in fig.get("data"):
            record.update({ "marker":{"size": 8} })

            if len(record.get("name").split(",")) > 1:
                legend = re.split(',|\[|\]', record.get("name"))

            else:
                continue

            for s in selected:
                if legend[2].strip() == s['entry_id']:
                    record.update({ "marker":{"size": 15} })

                else:
                    continue
    return fig




def del_rows_fig(selected, fig):
    del_data = []
    
    for r in range( len(fig.get("data")) ):
        # print(r, fig["data"][r])
        if len(fig["data"][r]["name"].split(",")) > 1:
            legend = re.split(',|\[|\]', fig["data"][r]["name"])
        else:
            continue

        for s in selected:
            if legend[2].strip() == s['entry_id']:
                del_data += [r]

    for d in reversed ( del_data ):
        del fig["data"][d]

    return fig, {"remove": selected}



def scale_data(selected, fig):
    ## selected looks as follows
    ##  {'rowIndex': 0, 
    # 'rowId': '0', 
    # 'data': {'entry_id': 'A0181-005-0', 'author': 'S.M.Sahakundu', 'year': 1979, 'e_inc_min': 10.5, 'e_inc_max': 27.6, 'points': 15, 'sf5': None, 'sf8': None, 'x4_code': '(13-AL-27(A,N)15-P-30,,SIG)', 'mt': 4, 'mf': 3, 'entry_id_link': '[A0181-005-0](../exfor/entry/A0181-005-0)', 'scale': '0.8'}, 
    # 'value': '0.8', 
    # 'colId': 'scale', 
    # 'timestamp': 1697111382289}
    if not fig or not selected:
        raise PreventUpdate
    
    if selected:
        for record in fig.get("data"):
        # record looks like this:
        # {'error_x': {'array': [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None], 'type': 'data'}, 'error_y': {'array': [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None], 'type': 'data'}, 'marker': {'size': 8}, 'mode': 'markers', 'name': 'S.M.Sahakundu, 1979 [A0181-005-0]', 'showlegend': True, 'x': [10.5, 11.9, 12, 13.6, 13.8, 15, 16, 16.5, 17.7, 18.1, 20, 21, 22, 23, 27.6], 'y': [0.05, 0.14200000000000002, 0.2, 0.33, 0.34, 0.4, 0.28, 0.27, 0.2, 0.163, 0.105, 0.08600000000000001, 0.081, 0.045, 0.021], 'type': 'scatter'}
            record.update({ "marker":{"size": 8} })

            if len(record.get("name").split(",")) > 1:
                ## 'name': 'S.M.Sahakundu, 1979 [A0181-005-0]'
                legend = re.split(',|\[|\]', record.get("name"))
                
                if legend[2].strip() == selected['data']['entry_id']:
                    record.update({"y": [ y * float(selected["value"]) for y in record["y"]  ] })

    return fig




def filter_by_year_range(year_range, fig):
    if not fig or not year_range:
        raise PreventUpdate
    
    if year_range and fig:

        filter_model = {}

        for record in fig.get("data"):
            record.update({"visible": "true"})

            if len(record.get("name").split(",")) > 1:
                legend = re.split(',|\[', record.get("name"))
                # print(record)

                if year_range:
                    if not year_range[0] < int(legend[1].strip()) < year_range[1]:
                        record.update({"visible": "legendonly"})

                    if year_range[0] < int(legend[1].strip()) < year_range[1]:
                        record.update({"visible": "true"})

                    filter_model = {
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

    return fig, filter_model




def fileter_by_en_range(energy_range, fig):
    # print(json.dumps(fig, indent=1))
    filter_model = {}
    if energy_range and fig:
        for record in fig.get("data"):
            record.update({"visible": "true"})
            if len(record.get("name").split(",")) > 1:
                if energy_range:
                    ## get the average energy of the dataset
                    sum_x = sum([float(x) for x in record["x"] if x is not None])
                    lower, upper = energy_range_conversion(energy_range)

                    if not lower < sum_x / len(record["x"]) < upper:
                        record.update({"visible": "legendonly"})

                    elif lower < sum_x / len(record["x"]) < upper:
                        record.update({"visible": "true"})

                    filter_model = {
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

    return fig, filter_model




def export_index(onlySelected, input_store):

    type = input_store.get("type").upper()
    elem = input_store.get("target_elem")
    mass = input_store.get("target_mass")
    reaction = input_store.get("reaction")
    mt = input_store.get("mt")

    if mt:
        filename = f"{elem}{mass}-{reaction}-{type}-MT{mt}-exfortables-index.csv"
    else:
        filename = f"{elem}{mass}-{reaction}-{type}-exfortables-index.csv"

    return True, {"columnKeys": ["author", "year", "entry_id", "e_inc_min", "e_inc_max", "points", "x4_code"], 
                    "fileName": filename, 
                    "allColumns": True,
                    "onlySelected": onlySelected, 
                    "onlySelectedAllPages": onlySelected
                    }



def export_data(onlySelected, input_store):

    type = input_store.get("type").upper()
    elem = input_store.get("target_elem")
    mass = input_store.get("target_mass")
    reaction = input_store.get("reaction")
    mt = input_store.get("mt")

    if mt:
        filename = f"{elem}{mass}-{reaction}-{type}-MT{mt}-exfortables.csv"
    else:
        filename = f"{elem}{mass}-{reaction}-{type}-exfortables.csv"

    data = {"columnKeys": ["author", "year", "entry_id", "en_inc", "den_inc", "data", "ddata"], 
            "fileName": filename,
            "allColumns": True,
            "onlySelected": onlySelected, 
            "onlySelectedAllPages": onlySelected
            }
    
    if type.upper() == "SIG":
        data["columnKeys"].append(["residual", "level_num"])
    elif type.upper() == "RP":
        data["columnKeys"].append(["residual"])
    elif type.upper() == "FY":
        data["columnKeys"].append(["mass", "charge", "isomer"])
    elif type.upper() == "DA":
        data["columnKeys"].append(["angle", "dangle"])
    elif type.upper() == "FDEY":
        data["columnKeys"].append(["energy", "denergy"])

    return True, data


### for the download files

def generate_exfortables_file_path(input_store):
    type = input_store.get("type").upper()
    elem = input_store.get("target_elem")
    mass = input_store.get("target_mass")
    
    reaction = input_store.get("reaction")
    level_num = input_store.get("level_num")

    target = f"{elem.capitalize()}-{str(int(mass))}"
    exfiles = []
    
    if level_num:
        reaction = convert_partial_reactionstr_to_inl(reaction)
        dir = os.path.join( EXFORTABLES_PY_GIT_REPO_PATH, 
                        reaction.split(",")[0].lower(), 
                        target,
                        reaction.replace(",", "-").lower() + "-L"+str(level_num),
                        type.lower() )

    else:
        dir = os.path.join( EXFORTABLES_PY_GIT_REPO_PATH, 
                        reaction.split(",")[0].lower(), 
                        target, 
                        reaction.replace(",", "-").lower(), 
                        type.lower() if type != "RP" else "xs")
    if type == "RP":
        rp_elem = input_store.get("rp_elem")
        rp_mass = input_store.get("rp_mass")
        residual = f"{rp_elem.capitalize()}-{str(int(rp_mass))}"

        if os.path.exists(dir):
            exfiles = [ f for f in os.listdir(dir)  if residual in f ]

    else:
        if os.path.exists(dir):
            exfiles = os.listdir(dir)

    return list_link_of_files(dir, exfiles)



def generate_endftables_file_path(input_store):
    type = input_store.get("type").upper()
    elem = input_store.get("target_elem")
    mass = input_store.get("target_mass")
    reaction = input_store.get("reaction")
    mt = input_store.get("mt")
    
    target = f"{elem.capitalize()}{str(int(mass)).zfill(3)}"

    libfiles = []
    for lib in LIB_LIST_MAX:
        dir = os.path.join( ENDFTABLES_PATH, 
                        reaction.split(",")[0].lower(), 
                        target,
                        lib,
                        "tables",
                        type.lower() if type != "RP" else "residual"
                        )
        
        if type == "RP":
            rp_elem = input_store.get("rp_elem")
            rp_mass = input_store.get("rp_mass")
            residual = f"rp{ elemtoz(rp_elem.capitalize()).zfill(3)}{str(int(rp_mass)).zfill(3)}.{lib}"
            if os.path.exists(dir):
                libfiles += [ f for f in os.listdir(dir) if residual in f ]

        else:
            if os.path.exists(dir):
                libfiles += [ f for f in os.listdir(dir) if f"MT{mt.zfill(3)}.{lib}" in f ]

    return list_link_of_files(dir, libfiles)



def list_link_of_files(dir, files):

    flinks = []
    for f in sorted(files):
        
        filename = os.path.basename(f)
        # dirname = os.path.dirname(f)
        # linkdir = dirname.replace(DATA_DIR, "")

        fullpath = os.path.join(dir, filename)
        a = html.A(
            filename, href=fullpath, target="_blank"
        )

        flinks.append(a)
        flinks.append(html.Br())

    return flinks






