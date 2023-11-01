####################################################################
#
# This file is part of libraries-2023 dataexplorer, https://nds.iaea.org/dataexplorer/.
# Copyright (C) 2022 International Atomic Energy Agency (IAEA)
#
# Contact:    nds.contact-point@iaea.org
#
####################################################################

import dash_ag_grid as dag

########### AGGRID tables
defaultFilterParams = {
    "filterOptions": ["contains"],
    "defaultOption": "contains",
    "trimInput": True,
    # "debounceMs": 1000,
}


columnDefs = [
    # {
    #     "headerName": "",
    #     "cellRenderer": "DeleteButton",
    #     "lockPosition":'left',
    #     "maxWidth":35,
    #     "filter": False,
    #     'cellStyle': {'paddingRight': 0, 'paddingLeft': 0},
    # },
    {
        "headerName": "Author",
        "field": "author",
        "type": "rightAligned",
        "filter": "agTextColumnFilter",
        "filterParams": defaultFilterParams,
        "checkboxSelection": True,
        "headerCheckboxSelection": True,
    },
    {
        "headerName": "Year",
        "field": "year",
        "type": "rightAligned",
        "filter": "agNumberColumnFilter",
    },
    {
        "headerName": "Entry Id",
        "field": "entry_id_link",
        "type": "rightAligned",
        "filter": "agTextColumnFilter",
        "filterParams": defaultFilterParams,
        # "cellStyle": {"color": "blue", "text-decoration": "underline"},
        "cellRenderer": "markdown",
    },
    {
        "headerName": "#Entry",
        "field": "entry_id",
        "type": "rightAligned",
        "filter": "agTextColumnFilter",
        "filterParams": defaultFilterParams,
        # "cellStyle": {"color": "blue", "text-decoration": "underline"},
        "cellRenderer": "markdown",
        "hide": True,
    },
    {
        "headerName": "Points",
        "field": "points",
        "type": "rightAligned",
        "filter": "agNumberColumnFilter",
    },
    {
        "headerName": "E_min [MeV]",
        "field": "e_inc_min",
        "type": "rightAligned",
        "filter": "agNumberColumnFilter",
        "valueFormatter": {"function": "d3.format('(.3e')(params.value)"},
    },
    {
        "headerName": "E_max [MeV]",
        "field": "e_inc_max",
        "type": "rightAligned",
        "filter": "agNumberColumnFilter",
        "valueFormatter": {"function": "d3.format('(.3e')(params.value)"},
    },
    {
        "headerName": "EXFOR Reaction Code",
        "field": "x4_code",
        "type": "rightAligned",
        "filter": "agTextColumnFilter",
        "filterParams": defaultFilterParams,
    },
    # {
    #     "headerName": "SF8",
    #     "field": "sf8",
    #     "type": "rightAligned",
    #     "filter": "agTextColumnFilter",
    # },
    {
        "headerName": "Scale data",
        "field": "scale",
        "type": "rightAligned",
        "filter": "agTextColumnFilter",
        "editable": True,
    },
]


defaultColDef = {
    "resizable": True,
    "sortable": True,
    "filter": True,
}


columnSizeOptions = {
    "defaultMinWidth": 100,
    "columnLimits": [
        {"key": "author", "minWidth": 200},
        {"key": "entry_id", "minWidth": 100},
        {"key": "x4_code", "minWidth": 300},
        {"key": "year", "maxWidth": 80},
        # {"key": "sf8", "maxWidth": 80},
        {"key": "points", "maxWidth": 80},
    ],
}


def index_table_ag(pageparam):
    return dag.AgGrid(
        id="index_table_" + pageparam,
        # enableEnterpriseModules=False,
        columnDefs=columnDefs,
        # rowData=df.to_dict("records"),
        defaultColDef=defaultColDef,
        columnSize="responsiveSizeToFit",
        columnSizeOptions=columnSizeOptions,
        dashGridOptions={
            "rowSelection": "multiple",
            "rowMultiSelectWithClick": True,
            # "pagination": True,
            # "paginationPageSize": 100,
            # "paginationAutoPageSize": True,
        },
        style={"height": 400, "width": "100%"},
        className="ag-theme-balham",  ## Themes: ag-theme-alpine, ag-theme-alpine-dark, ag-theme-balham, ag-theme-balham-dark, ag-theme-material, and ag-bootstrap.
        persistence=False,
        getRowId="params.data.entry_id",
        # persisted_props=["filterModel"],
    )
