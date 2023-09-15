####################################################################
#
# This file is part of libraries-2021 dataexplorer, https://nds.iaea.org/dataexplorer/.
# Copyright (C) 2022 International Atomic Energy Agency (IAEA)
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


# Style selection [CERULEAN, COSMO, CYBORG, DARKLY, FLATLY, JOURNAL, LITERA, LUMEN, LUX, MATERIA, MINTY, PULSE, SANDSTONE, SIMPLEX, SKETCHY, SLATE, SOLAR, SPACELAB, SUPERHERO, UNITED, YETI, ZEPHYR]
if DEVENV:
    app = dash.Dash(
        __name__,
        external_stylesheets=[dbc.themes.CERULEAN],
        url_base_pathname="/dataexplorer2/",
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

else:
    app = dash.Dash(
        __name__,
        external_stylesheets=[dbc.themes.JOURNAL],
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
    app.title = "LIBRARIES-2022 Data Explorer"

# print(app.config["url_base_pathname"])

app.layout = html.Div([dash.page_container])


if __name__ == "__main__":
    app.run_server(debug=True, use_reloader=True)
