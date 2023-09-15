import dash_ag_grid as dag

## https://dashaggrid.pythonanywhere.com/selection/cell-selection

## SQL query to load all indexes with bib data
# from exfor.datahandle.queries import join_reac_bib
# df = join_reac_bib()

# See https://community.plotly.com/t/dash-ag-grid-how-to-make-filter-available-with-infinite-scroll-mode/73430


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
#             Bib store
### ------------------------------------------------ ###
columnDefsBib = [
    {
        "headerName": "Entry",
        "field": "entry_id_link",
        "type": "leftAligned",
        "filter": "agTextColumnFilter",
        "filterParams": defaultFilterParams,
        "cellRenderer": "markdown",
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
        "headerName": "Ref",
        "field": "main_reference",
        "type": "rightAligned",
        # "filter": "agTextColumnFilter",
        "filterParams": defaultFilterParams,
    },
    {
        "headerName": "Year",
        "field": "year",
        "type": "rightAligned",
        # "filter": "agTextColumnFilter",
        "filter": "agNumberColumnFilter",
    },
    # {
    #     "headerName": "Target",
    #     "field": "target",
    #     "type": "rightAligned",
    #     "filter": "agTextColumnFilter",
    # },
    # {
    #     "headerName": "Projectile",
    #     "field": "projectile",
    #     "type": "rightAligned",
    #     "filter": "agTextColumnFilter",
    # },
    # {
    #     "headerName": "Process",
    #     "field": "process",
    #     "type": "rightAligned",
    #     "filter": "agTextColumnFilter",
    # },
    # {
    #     "headerName": "Observable",
    #     "field": "sf6",
    #     "type": "rightAligned",
    #     "filter": "agTextColumnFilter",
    # },
]

columnSizeOptionsBib = {
    "defaultMinWidth": 50,
    "columnLimits": [
        {"key": "authors", "maxWidth": 300},
        {"key": "entry", "maxWidth": 80},
        {"key": "main_facility_type_desc", "maxWidth": 200},
        {"key": "entry_id_link", "maxWidth": 80},
        {"key": "title", "minWidth": 500},
        {"key": "main_reference", "maxWidth": 150},
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
        "rowSelection": "multiple",
        "rowMultiSelectWithClick": True,
        # "domLayout": "autoHeight",
        "noRowsOverlayComponent": "CustomNoRowsOverlay",
        "noRowsOverlayComponentParams": {
            "message": "Please select facility from map",
            "fontSize": 12,
        },
    },
    style={"height": 300},
    className="ag-theme-balham",
    persistence=True,
    persisted_props=["filterModel"],
)


### ------------------------------------------------ ###
#             Full Index Store
### ------------------------------------------------ ###
columnDefs = [
    {
        "headerName": "Entry Id",
        "field": "entry_id_link",
        "filter": "agTextColumnFilter",
        "filterParams": defaultFilterParams,
        "cellRenderer": "markdown",
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
        "headerName": "Residual",
        "field": "residual",
        "type": "rightAligned",
        "filter": "agTextColumnFilter",
    },
    {
        "headerName": "Level Num",
        "field": "level_num",
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
        "headerName": "Emin",
        "field": "e_inc_min",
        "type": "rightAligned",
        "filter": "agTextColumnFilter",
    },
    {
        "headerName": "Emax",
        "field": "e_inc_max",
        "type": "rightAligned",
        "filter": "agTextColumnFilter",
    },
]


def aggrid_layout(param):
    return dag.AgGrid(
        id="index-all-" + param,
        columnDefs=columnDefs,
        columnSize="responsiveSizeToFit",
        defaultColDef=defaultColDef,
        dashGridOptions={
            "rowSelection": "multiple",
            "rowMultiSelectWithClick": True,
        },
        className="ag-theme-balham",
        persistence=True,
        persisted_props=["filterModel"],
    )


# # def aggrid_layout():
# #     return
# aggrid_layout_index = dag.AgGrid(
#             id="index-all",
#             columnDefs=columnDefs,
#             columnSize="responsiveSizeToFit",
#             defaultColDef=defaultColDef,
#             dashGridOptions={
#                 "rowSelection": "multiple",
#                 "rowMultiSelectWithClick": True,
#             },
#             className="ag-theme-balham",
#             persistence=True,
#             persisted_props=["filterModel"],
#         )
