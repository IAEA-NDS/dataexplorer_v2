import json
import os
import pandas as pd

from exfor_dictionary.exfor_dictionary import Diction
from config import MAPPING_FILE, EXFOR_DICTIONARY


with open(MAPPING_FILE) as map_file:
    MAPPING = json.load(map_file)


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





