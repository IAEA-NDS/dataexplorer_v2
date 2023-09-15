####################################################################
#
# This file is part of libraries-2021 dataexplorer, https://nds.iaea.org/dataexplorer/.
# Copyright (C) 2022 International Atomic Energy Agency (IAEA)
#
# Contact:    nds.contact-point@iaea.org
#
####################################################################

import pandas as pd
import numpy as np
import os

from config import ENDFTABLES_PATH
from submodules.utilities.elem import elemtoz
from libraries.datahandle.list import LIB_LIST_MAX, LIB_LIST_RP

# ------------------------------------------------------------------------------
# APP2: Libraries
def read_libs(nuclide, slct_reac, mt, groupwise):
    lib_list = LIB_LIST_MAX
    reac = slct_reac.split(",")

    libs = {}

    for lib in lib_list:
        path = os.path.join(ENDFTABLES_PATH, reac[0],  nuclide, lib, "tables/xs/")
        filename = "".join(
            [
                reac[0],
                "-",
                nuclide,
                "-MT",
                mt,
                "-G1102."
                if (
                    "G" in groupwise
                    and mt in ["001", "002", "018", "102"]
                    and not nuclide.endswith("000")
                    and reac[0] == "n"
                )
                else ".",
                lib,
                ".txt"
            ]
        )

        lfname = os.path.join(path, filename)

        if os.path.exists(lfname):
            # Library file name list for download
            libs[lib] = lfname

    return libs

    # lib_df = create_libdf(liblist)

    # if liblist:
    #     libfiles = [i[0] for i in liblist]

    # return libfiles, lib_df


# ------------------------------------------------------------------------------
# APP3: Residual CS
#
#
def read_resid_prod_lib(nuclide, inc_pt, rp_elem, rp_mass):
    lib_list = LIB_LIST_RP
    rp_z = elemtoz(rp_elem)

    liblist = []
    libfiles = []
    for lib in lib_list:
        path = os.path.join([ENDFTABLES_PATH, inc_pt,nuclide, lib, "tables/residual/"])
        lfname = "".join([path, inc_pt, "-", nuclide, "-rp", rp_z, rp_mass, ".", lib, ".txt"])

        if os.path.exists(lfname):
            # Library file name list for download
            liblist.append([lfname, lib])

    lib_df = create_libdf(liblist)

    if liblist:
        libfiles = [i[0] for i in liblist]

    return libfiles, lib_df


def create_libdf(libfiles):
    dfs = []
    for lib, lfile in libfiles.items():

        try:  # due to null file such as g + S  33 : (g,a)
            lib_df = pd.read_csv(
                lfile,
                sep="\s+",
                index_col=None,
                header=None,
                usecols=[0, 1],
                comment="#",
                names=["en_inc", "data"],
            )
            lib_df["lib"] = lib
            dfs.append(lib_df)

            if lib_df["XS"].sum() == 0:
                lib_df.drop(lib_df[(lib_df["lib"] == lib)].index, inplace=True)

        except:
            continue

    if dfs:
        lib_df = pd.concat(dfs, ignore_index=True)
        lib_df["data"] *= 1e-3
        # lib_df["en_inc"] *= 1e6

    else:
        lib_df = pd.DataFrame()


    return lib_df



