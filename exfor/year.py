import plotly.express as px
import pandas as pd

from .geo import bib_df


def yearsummary():
    count_df = pd.DataFrame(
        {
            "count": bib_df.groupby(
                [
                    "year",
                    # "entries",
                ]
            )["entry"].count()
        }
    ).reset_index()
    # print(count_df)

    # https://plotly.github.io/plotly.py-docs/generated/plotly.express.scatter_mapbox.html
    fig = px.bar(count_df, x="year", y="count", height=300)

    return fig


year_fig = yearsummary()
