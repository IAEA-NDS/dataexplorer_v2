####################################################################
#
# This file is part of libraries-2023 dataexplorer, https://nds.iaea.org/dataexplorer/.
# Copyright (C) 2022 International Atomic Energy Agency (IAEA)
#
# Contact:    nds.contact-point@iaea.org
#
####################################################################

import plotly.graph_objects as go
from dash import dcc


def default_axis(mt):
    if mt in [
        "001",
        "002",
        "018",
        "019",
        "102",
        # "103",
        # "104",
        "201",
        "202",
        "203",
        "204",
        "205",
        "206",
        "207",
        "600",
    ]:  # and not nuclide.endswith("000")
        xaxis_type = "log"
        yaxis_type = "log"

    else:
        xaxis_type = "linear"
        yaxis_type = "linear"

    return xaxis_type, yaxis_type


def default_chart(xaxis_type, yaxis_type, reaction):
    reaction = reaction.split(",")

    fig = go.Figure(
        layout=go.Layout(
            # template="plotly_white",
            xaxis={
                "title": "Incident energy [MeV]",
                "type": xaxis_type,
                "range": [0, 50] if xaxis_type == "linear" else [-8, 1.2],
                # "autorange": True if reaction[0] != "n" else False,
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
        fig.update_xaxes(showexponent="all", exponentformat="E")  # , range=[-8, 2.5])

    if yaxis_type == "log":
        fig.update_yaxes(showexponent="all", exponentformat="E")  # , autorange=True)

    return fig


def update_axis(mt, xaxis_type, yaxis_type, fig):
    if mt in [
        "001",
        "002",
        "018",
        "019",
        "102",
        # "103",
        # "104",
        "201",
        "202",
        "203",
        "204",
        "205",
        "206",
        "207",
        "600",
    ]:
        def_range_x_log = (-8, 2.5)
        def_range_x_lin = (0, 50)

    else:
        def_range_x_log = (0, 3)
        def_range_x_lin = (0, 50)

    if xaxis_type == "linear":
        fig.get("layout").get("xaxis").update(
            {"type": xaxis_type, "showexponent": "none", "range": def_range_x_lin}
        )

    elif xaxis_type == "log":
        fig.get("layout").get("xaxis").update(
            {
                "type": xaxis_type,
                "showexponent": "all",
                "exponentformat": "E",
                "range": def_range_x_log,
            }
        )

    if yaxis_type == "linear":
        fig.get("layout").get("yaxis").update(
            {"type": yaxis_type, "showexponent ": "none", "autorange": True}
        )

    elif yaxis_type == "log":
        fig.get("layout").get("yaxis").update(
            {
                "type": yaxis_type,
                "showexponent": "all",
                "exponentformat": "E",
                "autorange": True,
            }
        )  # "autorange":True})

    return fig
