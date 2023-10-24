import pandas as pd

import dash
from dash import html, dcc, callback, Input, dash_table, Output, State
import dash_pivottable
from config import engines

dash.register_page(__name__, path="/exfor/index")


def _load_bib():
    connection = engines["exfor"].connect()
    df = pd.read_sql_table("exfor_reactions", connection)
    return df


df = _load_bib()


## dash pivot version
layout = html.Div(
    [
        html.P("pivot"),
        dash_pivottable.PivotTable(
            data=[df.columns.values.tolist()] + df.values.tolist(),
            # cols=["target", "process", "product","sf6"],
            # rows=["target", "process", "product","sf6"],
            # vals=["entry"]
        ),
    ]
)
