import json
from io import StringIO
import pandas as pd

from Bio import Phylo
from dash import html, callback, Input, Output, State
import dash_cytoscape as cyto


from config import engines
from exfor.utils_phylogeny import *
from exfor.datahandle.list import MAPPING
from libraries2023.datahandle.list import PARTICLE



def _load_reactions():
    connection = engines["exfor"].connect()
    df = pd.read_sql_table("exfor_reactions", connection)
    return df


def _get_key(sf6):
    # DA/DA/DE --> return DE
    if not sf6:
        return None
    if len(sf6.split("/")) == 2:
        return sf6.split("/")[-1]
    else:
        return sf6


def _get_top_category(sf6):
    if not sf6:
        return "Others"

    if sf6.endswith("DA/DE"):
        return "DDX"

    elif MAPPING["SF6"].get(sf6):
        return MAPPING["SF6"][sf6]["top_category"]

    else:
        return "Others"


breadcrumb = {}


df = _load_reactions()
df["entry"] = df["entry_id"].str[:5]
df["key"] = df["sf6"].map(_get_key)
df["top_category"] = df["key"].map(_get_top_category)



def make_nodes(breadcrumb):
    # print(breadcrumb)

    def _in_tuple(*args):
        return tuple(a for a in args)

    top = []
    nodes = []

    if not breadcrumb:
        for c in df["top_category"].unique():
            top += _in_tuple(c)

        return str(tuple(top)) + "EXFOR"


    elif breadcrumb["top_category"] and not breadcrumb["sf6"]:
        for c in df["top_category"].unique():
            if c == breadcrumb["top_category"]:
                sf6 = ()

                for k in sorted(df[df["top_category"] == c]["sf6"].unique()):
                    sf6 += _in_tuple(k)

                nodes.append(str(sf6) + c)

            else:
                nodes.append(c)

        return "(" + ",".join(nodes) + ")EXFOR"


    elif breadcrumb["sf6"] and not breadcrumb["projectile"]:
        for c in df["top_category"].unique():
            if c == breadcrumb["top_category"]:
                sf6_node = []

                for k in sorted(df[df["top_category"] == c]["sf6"].unique()):
                    if k == breadcrumb["sf6"]:
                        process = ()

                        # for p in sorted(
                        #     df[(df["top_category"] == c) & (df["sf6"] == k)][
                        #         "projectile"
                        #     ].unique()
                        # ):
                        for p in PARTICLE:
                            process += _in_tuple(p)

                        sf6_node.append(str(process) + k)

                    else:
                        sf6_node.append(k)

                nodes.append("(" + ",".join(sf6_node) + ")" + c)

            else:
                nodes.append(c)

        return "(" + ",".join(nodes) + ")EXFOR"


    elif breadcrumb["projectile"] and not breadcrumb["element"]:
        for c in df["top_category"].unique():
            if c == breadcrumb["top_category"]:
                sf6_node = []

                for k in sorted(df[df["top_category"] == c]["sf6"].unique()):
                    if k == breadcrumb["sf6"]:
                        process = ()
                        proj_node = []

                        # for p in sorted(
                        #     df[(df["top_category"] == c) & (df["sf6"] == k)][
                        #         "projectile"
                        #     ].unique()
                        # ):
                        for p in PARTICLE:
                            process += _in_tuple(p)
                            if p == breadcrumb["projectile"]:
                                target = ()

                                for t in sorted(
                                    df[
                                        (df["top_category"] == c)
                                        & (df["sf6"] == k)
                                        & (df["projectile"] == p)
                                    ]["target"].unique()
                                ):
                                    target += _in_tuple(t)

                                proj_node.append(str(target) + p)

                            else:
                                proj_node.append(p)

                        sf6_node.append("(" + ",".join(proj_node) + ")" + c)

                    else:
                        sf6_node.append(k)

                nodes.append("(" + ",".join(sf6_node) + ")" + c)

            else:
                nodes.append(c)

        return "(" + ",".join(nodes) + ")EXFOR"

    else:
        for c in df["top_category"].unique():
            top += _in_tuple(c)

        return str(tuple(top)) + "EXFOR"


def create_tree(breadcrumb):
    ## create tree with Newick format
    c = make_nodes(breadcrumb)

    ## Convert newick to the tree format of dash_cytoscape
    tree = Phylo.read(StringIO(c), "newick")
    return tree


layout = {
    "name": "preset",
    "idealEdgeLength": 100,
    "nodeOverlap": 20,
    "refresh": 20,
    "fit": True,
    "padding": 30,
    "randomize": False,
    "componentSpacing": 100,
    "nodeRepulsion": 400000,
    "edgeElasticity": 100,
    "nestingFactor": 5,
    "gravity": 80,
    "responsive": True,
    "numIter": 1000,
    "initialTemp": 200,
    "coolingFactor": 0.95,
    "autoRefreshLayout": True,
    "boxSelectionEnabled": True,
    "userZoomingEnabled": True,
    "zoomingEnabled": True,
    "minTemp": 1.0,
}  # preset, random, grid, circle, concentric, breadthfirst, cose


