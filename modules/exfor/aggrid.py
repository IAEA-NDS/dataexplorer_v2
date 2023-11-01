####################################################################
#
# This file is part of libraries-2023 dataexplorer, https://nds.iaea.org/dataexplorer/.
# Copyright (C) 2022 International Atomic Energy Agency (IAEA)
#
# Contact:    nds.contact-point@iaea.org
#
####################################################################

import dash_ag_grid as dag

defaultFilterParams = {
    "filterOptions": ["contains"],
    "defaultOption": "contains",
    "trimInput": True,
    # "debounceMs": 1000,
}

defaultColDef = {
    # "floatingFilter": True,
    "resizable": True,
    "sortable": True,
    "filter": True,
}


### ------------------------------------------------ ###
#             Bib Table
### ------------------------------------------------ ###
columnDefsBib = [
    {
        "headerName": "Entry",
        "field": "entry_id_link",
        "type": "leftAligned",
        "filter": "agTextColumnFilter",
        "filterParams": defaultFilterParams,
        "cellRenderer": "markdown",
        "checkboxSelection": True,
        "headerCheckboxSelection": True,
    },
    {
        "headerName": "Facility Type",
        "field": "main_facility_type_desc",
        "type": "leftAligned",
        "filter": "agTextColumnFilter",
        "filterParams": defaultFilterParams,
        # "cellRenderer": "markdown",
    },
    {
        "headerName": "Authors",
        "field": "authors",
        "type": "leftAligned",
        "filter": "agTextColumnFilter",
        "filterParams": defaultFilterParams,
        # "editable": True,
    },
    {
        "headerName": "Title",
        "field": "title",
        "type": "leftAligned",
        "filter": "agTextColumnFilter",
        "filterParams": defaultFilterParams,
    },
    {
        "headerName": "Reference",
        "field": "main_reference_link",
        "filter": "agTextColumnFilter",
        "cellRenderer": "markdown",
    },
    {
        "headerName": "Year",
        "field": "year",
        "type": "rightAligned",
        # "filter": "agTextColumnFilter",
        "filter": "agNumberColumnFilter",
    },
]

columnSizeOptionsBib = {
    # "defaultMinWidth": 100,
    "columnLimits": [
        {"key": "entry_id_link", "maxWidth": 100},
        {"key": "authors", "minWidth": 300},
        {"key": "main_facility_type_desc", "maxWidth": 200},
        # {"key": "title", "minWidth": 500},
        {"key": "main_reference", "maxWidth": 200},
        {"key": "year", "maxWidth": 80},
    ],
}

aggrid_layout_bib = dag.AgGrid(
    id="bib_index",
    columnDefs=columnDefsBib,
    columnSize="responsiveSizeToFit",
    columnSizeOptions=columnSizeOptionsBib,
    defaultColDef=defaultColDef,
    dashGridOptions={
        "enableCellTextSelection": True,
        "rowSelection": "multiple",
        "rowMultiSelectWithClick": True,
        "domLayout": "autoHeight",
        "noRowsOverlayComponent": "CustomNoRowsOverlay",
        "noRowsOverlayComponentParams": {
            "message": "Please select facility from map",
            "fontSize": 12,
        },
        "pagination": True,
        "paginationPageSize": 20,
    },
    style={"height": None},  # , "width": "100%"},
    className="ag-theme-balham",
    persistence=True,
    persisted_props=["filterModel"],
)


columnDefsUpd = columnDefsBib + [
    {
        "headerName": "Updated",
        "field": "last_update",
        "type": "rightAligned",
        "filter": "agDateColumnFilter",
    },
    {
        "headerName": "Status",
        "field": "new",
        "type": "rightAligned",
        "filter": "agDateColumnFilter",
    },
]


columnSizeOptionsUpdated = {
    # "defaultMinWidth": 100,
    "columnLimits": [
        {"key": "entry_id_link", "maxWidth": 100},
        {"key": "authors", "minWidth": 300},
        {"key": "title", "minWidth": 500},
        {"key": "main_reference", "maxWidth": 250},
        {"key": "year", "maxWidth": 120},
        {"key": "last_update", "maxWidth": 150},
        {"key": "new", "maxWidth": 150},
    ],
}


