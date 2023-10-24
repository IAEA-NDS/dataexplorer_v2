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
from dash import dcc, html
import dash_bootstrap_components as dbc
from common import footer, libs_navbar

dash.register_page(__name__, path="/api_manual")


layout = dbc.Container(
    [
        libs_navbar,
        html.Hr(style={"border": "3px", "border-top": "1px solid"}),
        dcc.Markdown(
            """
### REST API Manual

This REST API is built using Flask and provides access to the EXFOR nuclear reaction database. The API endpoints are designed to retrieve specific information related to nuclear reactions such as experimental conditions, data tables, bibliography, etc. The API provides access to various dictionaries such as facility, method, detector, and institute. The API allows users to retrieve information related to an EXFOR entry or subentry by specifying the entry number and subentry number.

Base URL: `http://nds.iaea.org/dataexplorer/api/`

#### API endpoints:

##### GET `/exfor/`

This endpoint returns a message indicating that this is the EXFOR REST API.

Example response:

    {
        "message": "This is EXFOR REST API"
    }

##### GET `/exfor/<string:div>`

This endpoint returns a JSON object containing the relevant data for the specified category. The valid values for <string:div> are "entry", "facility", "institute", "method", and "detector". If <string:div> is "entry", a message is returned indicating that the user should specify an entry number.

* Path Parameters

div: A string indicating the division to access.

Available options:
- entry: Returns instructions for how to access a specific entry number in the database.
- facility: Returns a list of facilities in the database.
- institute: Returns a list of institutes in the database.
- method: Returns a list of methods in the database.
- detector: Returns a list of detectors in the database.


Example requests and responses:

 GET `/api/exfor/facility`

    {
        "1CANALA": "University of Alberta, Edmonton, Alberta",
        "2JPNJAE": "Japan Atomic Energy Agency (JAEA)",
        ...
    }

 GET `/exfor/method`

    {
        "ACTIV": "Activation",
        "EDE": "Particle identification by 'E/Delta E' measurement",
        ...
    }

 GET `/exfor/entry`

    {
        "message": "specify the entry number such as /api/exfor/10300"
    }


##### GET `/api/exfor/entry/<string:entnum>`

This endpoint returns a JSON object containing the data for the specified EXFOR entry number. The <string:entnum> parameter should be a 5-digit string. If an invalid length is provided, an error message is returned.

Example request and response:

bash

GET `/api/exfor/entry/10300`

    {
        "entry": "10300",
        "bib_record": {
            ...
        },
        "reactions": {
            ...
        },
        "histories": {
            ...
        },
        "data_tables": {
            ...
        },
        "experimental_conditions": {
            ...
        }
    }

##### GET `/api/exfor/entry/<string:entnum>/<string:section>`

This endpoint returns a JSON object containing the specified section of the data for the specified EXFOR entry number. The <string:entnum> parameter should be a 5-digit string, and the <string:section> parameter should be one of "reactions", "bib", "histories", "data", or "experiment". If an invalid length is provided for <string:entnum>, an error message is returned. If an invalid section is provided, an error message is returned.

Example request and response:

GET `/api/exfor/entry/10300/data`

    {
        "data_tables": {
            "001": {
                ...
            },
            "002": {
                ...
            },
            ...
        }
    }

    
GET `/api/exfor/subentry/<string:entnum>/<string:subent>`

This endpoint returns a JSON object containing the data for the specified subentry of the specified EXFOR entry number. The <string:entnum> parameter should be a 5-digit string, and the <string:subent> parameter should be a 3-digit string. If an invalid length is provided for either parameter, an error message is returned.

Example request and response:

GET `/api/exfor/subentry/10300/001`

    {
        "entry": "10300001",
        "experimental_conditions": {
            ...
        },
        "data_tables": {
            ...
        }
    }


"""
        ),
        footer,
    ]
)
