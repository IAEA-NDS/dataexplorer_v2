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
        "headerName": "Energy [MeV]",
        "field": "en_inc",
        "type": "rightAligned",
        "filter": "agNumberColumnFilter",
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



columnDefsFY = [
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
        "headerName": "A",
        "field": "mass",
        "type": "rightAligned",
        "filter": "agNumberColumnFilter",
    },
    {
        "headerName": "Z",
        "field": "charge",
        "type": "rightAligned",
        "filter": "agNumberColumnFilter",
    },
    {
        "headerName": "Isomer",
        "field": "isomer",
        "type": "rightAligned",
        "filter": "agNumberColumnFilter",
    },
    {
        "headerName": "Energy [MeV]",
        "field": "en_inc",
        "type": "rightAligned",
        "filter": "agNumberColumnFilter",
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
        # enableEnterpriseModules=False,
        columnDefs=columnDefs if pageparam !="FY" else columnDefsFY,
        defaultColDef=defaultColDef,
        # rowData=df.to_dict("records"),.
        columnSize="sizeToFit",
        # columnSizeOptions=columnSizeOptions,
        dashGridOptions={
            "rowSelection": "multiple",
            "rowMultiSelectWithClick": True,
            # "pagination": True,
            # "paginationPageSize": 100
        },
        className="ag-theme-balham",  ## Themes: ag-theme-alpine, ag-theme-alpine-dark, ag-theme-balham, ag-theme-balham-dark, ag-theme-material, and ag-bootstrap.
        persistence=True,
        # persisted_props=["filterModel"]
    )



