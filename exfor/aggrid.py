import pandas as pd
import dash_ag_grid as dag
from dash import html, dcc, callback, Input, Output, State
from exforparser.sql.queries import join_reac_bib

## https://dashaggrid.pythonanywhere.com/selection/cell-selection

## SQL query to load all indexes with bib data
df = join_reac_bib()

# See https://community.plotly.com/t/dash-ag-grid-how-to-make-filter-available-with-infinite-scroll-mode/73430
defaultFilterParams = {
    "filterOptions": ["contains"],
    "defaultOption": "contains",
    "trimInput": True,
    # "debounceMs": 1000,
}

columnDefs = [
    {
        "headerName": "entry_id",
        "field": "entry_id",
        "filter": "agTextColumnFilter",
        "filterParams": defaultFilterParams,
        # "checkboxSelection": True,
        # "headerCheckboxSelection": True,
        # "cellRenderer": {"function": "return_html(params.value)" },
    },
    {
        "headerName": "authors",
        "field": "authors",
        "type": "rightAligned",
        "filter": "agTextColumnFilter",
        "filterParams": defaultFilterParams,
        # "editable": True,
    },
    {
        "headerName": "year",
        "field": "year",
        "type": "rightAligned",
        # "filter": "agTextColumnFilter",
        "filter": "agNumberColumnFilter",
    },
    {
        "headerName": "institute",
        "field": "main_facility_institute",
        "type": "rightAligned",
        "filter": "agTextColumnFilter",
    },
    {
        "headerName": "facility",
        "field": "main_facility_type",
        "type": "rightAligned",
        "filter": "agTextColumnFilter",
    },
    {
        "headerName": "target",
        "field": "target",
        "type": "rightAligned",
        "filter": "agTextColumnFilter",
    },
    {
        "headerName": "process",
        "field": "process",
        "type": "rightAligned",
        "filter": "agTextColumnFilter",
    },
    {
        "headerName": "residual",
        "field": "residual",
        "type": "rightAligned",
        "filter": "agTextColumnFilter",
    },
    {
        "headerName": "sf5",
        "field": "sf5",
        "type": "rightAligned",
        "filter": "agTextColumnFilter",
    },
    {
        "headerName": "sf6",
        "field": "sf6",
        "type": "rightAligned",
        "filter": "agTextColumnFilter",
    },
    {
        "headerName": "sf7",
        "field": "sf7",
        "type": "rightAligned",
        "filter": "agTextColumnFilter",
    },
    {
        "headerName": "sf8",
        "field": "sf8",
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


defaultColDef = {
    "flex": 1,
    "width": 50,
    "editable": False,
    # "floatingFilter": True,
    "resizable": True,
    "sortable": True,
    "filter": True,
}


aggrid_layout = dag.AgGrid(
    id="index-all",
    enableEnterpriseModules=False,
    # licenseKey=os.environ["AGGRID_ENTERPRISE"],
    # columnDefs=[{"headerName": i, "field": i} for i in df.columns],
    columnDefs=columnDefs,
    rowData=df.to_dict("records"),
    columnSize="sizeToFit",
    defaultColDef=defaultColDef,
    dashGridOptions={
        "undoRedoCellEditing": True,
        "rowSelection": "multiple",
    },
    # persistence=True,
    # persisted_props=["filterModel"]
)


@callback(
    Output("location_sch", "href", allow_duplicate=True),
    Input("index-all", "cellClicked"),
    prevent_initial_call=True,
)
def display_cell_clicked_on(cell):
    if cell is None:
        return "Click on a cell"
    if cell["colId"] == "entry_id":
        return "http://127.0.0.1:8050/dataexplorer/exfor/entry/" + cell["value"]


@callback(Output("index-all", "filterModel"), Input("geo_map", "clickData"))
def select_facility(selected_data):
    if selected_data:
        print(selected_data["points"][0]["customdata"][1])
        return [
            {"authors": {"filterType": "text", "type": "contains", "filter": "Smith"}}
        ]
    else:
        []
