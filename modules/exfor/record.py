####################################################################
#
# This file is part of libraries-2023 dataexplorer, https://nds.iaea.org/dataexplorer/.
# Copyright (C) 2022 International Atomic Energy Agency (IAEA)
#
# Contact:    nds.contact-point@iaea.org
#
####################################################################

import os
import re
import git
import requests
import pandas as pd
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import dash
from dash import Dash, html, dcc, Input, Output, State, ctx, no_update, callback

from exforparser.tabulated.data_process import data_length_unify
from exfor_dictionary.exfor_dictionary import Diction

D = Diction()


from config import (
    MASTER_GIT_REPO_URL,
    MASTER_GIT_REPO_PATH,
    EXFOR_JSON_GIT_REPO_PATH,
    DATA_DIR,
    API_BASE_URL,
    owner,
    repo,
    api_token,
)
from submodules.common import open_json
from submodules.utilities.util import dict_merge
from pages_common import URL_PATH


# --------------------------------------------------------------- #
#             Record
# --------------------------------------------------------------- #
def get_record(entnum):
    # url = BASE_URL + URL_PATH + "api/exfor/entry/" + entnum
    # r = requests.get("https://int-nds.iaea.org/dataexplorer/api/exfor/entry/11112", timeout=3, verify=False)
    # return r.json()

    ## Going to noSQL in the future and this is a temporal solution
    file = os.path.join(EXFOR_JSON_GIT_REPO_PATH, "json", entnum[:3], entnum + ".json")

    if os.path.exists(file):
        return open_json(file)

    else:
        return entry_json_dummy


def get_git_history(entnum):
    # Create a GitPython Repo object for the repository
    repo = git.Repo(MASTER_GIT_REPO_PATH)
    file = f"exforall/{entnum[0:3]}/{entnum}.x4"

    # Run the git log -p command for the file and capture the output
    output = repo.git.execute(["git", "log", "-p", "--", file])

    return output


def get_git_history_api(entnum):
    ## Get commit history from Github REST API
    file = f"exforall/{entnum[0:3]}/{entnum}.x4"
    commits = []
    page = 1

    while True:
        # e.g. https://api.github.com/repos/shinokumura/exfor_master/commits?path=exforall/224/22449.x4&page=1
        url = f"https://api.github.com/repos/{owner}/{repo}/commits?path={file}&page={page}"
        response = requests.get(url, headers={"Authorization": f"Token {api_token}"})
        if response.status_code != 200:
            print(f"Error: {response.status_code} {response.reason}")
            break
        new_commits = response.json()
        if len(new_commits) == 0:
            break
        commits += new_commits
        page += 1

    simple_history = {}

    for n in range(len(commits)):
        commit_dict = {
            "message": commits[n]["commit"]["message"],
            "sha": commits[n]["sha"],
            "html_url": commits[n]["html_url"],
            "api_url": commits[n]["url"],
        }
        simple_history[n] = commit_dict
    print(simple_history)
    return simple_history


def compare_commits_api(entnum, commits):
    # Compare commits from Github REST API
    # https://api.github.com/repos/shinokumura/exfor_master/compare/c6dd95093cedb4be62e2814bb8d80ffccfed2713...0dda483cd04058da0c0dbcd4b72a7b07a42c7f56
    # 2 2005-03-24 c6dd95093cedb4be62e2814bb8d80ffccfed2713
    # Error: File not found in diff
    # 1 2006-06-16 0dda483cd04058da0c0dbcd4b72a7b07a42c7f56
    # Error: File not found in diff
    # 0 2006-07-20 5c5a62f3fe62dccc6542c2618557e77e468885ff
    file = f"exforall/{entnum[0:3]}/{entnum}.x4"

    if len(commits) == 1:
        print(f"Error: File does not have at least 2 commits")
        exit()

    for n in reversed(range(len(commits))):
        nth_sha = commits[n]["sha"]
        nplus1_sha = commits[n - 1]["sha"]

        url = f"https://api.github.com/repos/{owner}/{repo}/compare/{nth_sha}...{nplus1_sha}"
        response = requests.get(url, headers={"Authorization": f"Token {api_token}"})

        if response.status_code != 200:
            print(f"Error: {response.status_code} {response.reason}")
            exit()

        diff = response.json()

        for file_diff in diff["files"]:
            if file_diff["filename"] == file:
                return file_diff["patch"]
        else:
            ## Since earlier Commits contains most of the EXFOR entry and the Github REST API returns only top 300 files
            print("Error: File not found in diff")


entry_json_dummy = {
    "entry": "00000",
    "last_updated": "1900-01-01",
    "number_of_revisions": "0",
    "histories": [
        {"x4_code": "", "free_txt": []},
    ],
    "bib_record": {
        "title": "",
        "authors": [
            {"name": ""},
        ],
        "institutes": [{"x4_code": "", "free_txt": []}],
        "references": [
            {
                "x4_code": "",
                "free_txt": [],
                "publication_year": "1900",
                "doi": None,
                "pointer": "0",
            },
        ],
    },
    "reactions": {
        "000": {
            "0": {
                "x4_code": "",
                "children": [
                    {
                        "code": ["", [""], ""],
                        "type": None,
                        "target": "",
                        "process": "",
                        "sf49": "",
                        "sf4": None,
                        "sf5": None,
                        "sf6": "",
                        "sf7": None,
                        "sf8": "",
                        "sf9": None,
                    }
                ],
                "type": None,
                "free_text": "",
                "pointer": "0",
            }
        },
    },
}


def show_compile_history(entry_json):
    hist_data = []
    for history in entry_json["histories"]:
        hist_data += [
            dbc.Row([dbc.Col(history["x4_code"]), dbc.Col(history["free_txt"])])
        ]
    return hist_data


def generate_json_link(entnum):
    dir = os.path.join(EXFOR_JSON_GIT_REPO_PATH, "json", entnum[0:3])
    file = os.path.join(dir, entnum + ".json")
    dir = os.path.dirname(dir)

    if os.path.exists(file):
        flink = os.path.join(dir.replace(DATA_DIR, ""), os.path.basename(file))
        return f"{URL_PATH}{flink}"
    else:
        return "#"


def show_entry_links(entnum, entry_json):
    # get history from Github REST API
    gitlog_json = get_git_history_api(entnum)
    # print(gitlog_json)

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
                        href=f"{URL_PATH}exfor/entry/{entnum}/histories",
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
                        # href=generate_json_link(entnum),
                        color="success",
                        className="me-1",
                    ),
                ],
                style={"textAlign": "right"},
            )
        ]
    )


def show_entry_bib(entry_json=None):
    if not entry_json:
        entry_json = entry_json_dummy

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
