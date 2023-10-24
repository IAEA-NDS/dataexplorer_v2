####################################################################
#
# This file is part of libraries-2023 dataexplorer, https://nds.iaea.org/dataexplorer/.
# Copyright (C) 2022 International Atomic Energy Agency (IAEA)
#
# Contact:    nds.contact-point@iaea.org
#
####################################################################

import json
import os
import pandas as pd

from exfor_dictionary.exfor_dictionary import Diction
from config import MAPPING_FILE, EXFOR_DICTIONARY, MASTER_GIT_REPO_PATH


with open(MAPPING_FILE) as map_file:
    MAPPING = json.load(map_file)


with open(os.path.join(MASTER_GIT_REPO_PATH, "entry_updatedate.dat")) as ent_up_file:
    """
    read https://github.com/IAEA-NDS/exfor_master/blob/main/entry_updatedate.dat
    return df as follows
                entry last_commit  num_updates last_update
        7072   22403  2023-09-28            5  2023-09-28
        7078   22409  2023-09-28            4  2023-09-28
    """
    ent_update_df = pd.read_table(
        ent_up_file,
        sep="\s+",
        header=None,
        names=["entry", "last_commit", "num_updates"],
    )
    ent_update_df["last_update"] = pd.to_datetime(ent_update_df["last_commit"].str[:10])
    ent_update_df = ent_update_df.sort_values(by="last_update", ascending=False)


def get_institute_df():
    institute_df = pd.read_pickle(
        os.path.join(EXFOR_DICTIONARY, "pickles/institute.pickle")
    )
    return institute_df


def dict3_to_country():
    D = Diction(diction_num="3")
    institutes = D.get_diction()
    country_dict = {}

    for i in institutes:
        country_cd = i[1:4].strip()
        insttitute = i[4:].strip()

        if country_cd == insttitute and i != "3CHPCHP":
            country_dict[i[0:4]] = institutes[i]["description"]

    # df = pd.DataFrame(countries, columns=["country_code", "area_code", "country"])

    return country_dict


def get_institutes():
    D = Diction(diction_num="3")

    return D.get_diction()


def get_facility_type():
    D = Diction(diction_num="18")
    facilities = D.get_diction()
    facilities_dict = {}

    for i in facilities:
        facilities_dict[i] = facilities[i]["description"]

    return facilities_dict
