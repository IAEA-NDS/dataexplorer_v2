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
import requests

from exfor_dictionary.exfor_dictionary import Diction
from config import EXFOR_DICTIONARY, MASTER_GIT_REPO_PATH, MASTER_GIT_REPO_URL, HEADERS

from submodules.exfor.queries import (
    get_exfor_bib_table,
    join_reaction_bib,
    join_index_bib,
)


bib_df = get_exfor_bib_table()
reactions_df = join_reaction_bib()
index_df = join_index_bib()  # which is heavy

number_of_entries = len(bib_df)
number_of_reactions = len(reactions_df)


MAPPING = {
    "top_category": {
        "SIG": "Cross Section (SIG)",
        "DA": "Angular Distribution (DA)",
        "DE": "Energy Distribution (DE)",
        "FY": "Fission Yield(FY)",
        "DDX": "Double Differential Cross Section (DA/DE)",
        "KE": "Kinetic Energy (KE)",
        "RES": "Resonance Parameter",
        "NU": "Neutron (NU)",
        "TTY": "Tick Target Yield (TTY)",
        "Others": "Others",
    },
    "SF6": {
        "AG": {"description": "Symmetry coefficient", "top_category": "Others"},
        "AH": {"description": "Asymmetry coefficient", "top_category": "Others"},
        "AKE": {"description": "Average kinetic energy", "top_category": "KE"},
        "ALF": {
            "description": "Alpha = capture/fission cross-section ratio",
            "top_category": "Others",
        },
        "AMP": {"description": "Scattering length", "top_category": "Others"},
        "AP": {
            "description": "Most probable mass of fission-fragments",
            "top_category": "FY",
        },
        "ARE": {"description": "Resonance-area", "top_category": "RES"},
        "D": {"description": "Average level-spacing", "top_category": "RES"},
        "DA": {"description": "Angular Distribution (DA)", "top_category": "DA"},
        "DA2": {
            "description": "Double-diff. by angle (for quadruple-diff cs only)",
            "top_category": "DDX",
        },
        "DA/DE": {"description": "Double-diff. cross section", "top_category": "DDX"},
        "DE": {"description": "Energy Distribution (E)", "top_category": "DE"},
        "DE2": {
            "description": "Double-diff. by energy (for quadruple-diff.cs only)",
            "top_category": "DDX",
        },
        "DEN": {
            "description": "Differential with incident energy",
            "top_category": "DE",
        },
        "DP": {
            "description": "Differential with lin.momentum of outgoing particles",
            "top_category": "Others",
        },
        "DT": {
            "description": "Diff.with 4-momentum transfer squared of outg.particles",
            "top_category": "Others",
        },
        "EN": {"description": "Resonance-energy", "top_category": "RES"},
        "ETA": {
            "description": "Average neutron yield per nonelastic event",
            "top_category": "Others",
        },
        "FM": {
            "description": "Product of polarization and cross section",
            "top_category": "SIG",
        },
        "FY": {"description": "Fission Yield", "top_category": "FY"},
        "INT": {
            "description": "Cross-section integral over incident energy",
            "top_category": "SIG",
        },
        "IPA": {
            "description": "Cs integrated over partial angular range",
            "top_category": "SIG",
        },
        "IPP": {
            "description": "Cs integrated over partial momentum range",
            "top_category": "SIG",
        },
        "J": {"description": "Spin J", "top_category": "RES"},
        "KE": {"description": "Kinetic Energy (KE, AKE)", "top_category": "KE"},
        "KEM": {
            "description": "Temperature of Maxwellian distr.of outgoing particles",
            "top_category": "EN",
        },
        "KEP": {
            "description": "Most probable kinetic energy of outgoing particle",
            "top_category": "KE",
        },
        "KER": {"description": "Kerma factor", "top_category": "Others"},
        "L": {"description": "Angular momentum L", "top_category": "RES"},
        "LD": {"description": "Level-density", "top_category": "Others"},
        "LDP": {"description": "Level-density parameter", "top_category": "Others"},
        "MLT": {
            "description": "Multiplicity (particle yield per event)",
            "top_category": "FY",
        },
        "NU": {"description": "Fission-neutron yield, nu-bar", "top_category": "NU"},
        "PHS": {"description": "Reich-Moore phase", "top_category": "SIG"},
        "PN": {
            "description": "Pn-value or delayed neutron emission probability",
            "top_category": "NU",
        },
        "POL": {"description": "Polarization", "top_category": "SIG"},
        "PTY": {"description": "Parity", "top_category": "SIG"},
        "PY": {"description": "Product yield", "top_category": "TTY"},
        "RAD": {"description": "Scattering radius", "top_category": "Others"},
        "RAT": {"description": "Ratio", "top_category": "Others"},
        "RED": {"description": "Reduced", "top_category": "Others"},
        "RI": {"description": "Resonance integral", "top_category": "SIG"},
        "RYL": {"description": "Reaction yield", "top_category": "TTY"},
        "SCO": {"description": "Spin cut-off factor", "top_category": "Others"},
        "SGV": {"description": "Thermonuclear reaction rate", "top_category": "Others"},
        "SIF": {"description": "Self-indication function", "top_category": "Others"},
        "SIG": {"description": "Cross Section (SIG)", "top_category": "SIG"},
        "SPC": {
            "description": "Intensity of discrete gamma-lines",
            "top_category": "Others",
        },
        "STF": {"description": "Strength function", "top_category": "Others"},
        "STR": {"description": "Strength", "top_category": "Others"},
        "SUM": {"description": "Sum", "top_category": "Others"},
        "SWG": {"description": "Statistical weight g", "top_category": "Others"},
        "TEM": {"description": "Nuclear temperature", "top_category": "KE"},
        "TKE": {"description": "Total kinetic energy", "top_category": "KE"},
        "TMP": {
            "description": "Temperature-dependent quantity",
            "top_category": "Others",
        },
        "TRN": {"description": "Transmission", "top_category": "Others"},
        "TTT": {
            "description": "Thick-target yield per unit time",
            "top_category": "TTY",
        },
        "TTY": {
            "description": "Thick-target yield of the specified reaction product.",
            "top_category": "TTY",
        },
        "TYA": {
            "description": "Differential with respect to Treiman-Yang angle",
            "top_category": "DA",
        },
        "WID": {"description": "Resonance width", "top_category": "RES"},
        "ZP": {
            "description": "Most probable charge of fission fragments",
            "top_category": "FY",
        },
    },
}


