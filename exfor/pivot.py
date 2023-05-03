import pandas as pd

from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State
import dash_pivottable
from config import engines

app = Dash(__name__)


def _load_bib():
    connection = engines["exfor"].connect()
    df = pd.read_sql_table("exfor_reactions", connection)
    return df


df = _load_bib()
print(df[20:100].values.tolist())


app.layout = html.Div(
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


if __name__ == "__main__":
    app.run_server(debug=True)
