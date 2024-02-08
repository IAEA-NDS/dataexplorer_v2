####################################################################
#
# This file is part of libraries-2023 dataexplorer,
# https://nds.iaea.org/dataexplorer/.
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

columnDefsDefault = [
    {
        "headerName": "Entry Id",
        "field": "entry_id_link",
        "type": "rightAligned",
        "filter": "agTextColumnFilter",
        "filterParams": defaultFilterParams,
        # "cellStyle": {"color": "blue", "text-decoration": "underline"},
        "cellRenderer": "markdown",
        "checkboxSelection": True,
        "headerCheckboxSelection": True,
    },
    {
        "headerName": "#Entry",
        "field": "entry_id",
        "type": "rightAligned",
        "filter": "agTextColumnFilter",
        "filterParams": defaultFilterParams,
        # "cellStyle": {"color": "blue", "text-decoration": "underline"},
        "cellRenderer": "markdown",
        "linkTarget": "_blank",
        "hide": True,
    },
    {
        "headerName": "Author",
        "field": "author",
        "type": "rightAligned",
        "filter": "agTextColumnFilter",
        "filterParams": defaultFilterParams,
    },
    {
        "headerName": "Year",
        "field": "year",
        "type": "rightAligned",
        "filter": "agNumberColumnFilter",
    },
]


columnDefs_thermal = [
    {
        "headerName": "SF4",
        "field": "sf4",
        "type": "rightAligned",
        "filter": "agNumberColumnFilter",
    },
    {
        "headerName": "SF8",
        "field": "sf8",
        "type": "rightAligned",
        "filter": "agNumberColumnFilter",
    },
    {
        "headerName": "SF9",
        "field": "sf9",
        "type": "rightAligned",
        "filter": "agNumberColumnFilter",
    },
    {
        "headerName": "Energy [MeV]",
        "field": "en_inc",
        "type": "rightAligned",
        "filter": "agNumberColumnFilter",
        "valueFormatter": {"function": "d3.format('(.4e')(params.value)"},
    },
    {
        "headerName": "dEnergy [MeV]",
        "field": "den_inc",
        "type": "rightAligned",
        "filter": "agNumberColumnFilter",
        "valueFormatter": {"function": "d3.format('(.4e')(params.value)"},
    },
    {
        "headerName": "Data",
        "field": "data",
        "type": "rightAligned",
        "filter": "agNumberColumnFilter",
        "valueFormatter": {"function": "d3.format('(.4e')(params.value)"},
    },
    {
        "headerName": "dData",
        "field": "ddata",
        "type": "rightAligned",
        "filter": "agNumberColumnFilter",
        "valueFormatter": {"function": "d3.format('(.4e')(params.value)"},
    },
]


defaultColDef = {
    "flex": 1,
    "width": 30,
    # "floatingFilter": True,
    "resizable": True,
    "sortable": True,
    "filter": True,
}


columnSizeOptions = {
    "defaultMinWidth": 100,
    "columnLimits": [
        {"key": "author", "minWidth": 100},
        {"key": "entry_id", "minWidth": 100},
        {"key": "year", "maxWidth": 80},
    ],
}


thermal_data_table_ag = dag.AgGrid(
    id="thermal_data_table",
    columnDefs=columnDefsDefault + columnDefs_thermal,
    defaultColDef=defaultColDef,
    columnSize="responsiveSizeToFit",
    # columnSizeOptions=columnSizeOptions,
    dashGridOptions={
        "rowSelection": "multiple",
        "rowMultiSelectWithClick": True,
        # "pagination": True,
        # "paginationPageSize": 100
    },
    className="ag-theme-balham",  ## Themes: ag-theme-alpine, ag-theme-alpine-dark, ag-theme-balham, ag-theme-balham-dark, ag-theme-material, and ag-bootstrap.
    persistence=True,
    persisted_props=["filterModel"],
)
