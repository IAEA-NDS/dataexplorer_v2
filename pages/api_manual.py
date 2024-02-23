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
from pages_common import footer, libs_navbar

dash.register_page(__name__, path="/api_manual")


layout = dbc.Container(
    [
        # libs_navbar,
        # html.Hr(style={"border": "3px", "border-top": "1px solid"}),
        dcc.Markdown(
            """
### [Nuclear Reactions REST API Documentation](#reactions)

The REACTIONS REST API is built using Flask and provides access to the nuclear reaction dataset extracted from the Experimental Nuclear Reaction Database (EXFOR) using EXFOR_parser. The API endpoints are designed to retrieve data tables of specific nuclear reactions. This document outlines the available endpoints and their functionalities.

#### Overview

The REACTIONS REST API provides access to information about reactions, including cross section searches, fission yields, and reaction products. 

- **Base URL:** `https://nds.iaea.org/dataexplorer/api/reactions/`

#### Endpoints

##### 1. Home

- **Endpoint:** `/`
- **Method:** `GET`
- **Description:** Get information about the REACTIONS REST API.
- **Example:**
```bash
curl https://nds.iaea.org/dataexplorer/api/reactions/
```
- **Response:**
```json
{
    "message": "This is REACTIONS REST API"
}
```

##### 2. Search

- **Endpoint:** `/<type>`
- **Method:** `GET`
- **Description:** Search for reactions based on the specified type.
- **Parameters:**
  - `type` (path parameter): Type of observable (e.g., `xs` for cross section, `fy` for fission yield, `rp` for residual production cross section, `th` for thermal neutron capture cross section).
  - `page` (query parameter): Page number for pagination (default is 1).
  - `table` (query parameter, boolean): Data table request (default is False)
  - `eval` (query parameter, boolean): Evaluated nuclear reaction libraries data request (default is False)
  - Additional parameters based on the type of reaction (refer to examples).
- **Examples:**
  - Cross Section Search:
      ```bash
      curl https://nds.iaea.org/dataexplorer/api/reactions/xs?target_elem=Al&target_mass=27&reaction=n%2Cp&&table=True&eval=True&page=1
      ```
  - Fission Yield Search:
      ```bash
      curl https://nds.iaea.org/dataexplorer/api/reactions/fy?&target_elem=U&target_mass=235&reaction=n,f&fy_type=Cumulative&table=True&eval=True&page=1
  - Residual Products Search:
      ```bash
      curl https://nds.iaea.org/dataexplorer/api/reactions/rp?target_elem=Ti&target_mass=0&inc_pt=A&rp_elem=Cr&rp_mass=51&page=1
      ```
- **Response:**
  ```json
{
    "hits": 10,
    "aggregations": { /* Aggregated data based on the search criteria */ },
    "libraries": { /* Information about libraries */ },
}
  ```

#### Notes

- For detailed information on available parameters and usage, refer to the examples provided.
- Ensure that the appropriate parameters are included based on the type of reaction being searched.
- Pagination is supported using the `page` parameter.

This documentation provides a basic overview of the REACTIONS REST API. For more details and specific use cases, refer to the examples and consult with the API developer.




### [EXFOR Viewer REST API Documentation](#exfor)

The EXFOR Viewer REST API is built using Flask and provides access to the EXFOR nuclear reaction database. The API endpoints are designed to retrieve specific information related to nuclear reactions stored in the EXFOR format such as experimental conditions, data tables, bibliography, etc. The API allows users to retrieve information related to an EXFOR entry or subentry by specifying the entry number and subentry number.


#### Overview

The EXFOR Viewer REST API provides access to JSON converted EXFOR entries and the entities defined in the EXFOR dictionary. 

- **Base URL:** `https://nds.iaea.org/dataexplorer/api/exfor/`

#### EXFOR Viewer API Endpoints:

##### GET `/exfor/`

This endpoint returns a message indicating that this is the EXFOR REST API.

- **Endpoint:** `/`
- **Method:** `GET`
- **Description:** Get information about the REACTIONS REST API.
- **Example:**
```bash
curl https://nds.iaea.org/dataexplorer/api/exfor/
```
- **Response:**
```json
{
    "message": "This is EXFOR REST API"
}
```


##### GET `/exfor/<string:div>`

This endpoint returns a JSON object containing the relevant data for the specified category. The valid values for `<string:div>` are "entry", "subentry", and "dict". 

- **Endpoint:** `/<type>`
- **Method:** `GET`
- **Description:** Search for reactions based on the specified type.
- **Parameters:**
  - `entry`: Returns a specific entry in JSON format.
  - `subentry`: Returns a specific sub-entry in JSON format.
  - `dict`: Returns definition of the EXFOR keywords defined in the EXFOR dictionary.

###### GET `/api/exfor/entry/<string:entnum>`

This endpoint returns a JSON object of EXFOR entry. The `<string:entnum>` parameter should be a 5-digit string.

- **Example:**
```bash
- curl https://nds.iaea.org/dataexplorer/api//exfor/entry/10300
```
- **Response:**
```json
{
    "entry": "10300",
    "bib_record": { ... },
    "reactions": { ... },
    "histories": { ... },
    "data_tables": { ... },
    "experimental_conditions": { ... }
}
```

###### GET `/api/exfor/entry/<string:entnum>/<string:section>`

This endpoint returns a JSON object containing the specified section of the data for the specified EXFOR entry number. The `<string:section>` parameter should be one of "reactions", "bib", "histories", "data", or "experiment". If an invalid length is provided for `<string:entnum>`, an error message is returned. 

- **Example:**
```bash
curl https://nds.iaea.org/dataexplorer/api/exfor/entry/10300/data
```
- **Response:**
```json
{
    "data_tables": {
        "001": { ... },
        "002": { ... },
        ...
    }
}
```


###### GET `/api/exfor/subentry/<string:entnum>/<string:subent>`

This endpoint returns a JSON object containing the data for the specified subentry of the specified EXFOR entry number. The `<string:entnum>` parameter should be a 5-digit string, and the `<string:subent>` parameter should be a 3-digit string. If an invalid length is provided for either parameter, an error message is returned.

- **Example:**
```bash
curl https://nds.iaea.org/dataexplorer/api/exfor/subentry/10300/001
```

- **Response:**
```json
{
    "entry": "10300001",
    "experimental_conditions": { ... },
    "data_tables": {

 ... }
}
```


###### GET `/api/exfor/dict/<string:field>`

This endpoint returns a JSON object containing the list of the EXFOR keywords. The valid values for `<string:field>` are "facility", "institute", "method", and "detector".

- **Endpoint:** `/<field>`
- **Method:** `GET`
- **Description:** Search for the definition of EXFOR keywords defined in the EXFOR dictionary.
- **Parameters:**
  - `facility`: Returns a list of facilities in the dictionary.
  - `institute`: Returns a list of institutes in the dictionary.
  - `method`: Returns a list of methods in the dictionary.
  - `detector`: Returns a list of detectors in the dictionary.

- **Example:**
```bash
 GET `/api/exfor/dict/facility`
```
- **Response:**
```json
{
    "1CANALA": "University of Alberta, Edmonton, Alberta",
    "2JPNJAE": "Japan Atomic Energy Agency (JAEA)",
    ...
}
```


###### GET `/api/exfor/dict/<string:field>/<string:keyword>`

This endpoint returns a JSON object containing the definitions of the EXFOR keywords. If the keyword searched is obsolete, "active" returns "false".

- **Example:**
```bash
 GET `/api/exfor/dict/method/ede`
```

- **Response:**
```json
{
    "active":true,
    "description":"Particle identification by 'E/Delta E' measurement"
}
```

        """,
            link_target="_blank",
        ),
        footer,
    ]
)