def get_latest_master_release():
    response = requests.get(
        f"{MASTER_GIT_REPO_URL.replace('github.com','api.github.com/repos')}releases/latest",
        verify=False,
        headers=HEADERS,
    )
    return response.json()["name"]


def get_updated_entries():
    with open(
        os.path.join(MASTER_GIT_REPO_PATH, "entry_updatedate.dat")
    ) as ent_up_file:
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
        ent_update_df["last_update"] = pd.to_datetime(
            ent_update_df["last_commit"].str[:10]
        )
        ent_update_df = ent_update_df.sort_values(by="last_update", ascending=False)

    return ent_update_df


ent_update_df = get_updated_entries()


def get_institute_df():
    institute_df = pd.read_pickle(
        os.path.join(EXFOR_DICTIONARY, "pickles/institute.pickle")
    )
    return institute_df


institute_df = get_institute_df()


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


def get_facility_types():
    D = Diction(diction_num="18")

    return D.get_diction()


def get_sf5():
    D = Diction(diction_num="31")

    return D.get_diction()


def get_sf7():
    D = Diction(diction_num="33")

    return D.get_diction()


def get_sf8():
    D = Diction(diction_num="34")

    return D.get_diction()


# unique incident particles
# ['N' 'D' 'P' 'A' 'G' '0' '3-LI-6' '5-B-11' '3-LI-7' '3-LI-8' '4-BE-7'
#  '4-BE-9' '4-BE-10' '5-B-12' '5-B-8' '22-TI-48' '6-C-12' '7-N-14' '6-C-13'
#  '8-O-18' '8-O-16' '14-SI-30' '9-F-19' '10-NE-20' '20-CA-48' '12-MG-24'
#  '8-O-19' '8-O-20' '8-O-21' '8-O-22' '8-O-23' '8-O-24' '5-B-10' '20-CA-42'
#  '20-CA-43' '20-CA-44' '20-CA-45' '20-CA-46' '20-CA-47' '20-CA-49'
#  '20-CA-50' '20-CA-51' '18-AR-40' 'HE3' '6-C-10' '27-CO-68' '12-MG-25'
#  '12-MG-33' '14-SI-34' '8-O-13' '19-K-39' '19-K-45' '19-K-47' '18-AR-36'
#  '18-AR-44' '11-NA-24-L' '16-S-34' '20-CA-40' '24-CR-52' '24-CR-54'
#  '7-N-15' '22-TI-50' '14-SI-28' '9-F-17' '12-MG-34' '13-AL-34' '6-C-16'
#  '6-C-15' '6-C-14' 'T' '80-HG-204' '10-NE-22' '20-CA-38' '17-CL-35'
#  '17-CL-37' '52-TE-138' '52-TE-137' '52-TE-136' '52-TE-135' '52-TE-134'
#  '51-SB-137' '51-SB-136' '51-SB-135' '51-SB-134' '51-SB-133' '51-SB-132'
#  '51-SB-131' '51-SB-130' '51-SB-129' '50-SN-135' '50-SN-134' '50-SN-133'
#  '50-SN-132' '50-SN-131' '50-SN-130' '50-SN-129' '50-SN-128' '50-SN-127'
#  '50-SN-126' '50-SN-123' '50-SN-122' '50-SN-121' '50-SN-119' '50-SN-115'
#  '50-SN-114' '50-SN-113' '49-IN-130' '49-IN-129' '49-IN-128' '49-IN-127'
#  '5-B-19' '9-F-27' '9-F-29' '11-NA-23' '3-LI-9' '2-HE-6' '2-HE-8'
#  '26-FE-56' '4-BE-11' '54-XE-136' '8-O-15' '27-CO-55' '7-N-17' '7-N-18'
#  '7-N-19' '7-N-20' '7-N-21' '7-N-22' '92-U-238' '28-NI-58' '16-S-36'
#  '36-KR-78' '36-KR-86' '40-ZR-94' '40-ZR-93' '11-NA-33' '41-NB-93'
#  '3-LI-11' '19-K-46' '10-NE-17' '12-MG-31' '7-N-12' '30-ZN-70' '36-KR-70'
#  '36-KR-71' '36-KR-72' '35-BR-71' 'AP' '6-C-9' '6-C-17' '6-C-18' '16-S-32'
#  '10-NE-30' '18-AR-35' '18-AR-34' '17-CL-33' '14-SI-27' '14-SI-26'
#  '14-SI-25' '6-C-20' '12-MG-36' '54-XE-124' '5-B-13' '5-B-15' '5-B-14'
#  '64-GD-156' '64-GD-160' '50-SN-108' '50-SN-124' '10-NE-19' '8-O-17'
#  '54-XE-129' '10-NE-29' '8-O-14' '6-C-19' '6-C-22' '21-SC-45' '28-NI-64'
#  '12-MG-32' 'PIP' 'PIN' '37-RB-98' '4-BE-12' '23-V-61' '14-SI-36'
#  '14-SI-38' '14-SI-40' '12-MG-28' '5-B-17' '11-NA-21' '10-NE-31'
#  '11-NA-32' '12-MG-37' '13-AL-25' '12-MG-30' '4-BE-14' '6-C-0' '6-C-11'
#  '34-SE-82' '9-F-18' '28-NI-60' '12-MG-26' '92-U-230' '15-P-31' '11-NA-22'
#  '50-SN-104' '50-SN-112' '82-PB-208' '24-CR-48' '26-FE-50' '20-CA-36'
#  '17-CL-45' '10-NE-21' '10-NE-23' '10-NE-24' '10-NE-25' '10-NE-26'
#  '10-NE-27' '10-NE-28' '10-NE-32' '16-S-28' '16-S-44' '13-AL-33'
#  '13-AL-35' '13-AL-36' '13-AL-23' '21-SC-51' '21-SC-52' '21-SC-53'
#  '21-SC-54' '21-SC-55' '26-FE-58' '36-KR-82' '18-AR-46' '12-MG-22'
#  '12-MG-35' '15-P-27' '16-S-43' '22-TI-54' '13-AL-27' '12-MG-23'
#  '30-ZN-68' '7-N-16' '9-F-21' '9-F-22' '9-F-23' '9-F-24' '9-F-25' '9-F-26'
#  '11-NA-27' '11-NA-28' '11-NA-29' '11-NA-30' '11-NA-31' '27-CO-59'
#  '28-NI-68' '32-GE-76' '13-AL-32' '29-CU-69' '30-ZN-72' '19-K-48'
#  '17-CL-46' '22-TI-56' '24-CR-60' '24-CR-62' '26-FE-66' '28-NI-70'
#  '23-V-51' '12-MG-20' '10-NE-18' '32-GE-70' '13-AL-24' '36-KR-84'
#  '54-XE-132' '7-N-13' '16-S-38' '16-S-30' '28-NI-57' '25-MN-55' '11-NA-26'
#  '11-NA-25' '12-MG-29' '13-AL-39' '13-AL-38' '13-AL-37' '13-AL-31'
#  '13-AL-30' '14-SI-39' '14-SI-37' '14-SI-35' '14-SI-33' '15-P-43'
#  '15-P-42' '15-P-41' '15-P-40' '15-P-39' '15-P-38' '15-P-37' '15-P-36'
#  '16-S-42' '16-S-41' '16-S-40' '16-S-39' '17-CL-44' '17-CL-43' '17-CL-42'
#  '18-AR-47' '18-AR-45' '32-GE-82' '42-MO-92' '13-AL-26' '15-P-28' 'E'
#  '92-U-234' '92-U-233' '92-U-232' '92-U-231' '91-PA-231' '91-PA-230'
#  '91-PA-229' '91-PA-228' '85-AT-205' '85-AT-206' '86-RN-205' '86-RN-206'
#  '86-RN-207' '86-RN-208' '86-RN-209' '87-FR-208' '87-FR-209' '87-FR-210'
#  '87-FR-211' '87-FR-212' '87-FR-216' '87-FR-217' '87-FR-218' '88-RA-210'
#  '88-RA-211' '88-RA-212' '88-RA-213' '88-RA-214' '88-RA-215' '88-RA-216'
#  '88-RA-217' '88-RA-218' '88-RA-219' '88-RA-220' '88-RA-221' '88-RA-222'
#  '88-RA-223' '89-AC-215' '89-AC-216' '89-AC-217' '89-AC-218' '89-AC-219'
#  '89-AC-220' '89-AC-221' '89-AC-222' '89-AC-223' '89-AC-224' '89-AC-225'
#  '89-AC-226' '90-TH-221' '90-TH-222' '90-TH-223' '90-TH-224' '90-TH-225'
#  '90-TH-226' '90-TH-227' '90-TH-228' '90-TH-229' '91-PA-226' '91-PA-227'
#  '91-PA-232' '91-PA-235' '92-U-235' '92-U-236' '92-U-237' '9-F-20'
#  '11-NA-24' '13-AL-28' '14-SI-29' '16-S-29' '9-F-18-L' '79-AU-197'
#  '22-TI-46' '18-AR-42' '15-P-26' '26-FE-52' '28-NI-56' '28-NI-52'
#  '28-NI-53' '28-NI-54' '28-NI-55' '26-FE-48' '26-FE-49' '26-FE-51'
#  '26-FE-53' '24-CR-44' '24-CR-45' '24-CR-46' '24-CR-47' '24-CR-49'
#  '27-CO-50' '27-CO-51' '27-CO-52' '27-CO-53' '27-CO-54' '25-MN-46'
#  '25-MN-47' '25-MN-48' '25-MN-49' '25-MN-50' '25-MN-51' '23-V-43'
#  '23-V-44' '23-V-45' '23-V-46' '23-V-47' '57-LA-139' '67-HO-165'
#  '29-CU-63' '32-GE-74']
