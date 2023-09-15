import pandas as pd
from collections import OrderedDict
from operator import getitem


from submodules.utilities.elem import elemtoz_nz
from exforparser.sql.models import Exfor_Bib, Exfor_Reactions, Exfor_Data, Exfor_Indexes
from config import session, engines
from common import energy_range_conversion, get_number_from_string, get_str_from_string
from sqlalchemy import func

connection = engines["exfor"].connect()

def get_exfor_bib_table():
    df = pd.read_sql_table("exfor_bib", connection)
    return df


def get_exfor_reactions_table():
    df = pd.read_sql_table("exfor_reactions", connection)
    return df


def get_exfor_indexes_table():
    df = pd.read_sql_table("exfor_index", connection)
    return df


########  -------------------------------------- ##########
##         Join table for AGGrid
########  -------------------------------------- ##########
def join_reaction_bib():
    connection = engines["exfor"].connect()
    all = (
        session()
        .query(
            Exfor_Reactions.entry,
            Exfor_Reactions.entry_id,
            Exfor_Reactions.target,
            Exfor_Reactions.projectile,
            Exfor_Reactions.process,
            Exfor_Reactions.sf4,
            Exfor_Reactions.sf6,
            Exfor_Bib.first_author,
            Exfor_Bib.first_author_institute,
            Exfor_Bib.title,
            Exfor_Bib.main_reference,
            Exfor_Bib.authors,
            Exfor_Bib.year,
            Exfor_Bib.main_facility_institute,
            Exfor_Bib.main_facility_type,
            func.min(Exfor_Indexes.e_inc_min).label("e_inc_min"),
            func.max(Exfor_Indexes.e_inc_max).label("e_inc_max"),
            # Exfor_Indexes.e_inc_min
        )
        .join(Exfor_Bib, Exfor_Bib.entry == Exfor_Reactions.entry)
        .join(Exfor_Indexes, Exfor_Indexes.entry_id == Exfor_Reactions.entry_id, isouter = True)
        .group_by(Exfor_Reactions.entry_id)
        .order_by(Exfor_Bib.year.desc())
    )

    df = pd.read_sql(
        sql=all.statement,
        con=connection,
    )

    return df



def join_index_bib():
    connection = engines["exfor"].connect()
    all = (
        session()
        .query(
            Exfor_Indexes.entry_id,
            Exfor_Indexes.target,
            Exfor_Indexes.process,
            Exfor_Indexes.residual,
            Exfor_Indexes.e_inc_min,
            Exfor_Indexes.e_inc_max,
            Exfor_Indexes.sf5,
            Exfor_Indexes.sf6,
            Exfor_Indexes.sf7,
            Exfor_Indexes.sf8,
            Exfor_Bib.entry,
            Exfor_Bib.authors,
            Exfor_Bib.year,
            Exfor_Bib.main_facility_institute,
            Exfor_Bib.main_facility_type,
        )
        .join(Exfor_Bib, Exfor_Bib.entry == Exfor_Indexes.entry)
        .order_by(Exfor_Bib.year.desc())
    )
    
    df = pd.read_sql(
        sql=all.statement,
        con=connection,
    )

    return df




def reaction_query_simple(type, elem, mass, reaction, branch):
    # https://zenn.dev/shimakaze_soft/articles/6e5e47851459f5
    connection = engines["exfor"].connect()
    target = elemtoz_nz(elem) + "-" + elem.upper() + "-" + mass

    queries = [
        Exfor_Indexes.target == target,
        Exfor_Indexes.process == reaction.upper(),
        Exfor_Indexes.sf6 == type.upper(),
        Exfor_Indexes.arbitrary_data == False,
    ]

    if branch == "PAR":
        queries.append(Exfor_Indexes.sf5 == branch)

    elif isinstance(branch, int):
        queries.append(Exfor_Indexes.level_num == branch)

    reac = (
        session()
        .query(Exfor_Indexes, Exfor_Bib)
        .filter(*queries)
        .join(Exfor_Bib, Exfor_Indexes.entry == Exfor_Bib.entry, isouter=True)
        .distinct()
    )

    df = pd.read_sql(
        sql=reac.statement,
        con=connection,
    )
    # print(df)
    return df




