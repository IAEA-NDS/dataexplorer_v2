import json
import os
import pandas as pd

from exfor_dictionary import Diction
from config import engines, MAPPING_FILE, MODULES_DIR, EXFOR_PARSER
from libraries.datahandle.list import read_mt_json

with open(MAPPING_FILE) as map_file:
    MAPPING = json.load(map_file)


connection = engines["exfor"].connect()


def _load_instloc():
    institute_df = pd.read_pickle(
        os.path.join(MODULES_DIR, EXFOR_PARSER, "pickles/institute.pickle")
    )
    return institute_df


def _load_bib():
    df = pd.read_sql_table("exfor_bib", connection)
    return df


def _load_reactions():
    df = pd.read_sql_table("exfor_reactions", connection)
    return df


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


country_dict = dict3_to_country()
facilities_dict = get_facility_type()
institute_df = _load_instloc()
bib_df = _load_bib()
reaction_list = read_mt_json()