# def stylesheet(categroy):
# return [{
stylesheet = [
    {
        "selector": ".nonterminal",
        "style": {
            "label": "data(name)",
            "background-opacity": 0,
            "text-halign": "left",
            "text-valign": "top",
            "background-color": "blue",
            "line-color": "blue",
        },
    },
    {"selector": ".support", "style": {"label": "data(name)", "background-opacity": 0}},
    {
        "selector": "edge",
        "style": {
            "source-endpoint": "inside-to-node",
            "target-endpoint": "inside-to-node",
        },
    },
    {
        "selector": ".terminal",
        "style": {
            "label": "data(name)",
            "width": 10,
            "height": 10,
            "text-valign": "center",
            "text-halign": "right",
            "background-color": "#222222",
            "background-color": "blue",
            "line-color": "blue",
        },
    },
]


tree = create_tree(breadcrumb)
nodes, edges = generate_elements(tree)
elements = nodes + edges
cyto_layout = cyto.Cytoscape(
    id="cytoscape-phylogeny",
    elements=elements,
    stylesheet=stylesheet,
    layout=layout,
    style={"width": "100%", "height": "300px"},
    responsive=True,
)

# layout = html.Div(
#     [
#         cyto_layout,
#         html.P(id="cytoscape-tapNodeData-output"),
#     ]
# )


def check_node_parent(node_data, elements):
    sp = node_data["id"].split("c")
    breadcrumb = {
        "top_category": None,
        "sf6": None,
        "projectile": None,
        "element": None,
        "mass": None,
    }

    for i in range(len(sp))[1:]:
        if i == 1:
            search_string = "rc" + str(sp[i])

        else:
            search_string += "c" + str(sp[i])

        for l in range(len(elements)):
            if elements[l]["data"]["id"] == search_string:
                if i == 1:
                    breadcrumb["top_category"] = elements[l]["data"]["label"]

                if i == 2:
                    breadcrumb["sf6"] = elements[l]["data"]["label"]

                if i == 3:
                    breadcrumb["projectile"] = elements[l]["data"]["label"]

                if i == 4:
                    breadcrumb["element"] = elements[l]["data"]["label"]

                if i == 5:
                    breadcrumb["mass"] = elements[l]["data"]["label"]

    return breadcrumb



@callback(
    Output("cytoscape-phylogeny", "elements"),
    Input("cytoscape-phylogeny", "tapNode"),
    State("cytoscape-phylogeny", "elements"),
)
def displayTapNodeData(node_data, elements):
    if node_data:

        breadcrumb = check_node_parent(node_data["data"], elements)
        print(breadcrumb)

        tree = create_tree(breadcrumb)
        nodes, edges = generate_elements(tree)
        elements = nodes + edges

    # if breadcrumb.get("element"):

    return elements




# @callback(
#     Output("cytoscape-phylogeny", "stylesheet"),
#     Input("cytoscape-phylogeny", "mouseoverEdgeData"),
# )
# def color_children(edgeData):

#     if not edgeData:
#         return stylesheet

#     if "s" in edgeData["source"]:
#         val = edgeData["source"].split("s")[0]

#     else:
#         val = edgeData["source"]

#         children_style = [
#             {
#                 "selector": 'edge[source *= "{}"]'.format(val),
#                 "style": {"line-color": "blue"},
#             }
#         ]

#         return stylesheet + children_style


# @callback(
#     [
#         Output("cytoscape-phylogeny", "elements"),
#         Output("reaction_category", "value"),
#         Output("target_elem_ex", "value"),
#         Output("target_mass_ex", "value"),
#         Output("reaction_ex", "value"),
#         Output("reac_options_ex", "value"),
#     ],
#     # [
#     Input("cytoscape-phylogeny", "tapNode"),
#     Input("cytoscape-phylogeny", "elements"),
#     # ]
# )
# def displayTapNodeData(node_data, elements):
#     print(node_data, elements)
#     if not elements:
#         return None, None, None, None, None, None
#     breadcrumb = {}
#     # print(json.dumps(elements, indent=1))
#     if node_data:
#         breadcrumb = check_node_parent(node_data["data"], elements)
#         tree = create_tree(breadcrumb)
#         nodes, edges = generate_elements(tree)
#         elements = nodes + edges

#     if breadcrumb.get("element"):
#         charge, elem, mass = breadcrumb["element"].split("-")
#         return None, breadcrumb["top_category"], elem.capitalize(), mass, "n,g", None

#     else:
#         return elements, None, None, None, None, None




# if __name__ == "__main__":
#     app.run_server(debug=True)
