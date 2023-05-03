import json
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html, callback, Input, Output, State, no_update

# from dash import Dash
from exfor.datahandle.list import country_dict, facilities_dict, institute_df, bib_df



def geosummary(bib_df):
    bib_df["main_facility_institute"] = bib_df["main_facility_institute"].str.replace(
        r"\(|\)", ""
    , regex=True)
    bib_df["main_facility_type"] = bib_df["main_facility_type"].str.replace(
        r"\(|\)", ""
    , regex=True)
    bib_df["main_facility_country"] = bib_df["main_facility_institute"].str[0:4]
    bib_df["main_facility_country"] = bib_df["main_facility_country"].map(country_dict)
    bib_df["main_facility_type"] = bib_df["main_facility_type"].map(facilities_dict)
    bib_df = pd.merge(
        bib_df,
        institute_df,
        how="inner",
        left_on="main_facility_institute",
        right_on="code",
    )

    # get entries per facility/type
    entries = bib_df.groupby(["main_facility_institute", "main_facility_type"])[
        "entry"
    ].unique()

    count_df = pd.DataFrame(
        {
            "count": bib_df.groupby(
                [
                    "name",
                    "main_facility_institute",
                    "main_facility_type",
                    "main_facility_country",
                    "lat",
                    "lng",
                    # "entries",
                ]
            )["entry"].count()
        }
    ).reset_index()

    # merge list of entries to count_df
    count_df["entries"] = count_df.apply(
        lambda x: entries[x["main_facility_institute"], x["main_facility_type"]], axis=1
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
        ],  # "entries"
        color="main_facility_country",
        size="count",
        size_max=50,
        opacity=0.5,
        center={"lat": 32.827, "lon": 13.3813},
        zoom=1.0,
        height=400,
    )
    # fig.update_traces(cluster=dict(enabled=True))
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    fig.update_layout(title_text="Number of exfor entries per facility/institute")

    return fig


geo_fig = geosummary(bib_df)




@callback(
        Output('test', 'children'),
        Input('geo_map', 'clickData')
        )
def select_nodes(selected_data):
    # print('Callback select_nodes: ', selected_data)

    if not selected_data:
        return 'hello'
    else:
        return json.dumps(selected_data, indent=2)








# if __name__ == "__main__":
#     app.run_server(debug=True)
