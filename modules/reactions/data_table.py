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
]


columnDefs_xs = [
    {
        "headerName": "Energy [MeV]",
        "field": "en_inc",
        "type": "rightAligned",
        "filter": "agNumberColumnFilter",
        "valueFormatter": {"function": "d3.format('(.3e')(params.value)"},
    },
    {
        "headerName": "dEnergy [MeV]",
        "field": "den_inc",
        "type": "rightAligned",
        "filter": "agNumberColumnFilter",
        "valueFormatter": {"function": "d3.format('(.3e')(params.value)"},
    },
    {
        "headerName": "Data",
        "field": "data",
        "type": "rightAligned",
        "filter": "agNumberColumnFilter",
        "valueFormatter": {"function": "d3.format('(.3e')(params.value)"},
    },
    {
        "headerName": "dData",
        "field": "ddata",
        "type": "rightAligned",
        "filter": "agNumberColumnFilter",
        "valueFormatter": {"function": "d3.format('(.3e')(params.value)"},
    },
]


columnDefs_residual = [
    {
        "headerName": "Energy [MeV]",
        "field": "en_inc",
        "type": "rightAligned",
        "filter": "agNumberColumnFilter",
        "valueFormatter": {"function": "d3.format('(.3e')(params.value)"},
    },
    {
        "headerName": "dEnergy [MeV]",
        "field": "den_inc",
        "type": "rightAligned",
        "filter": "agNumberColumnFilter",
        "valueFormatter": {"function": "d3.format('(.3e')(params.value)"},
    },
    {
        "headerName": "Residual",
        "field": "residual",
        "type": "rightAligned",
        "filter": "agTextColumnFilter",
        "filterParams": defaultFilterParams,
    },
    {
        "headerName": "Level Number",
        "field": "level_num",
        "type": "rightAligned",
        "filter": "agNumberColumnFilter",
        "valueFormatter": {"function": "d3.format('(d')(params.value)"},
    },
    {
        "headerName": "Data",
        "field": "data",
        "type": "rightAligned",
        "filter": "agNumberColumnFilter",
        "valueFormatter": {"function": "d3.format('(.3e')(params.value)"},
    },
    {
        "headerName": "dData",
        "field": "ddata",
        "type": "rightAligned",
        "filter": "agNumberColumnFilter",
        "valueFormatter": {"function": "d3.format('(.3e')(params.value)"},
    },
]


columnDefs_de = [
    {
        "headerName": "Energy [MeV]",
        "field": "en_inc",
        "type": "rightAligned",
        "filter": "agNumberColumnFilter",
        "valueFormatter": {"function": "d3.format('(.3e')(params.value)"},
    },
    {
        "headerName": "dEnergy [MeV]",
        "field": "den_inc",
        "type": "rightAligned",
        "filter": "agNumberColumnFilter",
        "valueFormatter": {"function": "d3.format('(.3e')(params.value)"},
    },
    {
        "headerName": "dSig/dE [MeV]",
        "field": "e_out",
        "type": "rightAligned",
        "filter": "agNumberColumnFilter",
        "valueFormatter": {"function": "d3.format('(.3e')(params.value)"},
    },
    {
        "headerName": "dS/dE [MeV]",
        "field": "de_out",
        "type": "rightAligned",
        "filter": "agNumberColumnFilter",
        "valueFormatter": {"function": "d3.format('(.3e')(params.value)"},
    },
    {
        "headerName": "Data",
        "field": "data",
        "type": "rightAligned",
        "filter": "agNumberColumnFilter",
        "valueFormatter": {"function": "d3.format('(.3e')(params.value)"},
    },
    {
        "headerName": "dData",
        "field": "ddata",
        "type": "rightAligned",
        "filter": "agNumberColumnFilter",
        "valueFormatter": {"function": "d3.format('(.3e')(params.value)"},
    },
]


columnDefs_da = [
    {
        "headerName": "Energy [MeV]",
        "field": "en_inc",
        "type": "rightAligned",
        "filter": "agNumberColumnFilter",
        "valueFormatter": {"function": "d3.format('(.3e')(params.value)"},
    },
    {
        "headerName": "dEnergy [MeV]",
        "field": "den_inc",
        "type": "rightAligned",
        "filter": "agNumberColumnFilter",
        "valueFormatter": {"function": "d3.format('(.3e')(params.value)"},
    },
    {
        "headerName": "Angle [Degree]",
        "field": "angle",
        "type": "rightAligned",
        "filter": "agNumberColumnFilter",
        "valueFormatter": {"function": "d3.format('(.3e')(params.value)"},
    },
    {
        "headerName": "dAngle [Degree]",
        "field": "dangle",
        "type": "rightAligned",
        "filter": "agNumberColumnFilter",
        "valueFormatter": {"function": "d3.format('(.3e')(params.value)"},
    },
    {
        "headerName": "Data",
        "field": "data",
        "type": "rightAligned",
        "filter": "agNumberColumnFilter",
        "valueFormatter": {"function": "d3.format('(.3e')(params.value)"},
    },
    {
        "headerName": "dData",
        "field": "ddata",
        "type": "rightAligned",
        "filter": "agNumberColumnFilter",
        "valueFormatter": {"function": "d3.format('(.3e')(params.value)"},
    },
]


columnDefs_fy = [
    {
        "headerName": "A",
        "field": "mass",
        "type": "rightAligned",
        "filter": "agNumberColumnFilter",
        "valueFormatter": {"function": "d3.format('(.2f')(params.value)"},
    },
    {
        "headerName": "Z",
        "field": "charge",
        "type": "rightAligned",
        "filter": "agNumberColumnFilter",
        "valueFormatter": {"function": "d3.format('(.2f')(params.value)"},
    },
    {
        "headerName": "Isomer",
        "field": "isomer",
        "type": "rightAligned",
        "filter": "agNumberColumnFilter",
        "valueFormatter": {"function": "d3.format('(.2f')(params.value)"},
    },
    {
        "headerName": "Energy [MeV]",
        "field": "en_inc",
        "type": "rightAligned",
        "filter": "agNumberColumnFilter",
        "valueFormatter": {"function": "d3.format('(.3e')(params.value)"},
    },
    {
        "headerName": "dEnergy [MeV]",
        "field": "den_inc",
        "type": "rightAligned",
        "filter": "agNumberColumnFilter",
        "valueFormatter": {"function": "d3.format('(.3e')(params.value)"},
    },
    {
        "headerName": "Data",
        "field": "data",
        "type": "rightAligned",
        "filter": "agNumberColumnFilter",
        "valueFormatter": {"function": "d3.format('(.3e')(params.value)"},
    },
    {
        "headerName": "dData",
        "field": "ddata",
        "type": "rightAligned",
        "filter": "agNumberColumnFilter",
        "valueFormatter": {"function": "d3.format('(.3e')(params.value)"},
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


def data_table_ag(pageparam):
    return dag.AgGrid(
        id="exfor_table_" + pageparam,
        columnDefs=columnDefsDefault + columnDefs_xs
        if pageparam == "xs"
        else columnDefsDefault + columnDefs_fy
        if pageparam == "fy"
        else columnDefsDefault + columnDefs_de
        if pageparam == "de"
        else columnDefsDefault + columnDefs_da
        if pageparam == "da"
        else columnDefsDefault + columnDefs_residual
        if pageparam == "rp"
        else columnDefsDefault,
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