def index_query_by_bib(entries):
    queries = [Exfor_Indexes.entry.in_(tuple(entries))]
    # bib = session().query(Exfor_Indexes).filter().all()

    indexes = session().query(Exfor_Indexes).filter(*queries)
    df = pd.read_sql(
        sql=indexes.statement,
        con=connection,
    ) 

    return df





########  -------------------------------------- ##########
##         Reaction queries for the dataexplorer
########  -------------------------------------- ##########


def reaction_query(type, elem, mass, reaction, branch=None, rp_elem=None, rp_mass=None):
    # https://zenn.dev/shimakaze_soft/articles/6e5e47851459f5
    # print("reaction_query")
    reac = None
    target = elemtoz_nz(elem) + "-" + elem.upper() + "-" + mass

    queries = [Exfor_Indexes.target == target, Exfor_Indexes.arbitrary_data == False]

    if branch:
        if branch == "PAR":
            queries.append(Exfor_Indexes.sf5 == branch)

        elif isinstance(branch, int):
            queries.append(Exfor_Indexes.sf5 == "PAR")
            queries.append(Exfor_Indexes.level_num == branch)

        elif type == "FY":
            queries.append(Exfor_Indexes.sf5 == branch.upper())

    else:
        queries.append(Exfor_Indexes.sf5 == None)

    if type == "Residual":
        type = "SIG"

        if rp_mass.endswith(("m", "M", "g", "G")):
            residual = (
                rp_elem.capitalize()
                + "-"
                + str(get_number_from_string(rp_mass))
                + "-"
                + get_str_from_string(str(rp_mass)).upper()
            )

        else:
            residual = rp_elem.capitalize() + "-" + str(rp_mass)

        queries.append(Exfor_Indexes.projectile == reaction.upper())
        queries.append(Exfor_Indexes.residual == residual)

    else:
        queries.append(Exfor_Indexes.process == reaction.upper())
        queries.append(Exfor_Indexes.sf7 == None)
        queries.append(Exfor_Indexes.sf8 == None)


        if not any(r in reaction for r in ("tot", "f")):
            queries.append(~Exfor_Indexes.sf4.endswith("-G"))
            queries.append(~Exfor_Indexes.sf4.endswith("-M"))

    queries.append(Exfor_Indexes.sf6 == type.upper())
    reac = session().query(Exfor_Indexes).filter(*queries).all()

    entries = {}
    # sum_points = 0
    if reac:
        for ent in reac:
            entries[ent.entry_id] = {
                "e_inc_min": ent.e_inc_min,
                "e_inc_max": ent.e_inc_max,
                "points": ent.points,
                "sf5": ent.sf5,
                "sf8": ent.sf8,
                "x4_code": ent.x4_code,
            }
            # sum_points += ent.points

        # entries["total_points"] = sum_points

    return entries




def get_entry_bib(entries):
    bib = session().query(Exfor_Bib).filter(Exfor_Bib.entry.in_(tuple(entries))).all()

    legend = {}

    for b in bib:
        legend[b.entry] = {
            "author": b.first_author,
            "year": b.year if b.year else 1900,  ## Comments SO: should be int in SQL
        }

    return OrderedDict(
        sorted(legend.items(), key=lambda x: getitem(x[1], "year"), reverse=True),
    )




def data_query(entids, branch=None):
    connection = engines["exfor"].connect()
    queries = [Exfor_Data.entry_id.in_(tuple(entids))]

    if branch:
        if isinstance(branch, int):
            queries.append(Exfor_Data.level_num == branch)

    data = session().query(Exfor_Data).filter(*queries)

    df = pd.read_sql(
        sql=data.statement,
        con=connection,
    )

    return df


######## -------------------------------------- ########
#    Queries for FY
######## -------------------------------------- ########


def fy_branch(branch):
    if branch == "PRE":
        return ["PRE", "TER", "QTR", "PRV", "TER/CHG"]

    if branch == "IND":
        return ["IND", "SEC", "MAS", "CHG", "SEC/CHN"]

    if branch == "CUM":
        return ["CUM", "CHN"]


