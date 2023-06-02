from Bio import Phylo
import math
import pandas as pd
import plotly.graph_objs as go
import numpy as np

from exfor_dictionary import Diction

D = Diction()


def generate_elements(tree, xlen=30, ylen=30, grabbable=False):
    # function from
    # https://dash.plotly.com/cytoscape/biopython
    def get_col_positions(tree, column_width=80):
        taxa = tree.get_terminals()

        # Some constants for the drawing calculations
        max_label_width = max(len(str(taxon)) for taxon in taxa)
        drawing_width = column_width - max_label_width - 1

        """Create a mapping of each clade to its column position."""
        depths = tree.depths()
        # If there are no branch lengths, assume unit branch lengths
        if not max(depths.values()):
            depths = tree.depths(unit_branch_lengths=True)
            # Potential drawing overflow due to rounding -- 1 char per tree layer
        fudge_margin = int(math.ceil(math.log(len(taxa), 2)))
        cols_per_branch_unit = (drawing_width - fudge_margin) / float(
            max(depths.values())
        )

        return dict(
            (clade, int(blen * cols_per_branch_unit + 1.0) / 4)
            for clade, blen in depths.items()
        )

    def get_row_positions(tree):
        taxa = tree.get_terminals()
        positions = dict((taxon, 0.5 * idx) for idx, taxon in enumerate(taxa))

        def calc_row(clade):
            for subclade in clade:
                if subclade not in positions:
                    calc_row(subclade)
            positions[clade] = (
                positions[clade.clades[0]] + positions[clade.clades[-1]]
            ) // 2

        calc_row(tree.root)
        return positions

    def add_to_elements(clade, clade_id):
        children = clade.clades

        pos_x = col_positions[clade] * xlen
        pos_y = row_positions[clade] * ylen

        if clade.name == "D":
            label = None
        else:
            try:
                label = D.get_details("32", clade.name)
            except:
                label = clade.name

        cy_source = {
            "data": {
                "id": clade_id,
                "label": clade.name,
                "name": clade.name + ": " + label if label is not None else clade.name,
            },
            "position": {"x": pos_x, "y": pos_y},
            "classes": "nonterminal",
            # 'grabbable': grabbable
        }
        nodes.append(cy_source)

        if clade.is_terminal():
            # cy_source['data']['name'] = clade.name
            cy_source["data"]["name"] = (
                clade.name + ": " + label if label is not None else clade.name
            )
            cy_source["classes"] = "terminal"

        for n, child in enumerate(children):
            # The "support" node is on the same column as the parent clade,
            # and on the same row as the child clade. It is used to create the
            # 90 degree angle between the parent and the children.
            # Edge config: parent -> support -> child

            support_id = clade_id + "s" + str(n)
            child_id = clade_id + "c" + str(n)
            pos_y_child = row_positions[child] * ylen

            cy_support_node = {
                "data": {"id": support_id, "label": support_id},
                "position": {"x": pos_x, "y": pos_y_child},
                # 'grabbable': grabbable,
                "classes": "support",
            }

            cy_support_edge = {
                "data": {
                    "source": clade_id,
                    "target": support_id,
                    "sourceCladeId": clade_id,
                },
                # "classes": "support",
            }

            cy_edge = {
                "data": {
                    "source": support_id,
                    "target": child_id,
                    # 'length': clade.branch_length,
                    "length": 10,
                    "sourceCladeId": clade_id,
                },
            }

            if clade.confidence and clade.confidence.value:
                cy_source["data"]["confidence"] = clade.confidence.value

            nodes.append(cy_support_node)
            edges.extend([cy_support_edge, cy_edge])

            add_to_elements(child, child_id)

    col_positions = get_col_positions(tree)
    row_positions = get_row_positions(tree)

    nodes = []
    edges = []

    add_to_elements(tree.clade, "r")

    return nodes, edges
