import dash_ag_grid as dag

########### AGGRID tables
defaultFilterParams = {
    "filterOptions": ["contains"],
    "defaultOption": "contains",
    "trimInput": True,
    # "debounceMs": 1000,
}


columnDefs = [
    {
        "headerName": "Author",
        "field": "author",
        "type": "rightAligned",
        "filter": "agTextColumnFilter",
        "filterParams": defaultFilterParams,
        # "checkboxSelection": True,
        # "headerCheckboxSelection": True,
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
    {
        "headerName": "SF8",
        "field": "sf8",
        "type": "rightAligned",
        "filter": "agTextColumnFilter",
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
        {"key": "sf8", "maxWidth": 80},
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
        className="ag-theme-balham",  ## Themes: ag-theme-alpine, ag-theme-alpine-dark, ag-theme-balham, ag-theme-balham-dark, ag-theme-material, and ag-bootstrap.
        persistence=True,
        persisted_props=["filterModel"],
    )
