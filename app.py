####################################################################
#
# This file is part of libraries-2021 dataexplorer, https://nds.iaea.org/dataexplorer/.
# Copyright (C) 2024 International Atomic Energy Agency (IAEA)
#
# Contact:    nds.contact-point@iaea.org
#
# Change logs:
#    First release: 2021-08-20
#    Update libraries: 2022-09-05, JENDL4.0 and TENDL2019 have been replced by JENDL5.0 and TENDL2021
#
####################################################################

import dash
from dash import html
import dash_bootstrap_components as dbc

from config import DEVENV

# see dash API reference: https://dash.plotly.com/reference
# Style selection [CERULEAN, COSMO, CYBORG, DARKLY, FLATLY, JOURNAL, LITERA, LUMEN, LUX, MATERIA, MINTY, PULSE, SANDSTONE, SIMPLEX, SKETCHY, SLATE, SOLAR, SPACELAB, SUPERHERO, UNITED, YETI, ZEPHYR]
if DEVENV:
    app = dash.Dash(
        __name__,
        external_stylesheets=[dbc.themes.CERULEAN],
        url_base_pathname="/dataexplorer2/",
        # routes_pathname_prefix="/",  # if Prod
        # requests_pathname_prefix="/dataexplorer2/",  # if Prod
        suppress_callback_exceptions=True,
        meta_tags=[
            {
                "name": "IAEA Nuclear Data Section",
                "content": "Nuclear Reaction, Nuclear Data, Cross Section, TALYS, TENDL",
            },
            {"http-equiv": "X-UA-Compatible", "content": "IE=edge"},
            {"name": "viewport", "content": "width=device-width, initial-scale=1.0"},
        ],
        use_pages=True,
    )

else:
    app = dash.Dash(
        __name__,
        external_stylesheets=[dbc.themes.CERULEAN],
        # url_base_pathname="/dataexplorer2/",
        routes_pathname_prefix="/",  # if Prod
        requests_pathname_prefix="/dataexplorer2/",  # if Prod
        suppress_callback_exceptions=True,
        meta_tags=[
            {
                "name": "IAEA Nuclear Data Section",
                "content": "Nuclear Reaction data plot, LIBRARIES-2022, TALYS",
            },
            {"http-equiv": "X-UA-Compatible", "content": "IE=edge"},
            {"name": "viewport", "content": "width=device-width, initial-scale=1.0"},
        ],
        use_pages=True,
    )
    server = app.server  # for PROD/INT env

app.title = "IAEA Nuclear Reaction Data Explorer"
app.layout = html.Div([dash.page_container])

if __name__ == "__main__":
    if DEVENV:
        app.run_server(
            host="0.0.0.0", use_reloader=True
        )
        # app.run_server(
        #     host="127.0.0.1", debug=True, dev_tools_prune_errors=False, use_reloader=True
        # )
    else:
        app.run_server(use_reloader=True)
