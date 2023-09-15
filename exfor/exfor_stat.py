import dash_bootstrap_components as dbc
from dash import dcc, html
from dash import html, dcc

# from exfor.cytoscape import *
from exfor.geo import geo_fig
from exfor.aggrid import aggrid_layout
from exfor.year import year_fig
from common import exfor_navbar, footer


stat_right_layout = [
    exfor_navbar,
    # taxonomy
    # html.Hr(style={"border": "3px", "border-top": "1px solid"}),
    # html.Label("EXFOR Taxonomy"),
    # dbc.Row(cyto_layout),
    # geo
    html.Hr(style={"border": "3px", "border-top": "1px solid"}),
    html.Label("Nuclear Reaction Experimental Facilities (Based on EXFOR FACILITY)"),
    # dcc.Loading(
    #     children=dbc.Row(dcc.Graph(id="geo_map", figure=geo_fig())),
    #     type="circle",
    # ),
    # year counts
    html.Hr(style={"border": "3px", "border-top": "1px solid"}),
    html.Label("Number of Nuclear Reaction Measurements (Based on EXFOR REFERENCE)"),
    dcc.Loading(
        children=dbc.Row(dcc.Graph(figure=year_fig())),
        type="circle",
    ),
    # All reaction index
    html.Hr(style={"border": "3px", "border-top": "1px solid"}),
    html.Label("Experimental Nuclear Reaction Indexes (Based on EXFOR REACTION)"),
    # dcc.Loading(
    #     children=dbc.Row(aggrid_layout("all")),
    #     type="circle",
    # ),
    html.Hr(style={"border": "3px", "border-top": "1px solid"}),
    html.Div(id="test"),
    footer,
]