def aggrid_updated(df=None):
    return dag.AgGrid(
        id="bib",
        rowData=df.to_dict("records"),
        columnDefs=columnDefsUpd,
        columnSize="responsiveSizeToFit",
        columnSizeOptions=columnSizeOptionsUpdated,
        defaultColDef=defaultColDef,
        dashGridOptions={
            "enableCellTextSelection": True,
            "rowSelection": "multiple",
            "rowMultiSelectWithClick": True,
            "domLayout": "autoHeight",
            "pagination": True,
            "paginationPageSize": 15,
            "loadingOverlayComponent": "CustomLoadingOverlay",
            "loadingOverlayComponentParams": {
                "loadingMessage": "Recently added/updated list will be shown here.",
            },
        },
        # style={"height": None},  # , "width": "100%"},
        style={"height": 400, "width": "100%"},
        className="ag-theme-balham",
        persistence=True,
        persisted_props=["filterModel"],
    )


### ------------------------------------------------ ###
#             Full Index Store
### ------------------------------------------------ ###
columnDefsIndexAll = [
    {
        "headerName": "Entry Id",
        "field": "entry_id_link",
        "filter": "agTextColumnFilter",
        "filterParams": defaultFilterParams,
        "cellRenderer": "markdown",
        # "checkboxSelection": True,
        # "headerCheckboxSelection": True,
    },
    {
        "headerName": "Authors",
        "field": "authors",
        "filter": "agTextColumnFilter",
    },
    {
        "headerName": "Year",
        "field": "year",
        "filter": "agNumberColumnFilter",
    },
    {
        "headerName": "Reference",
        "field": "main_reference_link",
        "filter": "agTextColumnFilter",
        "cellRenderer": "markdown",
    },
    # {
    #     "headerName": "Reference",
    #     "field": "main_reference",
    #     "filter": "agTextColumnFilter",
    # },
    {
        "headerName": "Target",
        "field": "target",
        "type": "rightAligned",
        "filter": "agTextColumnFilter",
    },
    {
        "headerName": "Process",
        "field": "process",
        "type": "rightAligned",
        "filter": "agTextColumnFilter",
    },
    # {
    #     "headerName": "Residual",
    #     "field": "residual",
    #     "type": "rightAligned",
    #     "filter": "agTextColumnFilter",
    # },
    # {
    #     "headerName": "Level Num",
    #     "field": "level_num",
    #     "type": "rightAligned",
    #     "filter": "agTextColumnFilter",
    # },
    {
        "headerName": "SF4",
        "field": "sf4",
        "type": "rightAligned",
        "filter": "agTextColumnFilter",
    },
    {
        "headerName": "SF5",
        "field": "sf5",
        "type": "rightAligned",
        "filter": "agTextColumnFilter",
    },
    {
        "headerName": "SF6",
        "field": "sf6",
        "type": "rightAligned",
        "filter": "agTextColumnFilter",
    },
    {
        "headerName": "SF7",
        "field": "sf7",
        "type": "rightAligned",
        "filter": "agTextColumnFilter",
    },
    {
        "headerName": "SF8",
        "field": "sf8",
        "type": "rightAligned",
        "filter": "agTextColumnFilter",
    },
    {
        "headerName": "EXFOR Reaction Code",
        "field": "x4_code",
        "type": "rightAligned",
        "filter": "agTextColumnFilter",
    },
    {
        "headerName": "Emin",
        "field": "e_inc_min",
        "type": "rightAligned",
        "filter": "agNumberColumnFilter",
        "valueFormatter": {"function": "d3.format('(.3e')(params.value)"},
    },
    {
        "headerName": "Emax",
        "field": "e_inc_max",
        "type": "rightAligned",
        "filter": "agNumberColumnFilter",
        "valueFormatter": {"function": "d3.format('(.3e')(params.value)"},
    },
]


