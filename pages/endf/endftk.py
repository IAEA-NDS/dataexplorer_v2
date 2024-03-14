####################################################################
#
# This file is part of libraries-2021 dataexplorer, https://nds.iaea.org/dataexplorer/.
# Copyright (C) 2022 International Atomic Energy Agency (IAEA)
#
# Contact:    nds.contact-point@iaea.org
#
####################################################################

import pandas as pd
import dash
from dash import html, dcc, Input, Output, ALL, MATCH, ctx, no_update, Patch, callback, callback_context
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate
import os
from zipfile import ZipFile 

from config import ENDFtk_Build_PATH, DeCE_Bin_PATH, ENDF_Archive_DIR
from pages_common import (
    sidehead,
    footer,
    endftk_navbar,
    page_urls,
    main_fig,
    input_lin_log_switch
)
from submodules.utilities.reaction import generate_mt_list
from modules.reactions.figs import default_chart

import sys
sys.path.append( ENDFtk_Build_PATH )
import ENDFtk


## Registration of page
dash.register_page(
    __name__,
    path="/endf/endftk",
    title="ENDF-6 Viewer powered by ENDFtk (ENDF Toolkit)",
    redirect_from=["/endftk", "/endftoolkit", "/endf"],
)
pageparam = "endftk"




# ## ENDF Files
# endf_files = [
#     "BROND-2-2",
#     "BROND-3.1",
#     "DXS",
#     "ENDF-B-IV",
#     "ENDF-B-V",
#     "ENDF-B-VI-8",
#     "ENDF-B-VII.0",
#     "ENDF-B-VII.1",
#     "ENDF-B-VIII.0",
#     "ENDF-HE-VI",
#     "IBA-Eval",
#     "IBA-Eval-2007",
#     "JENDL-3.2",
#     "JENDL-3.3",
#     "JENDL-4.0",
#     "JENDL-4.0-HE",
#     "JENDL-4.0u2-20160106",
#     "JENDL-5",
#     "JENDL-AD-2017",
#     "JENDL-DEU-2020",
#     "JENDL-HE-2007",
#     "JENDL-ImPACT-18",
#     "JENDL-PD-2016",
#     "JENDL-PD-2016.1",
# ]


## MF Description
mf_dict = {
    1: "General information",
    # 2: "Resonance parameter data",
    3: "Reaction cross sections",
    4: "Angular distributions for emitted particles",
    5: "Energy distributions for emitted particles",
    6: "Energy-angle distributions for emitted particles",
    7: "Thermal neutron scattering law data",
    8: "Radioactivity and fission-product yield data",
    9: "Multiplicities for radioactive nuclide production",
    10: "Cross sections for radioactive nuclide production",
    12: "Multiplicities for photon production",
    13: "Cross sections for photon production",
    14: "Angular distributions for photon production",
    15: "Energy distributions for photon production",
    23: "Photo- or electro-atomic interaction cross sections",
    26: "Electro-atomic angle and energy distribution",
    27: "Atomic form factors or scattering functions for photo-atomic interactions",
    28: "Atomic relaxation data",
    30: "Data covariances obtained from parameter covariances and sensitivities",
    31: "Data covariances for nu(bar)",
    32: "Data covariances for resonance parameters",
    33: "Data covariances for reaction cross sections",
    34: "Data covariances for angular distributions",
    35: "Data covariances for energy distributions",
    39: "Data covariances for radionuclide production yields",
    40: "Data covariances for radionuclide production cross sections",
}

def input_endf(**query_strings):
    return [
        html.Br(),
        html.Label("ENDF-6 Format File"),
        dcc.Dropdown(
            id="endflib_" + pageparam,
            options=os.listdir(ENDF_Archive_DIR),
            placeholder="Select Library",
            persistence=True,
            persistence_type="memory",
            value="ENDF-B-VIII.0",
            style={"font-size": "small", "width": "100%"},
        ),
        dcc.Dropdown(
            id="endfdir_" + pageparam,
            options=[],
            placeholder="Select Type",
            persistence=True,
            persistence_type="memory",
            value="n",
            style={"font-size": "small", "width": "100%"},
        ),
        dcc.Dropdown(
            id="endffile_" + pageparam,
            options=[],
            placeholder="Select File",
            persistence=True,
            persistence_type="memory",
            value="n_9228_92-U-235.zip",
            style={"font-size": "small", "width": "100%"},
        ),
        html.Br(),
        html.Div(id="dropdown-container-div", children=conditions(0)),
        html.Button("Add Section", id="add-section-btn", n_clicks=0, style = {"float": "right"}),
        dcc.Store(id="input_store_" + pageparam),
    ]   


