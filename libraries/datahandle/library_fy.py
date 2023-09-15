####################################################################
#
# This file is part of libraries-2021 dataexplorer, https://nds.iaea.org/dataexplorer/.
# Copyright (C) 2022 International Atomic Energy Agency (IAEA)
#
# Contact:    nds.contact-point@iaea.org
#
####################################################################

import pandas as pd
import os

from datahandle.list import LIB_LIST_FY
from config import LIB_PATH_FY

# ------------------------------------------------------------------------------
# APP4: Fission Yield
#
def read_libfy(nuclide, inc_pt, mt, energy, fy_type):
    lib_list = LIB_LIST_FY

    if energy == "eV":
        en = "2.53E-08"  # less than 0.0253 eV
    elif energy == "keV":
        en = "0000.500"
    elif energy == "MeV":
        en = "0014.000"
    elif energy == "0":
        en = "0000.000"

    liblist = []
    libfiles = []
    dfs = []
    for lib in lib_list:
        if lib == "jeff3.3" and energy == "keV":
            en = "0000.400"
        elif energy == "keV":
            en = "0000.500"

        lfname = "".join(
            [
                LIB_PATH_FY,
                inc_pt,
                "/",
                nuclide,
                "/",
                lib,
                "/tables/FY/",
                inc_pt,
                "-",
                nuclide,
                "-MT",
                mt,
                "-E",
                en,
                ".",
                lib,
                ".txt"
            ]
        )

        if os.path.exists(lfname):
            # Library file name list for download
            liblist.append([lfname, lib])

            libfy_df = pd.read_csv(
                lfname,
                sep="\s+",
                index_col=None,
                header=None,
                comment="#",
                names=["Z", "A", "M", "FPY", "dFPY"],
            )
            libfy_df["lib"] = lib
            dfs.append(libfy_df)

    if dfs:
        libfy_df = pd.concat(dfs, ignore_index=True)

        # create Y(A) table
        libya_df = create_libYA(libfy_df, fy_type)

    else:
        libfy_df = pd.DataFrame()
        libya_df = pd.DataFrame()

    if liblist:
        libfiles = [i[0] for i in liblist]

    return libfiles, libya_df, libfy_df


def create_libYA(libfy_df, fytype):
    aa = []
    lib = libfy_df["lib"].unique()
    for l in lib:
        for a in range(60, 180):

            if fytype == "Independent":
                ay = libfy_df[(libfy_df["A"] == a) & (libfy_df["lib"] == l)][
                    "FPY"
                ].sum()
            if fytype == "Cumulative":
                ay = libfy_df[(libfy_df["A"] == a) & (libfy_df["lib"] == l)][
                    "FPY"
                ].max()

            d = {"A": a, "FPY": ay, "lib": l}
            aa.append(d)
        libya_df = pd.DataFrame(aa)
    return libya_df
