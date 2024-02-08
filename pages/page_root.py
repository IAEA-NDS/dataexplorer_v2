####################################################################
#
# This file is part of libraries-2021 dataexplorer, https://nds.iaea.org/dataexplorer/.
# Copyright (C) 2024 International Atomic Energy Agency (IAEA)
#
# Contact:    nds.contact-point@iaea.org
#
####################################################################


import dash
from dash import dcc, Input, Output, callback
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate


## Registration of page
dash.register_page(
    __name__,
    path="/",
    title="IAEA Nuclear Dataexplorer",
    description="Nuclear reaction experimental and evaluated data plotter",
)

layout = dcc.Location(id="root_location")


@callback(
    [
        Output("root_location", "href"),
        Output("root_location", "refresh"),
    ],
    Input("root_location", "href"),
)
def redirect_to_xs(loc):
    if loc.rsplit("/", 1)[-1] == "":
        return "reactions/xs", True

    else:
        raise PreventUpdate
