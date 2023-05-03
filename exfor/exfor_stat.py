import dash_bootstrap_components as dbc
from dash import dcc, html
from dash import html, dcc, callback, Input, dash_table, Output

from exfor.cytoscape import *
from exfor.geo import geo_fig
from exfor.aggrid import aggrid_layout
from exfor.year import year_fig
from common import exfor_navbar, footer


stat_right_layout = dbc.Container(
    id="stat_figures",
    children=[
        exfor_navbar,
        # taxonomy
        html.Hr(style={"border": "3px", "border-top": "1px solid"}),
        html.Label("EXFOR Taxonomy"),
        dbc.Row(cyto_layout),
        
        # year counts
        html.Hr(style={"border": "3px", "border-top": "1px solid"}),
        html.Label("Entries by publication year"),
        dbc.Row(dcc.Graph(figure=year_fig)),

        # geo
        html.Hr(style={"border": "3px", "border-top": "1px solid"}),
        html.Label("Nuclear Reaction Experimental Facilities (From EXFOR BIB)"),
        dbc.Row(dcc.Graph(id="geo_map", figure=geo_fig)),

        # counts
        html.Hr(style={"border": "3px", "border-top": "1px solid"}),
        html.Label("Reaction Indexes (From EXFOR SUBENT)"),
        dbc.Row(aggrid_layout),
        footer,

        html.Div(id="test"),
    ],
    fluid=True,
)

