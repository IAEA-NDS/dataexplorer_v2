import plotly.express as px
import pandas as pd

from exfor.datahandle.queries import get_exfor_bib_table


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