def conditions(n_clicks):
    return html.Div([
        html.Label("ENDF Section"),
        html.Label("Files - MF", style={"font-size": "small"}),
        dcc.Dropdown(
            id={"type": "mf_" + pageparam, "index": n_clicks},
            # id="mf_" + pageparam,
            options=[ {"label": f"MF{i}: {j}", "value": i} for i, j in mf_dict.items() ],
            placeholder="Select MF",
            persistence=True,
            persistence_type="memory",
            value=3,
            style={"font-size": "small", "width": "100%"},
            multi=False
        ),
        dcc.Dropdown(
            id={"type": "mt_" + pageparam, "index": n_clicks},
            # id="mt_" + pageparam,
            options=[],
            placeholder="Select MT",
            persistence=True,
            persistence_type="memory",
            value=1,
            style={"font-size": "small", "width": "100%"},
            multi=False
        ),
        dcc.Dropdown(
            id="operator_" + pageparam,
            options=[ "extract", "+", "-", "*", "/" ],
            placeholder="Select Operation",
            persistence=True,
            persistence_type="memory",
            value="extract",
            style={"font-size": "small", "width": "100%"},
            multi=False
        ),
        html.Br(),
        ], id="test_div",  style={"border": "0.5px dotted #333333",}, # "background-color": "#ffff99" 
        )


right_layout_endf = [
    endftk_navbar,
    html.Hr(
        style={
            "border": "3px",
            "border-top": "1px solid",
            "margin-top": "5px",
            "margin-bottom": "5px",
        }
    ),
    
    # Log/Linear switch
    html.Div(children=input_lin_log_switch(pageparam)),
    html.Div(id="output_endftk"),
    # main_fig,
    dcc.Loading(
        children=main_fig(pageparam),
        type="circle",
    ),
    html.Hr(style={"border": "3px", "border-top": "1px solid"}),
    footer,
]

def layout(**query_strings):
    return html.Div(
        [
            dcc.Location(id="location"),
            dbc.Row(
                [
                    ### left panel
                    dbc.Col(
                        [
                            sidehead,
                            html.Div(
                                [
                                    html.Label("Dataset"),
                                    dcc.Dropdown(
                                        id="dataset",
                                        options=list(page_urls.keys()),
                                        value="ENDF-6 Format Viewer",
                                        style={"font-size": "small"},
                                        persistence=True,
                                        persistence_type="memory",
                                    ),
                                    html.Div(input_endf(**query_strings)),
                                ],
                                style={"margin-left": "10px"},
                            ),
                        ],
                        style={
                            "height": "100vh",
                            "background-color": "hsla(30,40%,90%,0.5)",
                        },
                        width=2,
                    ),
                    ### Right panel
                    dbc.Col(
                        [
                            html.Div(
                                children=right_layout_endf,
                                style={"margin-right": "20px", "margin-left": "10px"},
                            ),
                        ],
                        width=10,
                    ),
                ]
            ),
        ],
        style={"height": "100vh"},
    )



################################# Callback

@callback(
    Output("endfdir_endftk", "options"),
    Input("endflib_endftk", "value"),
)
def update_dir_list(libname):
    ## List the name of evaluated data libraries in the endf_archive folder
    if libname:
        return sorted( [a for a in os.listdir(os.path.join(ENDF_Archive_DIR, libname)) if os.path.isdir(os.path.join(ENDF_Archive_DIR, libname, a))] )

    else:
        return no_update



@callback(
    Output("endffile_endftk", "options"),
    [
        Input("endflib_endftk", "value"),
        Input("endfdir_endftk", "value"),
    ]
)
def update_dir_list(libname, dir):
    ## List the files in the Library/Projectile (or decay or fpy directory)
    if libname and dir:
        return sorted( [f for f in os.listdir(os.path.join(ENDF_Archive_DIR, libname, dir)) if os.path.isfile(os.path.join(ENDF_Archive_DIR, libname, dir, f))] )
    else:
        return no_update


@callback(
    Output("input_store_endftk", "data"),
    [
        Input("endflib_endftk", "value"),
        Input("endfdir_endftk", "value"),
        Input("endffile_endftk", "value"),
    ]
)
def update_dir_list(libname, dir_name, file):
    ## Store input condition
    if libname and dir_name and file:
        return dict(
            {
                "libname": libname,
                "dir_name": dir_name,
                "file": file,
            }
            )
    else:
        return no_update



@callback(
    Input("input_store_endftk", "data"),
    output=dict(
            options=Output({'type': 'mt_endftk', 'index': ALL}, 'options')
    ),
)
def update_dir_list2(input_store):
    libname = input_store.get("libname")
    dir_name = input_store.get("dir_name")

    ## To update the MT numbers. It needs the projectile as an input (taken from dir name).
    if libname and dir_name:
        mt = [ {"label": f"MT{i}: {j}", "value": int(i)} for i, j in generate_mt_list(dir_name).items() ]
        outputs = len(callback_context.outputs_grouping['options'])

        return {'options': [mt for _ in range(outputs)]}
    
    else:
        return no_update



