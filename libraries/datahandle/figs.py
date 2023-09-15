####################################################################
#
# This file is part of libraries-2021 dataexplorer, https://nds.iaea.org/dataexplorer/.
# Copyright (C) 2022 International Atomic Energy Agency (IAEA)
#
# Contact:    nds.contact-point@iaea.org
#
####################################################################

import plotly.graph_objects as go
from dash import dcc


main_fig = dcc.Graph(
    id="main_fig",
    config={
        "displayModeBar": True,
        "scrollZoom": True,
        "modeBarButtonsToAdd": ["drawline", "drawopenpath", "eraseshape"],
        "modeBarButtonsToRemove": ["lasso2d"],
    },
    figure={
        "layout": {
            "title": "Please select target and reaction.",
            "height": 600,
        }
    },
)


def default_axis(mt):
    if mt in [
        "001",
        "002",
        "018",
        "019",
        "102",
        "201",
        "202",
        "203",
        "204",
        "205",
        "206",
        "207",
    ]:  # and not nuclide.endswith("000")
        xaxis_type = "log"
        yaxis_type = "log"

    else:
        xaxis_type = "linear"
        yaxis_type = "linear"

    return xaxis_type, yaxis_type

def default_chart(xaxis_type, yaxis_type, reaction, mt):
    reaction = reaction.split(",")

    fig = go.Figure(
        layout = go.Layout(
            # template="plotly_white",
            xaxis={
                "title": "Incident energy [MeV]",
                "type": xaxis_type,
                "autorange": True,
                "rangeslider": {
                    "bgcolor": "White",
                    "visible": True,
                    "autorange": True,
                    "thickness": 0.2,
                },
            },
            yaxis={
                "title": "Cross section [barn]",
                "type": yaxis_type,
                "fixedrange": False,
            },
            margin={"l": 40, "b": 40, "t": 30, "r": 0},
        )
    )

    # Expornential format
    if xaxis_type == "log":
        fig.update_xaxes(exponentformat="power")

    if yaxis_type == "log":
        fig.update_yaxes(exponentformat="power")

    return fig

    # elif (
    #     mt
    #     in [
    #         "001",
    #         "002",
    #         "018",
    #         "019",
    #         "102",
    #         "103",
    #         "201",
    #         "202",
    #         "203",
    #         "204",
    #         "205",
    #         "206",
    #         "207",
    #         "rp",
    #     ]
    #     and reaction[0] == "n"
    # ):
    #     #  and not nuclide.endswith("000")
    #     fig = go.Figure(
    #         layout=go.Layout(
    #             xaxis={
    #                 "title": "Incident energy [MeV]",
    #                 "type": xaxis_type,
    #                 "rangeslider": {
    #                     "bgcolor": "White",
    #                     "autorange": True,
    #                     "thickness": 0.15,
    #                 },
    #             },
    #             yaxis={
    #                 "title": "Cross section [barn]",
    #                 "type": yaxis_type,
    #                 "fixedrange": False,
    #             },
    #             margin={"l": 40, "b": 40, "t": 30, "r": 0},
    #         )
    #     )

    # elif any(str(i).zfill(3) in mt for i in range(50, 90)):
    #     #  and not nuclide.endswith("000")
    #     fig = go.Figure(
    #         layout=go.Layout(
    #             xaxis={
    #                 "title": "Incident energy [MeV]",
    #                 "type": xaxis_type,
    #                 "range": [0, 20] if xaxis_type == "linear" else [5.0, 6.5],
    #                 "rangeslider": {
    #                     "bgcolor": "White",
    #                     "autorange": True,
    #                     "thickness": 0.15,
    #                 },
    #             },
    #             yaxis={
    #                 "title": "Cross section [barn]",
    #                 "type": yaxis_type,
    #                 "fixedrange": False,
    #             },
    #             margin={"l": 40, "b": 40, "t": 30, "r": 0},
    #         )
    #     )

    # elif mt in ["016", "017", "037"] and reaction[0] == "n":
    #     #  and not nuclide.endswith("000")
    #     fig = go.Figure(
    #         layout=go.Layout(
    #             xaxis={
    #                 "title": "Incident energy [MeV]",
    #                 "type": xaxis_type,
    #                 "range": [1000000, 50000000]
    #                 if xaxis_type == "linear"
    #                 else [6.1, 7.5],
    #                 "rangeslider": {
    #                     "bgcolor": "White",
    #                     "autorange": True,
    #                     "thickness": 0.15,
    #                 },
    #             },
    #             yaxis={
    #                 "title": "Cross section [barn]",
    #                 "type": yaxis_type,
    #                 "fixedrange": False,
    #             },
    #             margin={"l": 40, "b": 40, "t": 30, "r": 0},
    #         )
    #     )

    # else:
    #     fig = go.Figure(
    #         layout=go.Layout(
    #             # template="plotly_white",
    #             xaxis={
    #                 "title": "Incident energy [MeV]",
    #                 "type": xaxis_type,
    #                 "autorange": True,
    #             },
    #             yaxis={
    #                 "title": "Cross section [barn]",
    #                 "type": yaxis_type,
    #             },
    #             margin={"l": 40, "b": 40, "t": 30, "r": 0},
    #         )
    #     )