def reaction_query_fy(
    type, elem, mass, reaction, branch, mesurement_opt_fy, energy_range
):
    # https://zenn.dev/shimakaze_soft/articles/6e5e47851459f5

    target = elemtoz_nz(elem) + "-" + elem.upper() + "-" + mass
    lower, upper = energy_range_conversion(energy_range)

    reac = (
        session()
        .query(Exfor_Indexes)
        .filter(
            Exfor_Indexes.target == target,
            Exfor_Indexes.process == reaction.upper(),
            Exfor_Indexes.sf5.in_(tuple(fy_branch(branch))),
            Exfor_Indexes.sf6 == type.upper(),
            Exfor_Indexes.e_inc_min >= lower,
            Exfor_Indexes.e_inc_max <= upper,
            Exfor_Indexes.arbitrary_data == False,
            (
                Exfor_Indexes.sf4 == "MASS"
                if mesurement_opt_fy == "A"
                else Exfor_Indexes.sf4 == "ELEM"
                if mesurement_opt_fy == "Z"
                else Exfor_Indexes.sf4.isnot(None)
            ),
        )
        .all()
    )

    entries = {}

    for ent in reac:
        entries[ent.entry_id] = {
            "e_inc_min": ent.e_inc_min,
            "e_inc_max": ent.e_inc_max,
            "points": ent.points,
            "sf8": ent.sf8,
            "residual": ent.residual,
            "x4_code": ent.x4_code,
        }

    return entries


def reaction_query_fission(type, elem, mass, reaction, branch, energy_range):
    # https://zenn.dev/shimakaze_soft/articles/6e5e47851459f5
    sf4 = None
    sf5 = None
    sf6 = None
    target = elemtoz_nz(elem) + "-" + elem.upper() + "-" + mass

    queries = [
        Exfor_Indexes.target == target,
        Exfor_Indexes.process == reaction.upper(),
        Exfor_Indexes.arbitrary_data == False,
    ]

    if branch == "nu_n":
        sf5 = ["PR"]
        sf6 = ["NU"]
    elif branch == "nu_g":
        sf4 = "0-G-0"
        sf5 = ["PR"]
        sf6 = ["FY"]
    elif branch == "dn":
        sf5 = ["DL"]
        sf6 = ["NU"]
    elif branch == "pfns":
        sf5 = ["PR"]
        sf6 = ["NU/DE"]
    elif branch == "pfgs":
        sf4 = "0-G-0"
        sf5 = ["PR"]
        sf6 = ["FY/DE"]
    else:
        ## to avoid large query
        return None, None

    if sf4:
        queries.append(Exfor_Indexes.sf4 == sf4)

    if sf5:
        queries.append(Exfor_Indexes.sf5.in_(tuple(sf5)))

    if sf6:
        queries.append(Exfor_Indexes.sf6.in_(tuple(sf6)))

    if energy_range:
        lower, upper = energy_range_conversion(energy_range)
        queries.append(Exfor_Indexes.e_inc_min >= lower)
        queries.append(Exfor_Indexes.e_inc_max <= upper)

    reac = session().query(Exfor_Indexes).filter(*queries).all()

    entids = {}
    entries = []

    for ent in reac:
        entids[ent.entry_id] = {
            "e_inc_min": ent.e_inc_min,
            "e_inc_max": ent.e_inc_max,
            "points": ent.points,
            "sf5": ent.sf5,
            "sf8": ent.sf8,
            "x4_code": ent.x4_code,
        }
        entries += [ent.entry]
    # print(entids)

    return entids, entries


### facility query


def facility_query(facility_code, facility_type):
    # https://zenn.dev/shimakaze_soft/articles/6e5e47851459f5
    connection = engines["exfor"].connect()

    queries = [
        Exfor_Indexes.main_facility_institute == facility_code,
        Exfor_Indexes.main_facility_type == facility_type.upper(),
    ]

    reac = (
        session()
        .query(Exfor_Indexes, Exfor_Bib)
        .filter(*queries)
        .join(Exfor_Bib, Exfor_Indexes.entry == Exfor_Bib.entry, isouter=True)
        .distinct()
    )

    df = pd.read_sql(
        sql=reac.statement,
        con=connection,
    )
    # print(df)
    return df