columnDefsIndexSearchRes = [
    {
        "headerName": "Entry Id",
        "field": "entry_id_link",
        "filter": "agTextColumnFilter",
        "filterParams": defaultFilterParams,
        "cellRenderer": "markdown",
        # "checkboxSelection": True,
        # "headerCheckboxSelection": True,
    },
    {
        "headerName": "Target",
        "field": "target",
        "type": "rightAligned",
        "filter": "agTextColumnFilter",
    },
    {
        "headerName": "Process",
        "field": "process",
        "type": "rightAligned",
        "filter": "agTextColumnFilter",
    },
    {
        "headerName": "SF4",
        "field": "sf4",
        "type": "rightAligned",
        "filter": "agTextColumnFilter",
    },
    {
        "headerName": "SF5",
        "field": "sf5",
        "type": "rightAligned",
        "filter": "agTextColumnFilter",
    },
    {
        "headerName": "SF6",
        "field": "sf6",
        "type": "rightAligned",
        "filter": "agTextColumnFilter",
    },
    {
        "headerName": "SF7",
        "field": "sf7",
        "type": "rightAligned",
        "filter": "agTextColumnFilter",
    },
    {
        "headerName": "SF8",
        "field": "sf8",
        "type": "rightAligned",
        "filter": "agTextColumnFilter",
    },
]


columnSizeOptionsIndex = {
    # "defaultMinWidth": 100,
    "columnLimits": [
        {"key": "entry_id_link", "maxWidth": 150},
        {"key": "authors", "maxWidth": 300},
        {"key": "target", "maxWidth": 100},
        {"key": "main_reference", "maxWidth": 200},
        {"key": "year", "maxWidth": 100},
        {"key": "process", "maxWidth": 100},
        {"key": "residual", "maxWidth": 100},
        {"key": "level_num", "maxWidth": 100},
        {"key": "sf4", "maxWidth": 100},
        {"key": "sf5", "maxWidth": 100},
        {"key": "sf6", "maxWidth": 100},
        {"key": "sf7", "maxWidth": 100},
        {"key": "sf8", "maxWidth": 100},
    ],
}


def aggrid_index_result(param):
    return dag.AgGrid(
        id="index_all_" + param,
        columnDefs=columnDefsIndexSearchRes,
        columnSize="responsiveSizeToFit",
        columnSizeOptions=columnSizeOptionsIndex,
        defaultColDef=defaultColDef,
        dashGridOptions={
            "rowSelection": "multiple",
            "rowMultiSelectWithClick": True,
            "pagination": True,
            "paginationPageSize": 20,
            # "pagination": True,
            # "domLayout": "autoHeight",
            "loadingOverlayComponent": "CustomLoadingOverlay",
            "loadingOverlayComponentParams": {
                "loadingMessage": "Please specify search criteria.",
                # "color": "red",
            },
        },
        # style={"height": None},  # "width": "100%"},
        style={"height": 400, "width": "100%"},
        className="ag-theme-balham",
        persistence=True,
        persisted_props=["filterModel"],
    )


def aggrid_search_result(param):
    return dag.AgGrid(
        id="index_search_res_" + param,
        columnDefs=columnDefsIndexAll,
        columnSize="responsiveSizeToFit",
        columnSizeOptions=columnSizeOptionsIndex,
        defaultColDef=defaultColDef,
        dashGridOptions={
            "rowSelection": "single",
            # "rowMultiSelectWithClick": True,
            "pagination": True,
            "paginationPageSize": 100,
            # "pagination": True,
            # "domLayout": "autoHeight",
            "loadingOverlayComponent": "CustomLoadingOverlay",
            "loadingOverlayComponentParams": {
                "loadingMessage": "Please specify search criteria.",
                # "color": "red",
            },
        },
        # style={"height": None},  # "width": "100%"},
        style={"height": 800, "width": "100%"},
        className="ag-theme-balham",
        persistence=True,
        persisted_props=["filterModel"],
    )


### ------------------------------------------------ ###
#             Dynamic generation
### ------------------------------------------------ ###
def aggrid_layout_dynamic(param, df):
    return dag.AgGrid(
        id="aggrid_" + param,
        style={"height": "500px", "width": "100%"},
        columnDefs=[{"field": i} for i in df.columns],
        rowData=df.to_dict("records"),
        columnSize="responsiveSizeToFit",
        dashGridOptions={
            "rowSelection": "multiple",
            "rowMultiSelectWithClick": True,
            "pagination": True,
            # "domLayout": "autoHeight",
            # "noRowsOverlayComponent": "CustomNoRowsOverlay",
            # "noRowsOverlayComponentParams": {
            #     "message": "Please select facility from map",
            #     "fontSize": 12,
            # },
        },
        className="ag-theme-balham",
        persisted_props=["filterModel"],
    )