@callback(
    Output("dropdown-container-div", "children"), 
    Input("add-section-btn", "n_clicks")
)
def display_dropdowns(n_clicks):
    print("n_clicks", n_clicks)
    patched_children = Patch()
    new_dropdown = conditions(n_clicks)
    patched_children.append(new_dropdown)
    return patched_children



@callback(
    [
        Output("output_endftk", "children"),
        Output("main_fig_endftk", "figure"),
    ],
    [
        Input("input_store_endftk", "data"),
        Input({"type": "mf_endftk", "index": ALL}, "value"),
        Input({"type": "mt_endftk", "index": ALL}, "value"),
        Input({"type": "operator_endftk", "index": ALL}, "value"),
    ]
)
def display_output(input_store, mfs, mts, operators):
    libname = input_store.get("libname")
    dir_name = input_store.get("dir_name")
    file = input_store.get("file")

    file_path = os.path.join( ENDF_Archive_DIR, libname, dir_name, file )

    if file.endswith(".zip"):
        # loading the temp.zip and creating a zip object 
        with ZipFile(file_path, 'r') as zObject: 
            zObject.extract( file.replace(".zip", ".dat"), path="") 
        zObject.close()
        file_path =  file.replace(".zip", ".dat")

    
    print("MT", mfs, "MF", mts, file_path)
    tape = ENDFtk.tree.Tape.from_file( file_path )
    mat = tape.materials.front()

    assert len(mts) == len(mfs)

    parsed = []
    message = ""
    fig = default_chart("log", "log", "n,f")
    allowed = []
    for i in range(len(mts)):
        print(f"{i}th data")
        try:
            data = mat.file( mfs[i] ).section( mts[i] ).parse()

        except:
            for section in mat.file( mfs[i] ).sections:
                allowed += section.MT
            message = f"IndexError: map::at:  key not found. Allowed MTs are {allowed}"

        if mfs[i] == 2:
            if mts[i] != 151:
                message = f"only MT 151 (resonance parameters) are allowed."

            data = mat.file( 2 ).section( 151 ).parse()
            # print(data.el, data.eh, data.spin)

        elif mfs[i] == 3:
            data = mat.file( mfs[i] ).section( mts[i] ).parse()
            df = pd.DataFrame(list(zip(  data.energies.to_list(), data.cross_sections.to_list() )), columns = ["energies", "cross_sections"])
            message += f"Selection {str(i)} = MF {mfs[i]} - MT {mts[i]}"# {operators[i]}"
            print(df)

        if not df.empty:
            fig.add_trace(
                go.Scattergl(
                    x=df["energies"],
                    y=df["cross_sections"],
                    showlegend=True,
                    mode="markers",
                    name=f"MF{str(mfs[i])} - MT{str(mts[i])}",
                )
            )
            # parsed[i] = {"cross_sections": data.cross_sections.to_list(), "energies":data.energies.to_list()}
    # [html.Div(f"Selection {i + 1} = MF {f} - MT {t} {m}" for (i, f, t, m) in enumerate(zip(mfs, mts, operators)))]
    fig.update_yaxes(autorange=True)
    fig.update_xaxes(autorange=True)
    return [f"{message}"], fig





#  |  Readonly properties defined here:
#  |
#  |  AWR
#  |      The atomic weight ratio for the section
#  |
#  |  LR
#  |      The complex break up flag
#  |
#  |  MT
#  |      The MT number of the section
#  |
#  |  NC
#  |      The number of lines in this section
#  |
#  |  NP
#  |      The number of points
#  |
#  |  NR
#  |      The number of interpolation ranges
#  |
#  |  QI
#  |      The reaction Q value
#  |
#  |  QM
#  |      The mass difference Q value
#  |
#  |  ZA
#  |      The ZA identifier for the section
#  |
#  |  atomic_weight_ratio
#  |      The atomic weight ratio for the section
#  |
#  |  boundaries
#  |      The interpolation boundaries
#  |
#  |  complex_breakup
#  |      The complex break up flag
#  |
#  |  cross_sections
#  |      The cross section values
#  |
#  |  energies
#  |      The energy values
#  |
#  |  interpolants
#  |      The interpolation type for each range
#  |
#  |  mass_difference_qvalue
#  |      The mass difference Q value
#  |
#  |  reaction_qvalue
#  |      The mass difference Q value
#  |
#  |  section_number
#  |      The MT number of the section
#  |
#  |  target_identifier
#  |      The ZA identifier for the section