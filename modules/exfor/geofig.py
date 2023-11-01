####################################################################
#
# This file is part of libraries-2023 dataexplorer, https://nds.iaea.org/dataexplorer/.
# Copyright (C) 2022 International Atomic Energy Agency (IAEA)
#
# Contact:    nds.contact-point@iaea.org
#
####################################################################

import pandas as pd
import numpy as np
import plotly.express as px
from modules.exfor.list import dict3_to_country, get_facility_type, institute_df


def get_reactions_geo(df):
    df["main_facility_institute"] = df["main_facility_institute"].str.replace(
        r"\(|\)", "", regex=True
    )

    df["main_facility_type"] = df["main_facility_type"].str.replace(
        r"\(|\)", "", regex=True
    )
    df["main_facility_country"] = df["main_facility_institute"].str[0:4]
    df["main_facility_country"] = df["main_facility_country"].map(dict3_to_country())
    df["main_facility_type_desc"] = df["main_facility_type"].map(get_facility_type())

    df = pd.merge(
        df,
        institute_df,
        how="left",
        left_on="main_facility_institute",
        right_on="code",
    )

    return df


def geo_fig(grouping, geo_df):
    # reactions_df = get_exfor_bib_table()
    # get entries per facility/type
    entries = geo_df.groupby(["main_facility_institute", "main_facility_type"])[
        "entry"
    ].unique()

    count_df = pd.DataFrame(
        {
            "count": geo_df.groupby(
                [
                    "name",
                    "main_facility_institute",
                    "main_facility_type",
                    "main_facility_type_desc",
                    "main_facility_country",
                    "lat",
                    "lng",
                    # "entries",
                ]
            )["entry"].count()
        }
    ).reset_index()

    if count_df.empty:
        count_df = pd.DataFrame.from_dict(
            {
                "name": ["IAEA"],
                "main_facility_institute": ["International Atomic Energy Agency"],
                "main_facility_type": ["Please try with another criteria"],
                "main_facility_type_desc": [
                    "No data found so you are at the IAEA, Vienna, Austria"
                ],
                "lat": [48.23440327093907],
                "lng": [16.41635769209409],
                "count": [10],
            }
        )
        fig = px.scatter_mapbox(
            data_frame=count_df,
            lat="lat",
            lon="lng",
            hover_data=[
                "name",
                "main_facility_institute",
                "main_facility_type",
                "main_facility_type_desc",
            ],  # "entries"
            size="count",
            zoom=9,
        )

    else:
        # merge list of entries to count_df
        count_df["entries"] = count_df.apply(
            lambda x: entries[x["main_facility_institute"], x["main_facility_type"]],
            axis=1,
        )

        # sort count_df by country name alphabet
        count_df = count_df.sort_values(by=["main_facility_country"])

        # https://plotly.github.io/plotly.py-docs/generated/plotly.express.scatter_mapbox.html
        fig = px.scatter_mapbox(
            data_frame=count_df,
            lat="lat",
            lon="lng",
            hover_data=[
                "name",
                "main_facility_institute",
                "main_facility_type",
                "main_facility_type_desc",
            ],  # "entries"
            color="main_facility_country"
            if grouping == "Country"
            else "main_facility_type_desc",
            size="count",
            size_max=50,
            opacity=0.5,
            center={"lat": 32.827, "lon": 13.3813},
            zoom=1.0,
            height=400,
        )
    # fig.update_traces(cluster=dict(enabled=True))
    fig.update_layout(
        mapbox_style="open-street-map",
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        # title_text="Number of exfor entries per facility/institute",
        # updatemenus=[
        #             dict(
        #                 buttons=list([
        #                     dict(
        #                         args=[{"color": [count_df["main_facility_country"]]}],
        #                         label="Country",
        #                         method="update"
        #                     ),
        #                     dict(
        #                         args=[{"color": [count_df["main_facility_type"]]}],
        #                         label="Facility Type",
        #                         method="update"
        #                     )
        #                 ]),
        #                 direction="down",
        #                 pad={"r": 10, "t": 10},
        #                 showactive=True,
        #                 x=0.1,
        #                 xanchor="left",
        #                 y=1.1,
        #                 yanchor="top"
        #             ),
        #         ],
        # annotations=[
        #         dict(text="Group by:", showarrow=False,
        #         x=0, y=1.085, yref="paper", align="left")
        #         ]
    )

    return fig
