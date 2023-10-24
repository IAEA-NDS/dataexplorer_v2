####################################################################
#
# This file is part of libraries-2023 dataexplorer, https://nds.iaea.org/dataexplorer/.
# Copyright (C) 2022 International Atomic Energy Agency (IAEA)
#
# Contact:    nds.contact-point@iaea.org
#
####################################################################

import numpy as np
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash import html, dcc
from datetime import date, timedelta
import dateutil.relativedelta

from exfor.geofig import reactions_df, geo_fig
from exfor.aggrid import aggrid_updated
from exfor.list import ent_update_df
from common import exfor_navbar, footer
from submodules.exfor.queries import (
    entry_query_by_id,
    get_entry_bib,
    get_exfor_bib_table,
    index_query_by_id,
)


def updated_list():
    ## Filter entries by the recently updated
    before = pd.to_datetime("today") - timedelta(days=60)

    df2 = ent_update_df[
        (ent_update_df["last_update"] >= before) & (ent_update_df["num_updates"] == 1)
    ]
    df3 = entry_query_by_id(df2["entry"].to_list())

    df3 = df3.merge(df2)
    df3["entry_id_link"] = "[" + df3["entry"] + "](entry/" + df3["entry"] + ")"
    df3["last_update"] = df3["last_update"].dt.strftime("%Y-%m-%d")
    df3["new"] = np.where(df3["num_updates"] == 1, "New", "Updated")

    return aggrid_updated(df3)


def year_fig():
    count_df = pd.DataFrame(
        {
            "count": get_exfor_bib_table()
            .groupby(
                [
                    "year",
                    # "entries",
                ]
            )["entry"]
            .count()
        }
    ).reset_index()
    # print(count_df)

    # https://plotly.github.io/plotly.py-docs/generated/plotly.express.scatter_mapbox.html
    fig = px.bar(count_df, x="year", y="count", height=300)

    return fig


stat_right_layout = [
    exfor_navbar,
    ## taxonomy
    # html.Hr(style={"border": "3px", "border-top": "1px solid"}),
    # html.Label("EXFOR Taxonomy"),
    # dbc.Row(cyto_layout),
    html.Hr(style={"border": "3px", "border-top": "1px solid"}),
    html.Label("Recently added/updated EXFOR entries"),
    updated_list(),
    ## geo
    html.Hr(style={"border": "3px", "border-top": "1px solid"}),
    html.Label(
        children=[
            "Nuclear Reaction Experimental Facilities (Based on EXFOR FACILITY)  ",
            html.A("GEO Search", href="exfor/geo"),
        ]
    ),
    dcc.Loading(
        children=dbc.Row(
            dcc.Graph(id="geo_map", figure=geo_fig("Country", reactions_df))
        ),
        type="circle",
    ),
    ## year counts
    html.Hr(style={"border": "3px", "border-top": "1px solid"}),
    html.Label("Number of Nuclear Reaction Measurements (Based on EXFOR REFERENCE)"),
    dcc.Loading(
        children=dbc.Row(dcc.Graph(figure=year_fig())),
        type="circle",
    ),
    ## All reaction index
    # html.Hr(style={"border": "3px", "border-top": "1px solid"}),
    # html.Label("Experimental Nuclear Reaction Indexes (Based on EXFOR REACTION)"),
    # dcc.Loading(
    #     children=dbc.Row(aggrid_layout("all")),
    #     type="circle",
    # ),
    html.Hr(style={"border": "3px", "border-top": "1px solid"}),
    # html.Div(id="test"),
    footer,
]
