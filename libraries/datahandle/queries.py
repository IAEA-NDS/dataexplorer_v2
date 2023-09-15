import pandas as pd

from endftables_sql.models import (
    Endf_Reactions,
    Endf_XS_Data,
    Endf_Residual_Data,
    Endf_N_Residual_Data,
    Endf_FY_Data,
)
from config import session_lib, engines
from common import get_number_from_string, get_str_from_string

######## -------------------------------------- ########
#    Queries for endftables
######## -------------------------------------- ########


def lib_query(type, elem, mass, reaction, mt, rp_elem=None, rp_mass=None):
    target = elem + mass.zfill(3)
    queries = [
        Endf_Reactions.target == target,
        Endf_Reactions.projectile == reaction.split(",")[0].lower(),
    ]

    if type == "XS":
        # type = "xs"
        queries.append(Endf_Reactions.process == reaction.split(",")[1].upper())
        queries.append(
            Endf_Reactions.mt == mt
        )  # if mt is not None else Endf_Reactions.mt is not None)

    elif type == "Residual":
        if rp_mass.endswith(("m", "M", "g", "G")):
            residual = (
                rp_elem.capitalize()
                + str(get_number_from_string(rp_mass))
                + get_str_from_string(str(rp_mass)).lower()
            )

        else:
            residual = rp_elem.capitalize() + str(rp_mass)

        queries.append(Endf_Reactions.residual == residual)

    elif type == "FY":
        queries.append(Endf_Reactions.mt == mt)

    queries.append(Endf_Reactions.type == type.lower())
    ## Establish session to the endftable database
    reac = session_lib().query(Endf_Reactions).filter(*queries).all()

    libs = {}
    for r in reac:
        # print(r.reaction_id, r.evaluation, r.target, r.projectile, r.process, r.residual, r.mt)
        libs[r.reaction_id] = r.evaluation

    return libs


def lib_xs_data_query(ids):
    connection = engines["endftables"].connect()
    data = (
        session_lib()
        .query(Endf_XS_Data)
        .filter(Endf_XS_Data.reaction_id.in_(tuple(ids)))
    )

    df = pd.read_sql(
        sql=data.statement,
        con=connection,
    )

    return df


def lib_residual_data_query(inc_pt, ids):
    connection = engines["endftables"].connect()

    if inc_pt == "n":
        data = (
            session_lib()
            .query(Endf_N_Residual_Data)
            .filter(Endf_N_Residual_Data.reaction_id.in_(tuple(ids)))
        )
    else:
        data = (
            session_lib()
            .query(Endf_Residual_Data)
            .filter(Endf_Residual_Data.reaction_id.in_(tuple(ids)))
        )

    df = pd.read_sql(
        sql=data.statement,
        con=connection,
    )

    return df


def lib_data_query_fy(ids, en_lower, en_upper):
    connection = engines["endftables"].connect()
    data = (
        session_lib()
        .query(Endf_FY_Data)
        .filter(
            Endf_FY_Data.reaction_id.in_(tuple(ids)),
            # Endf_FY_Data.en_inc >= en_lower,
            # Endf_FY_Data.en_inc <= en_upper,
        )
    )

    df = pd.read_sql(
        sql=data.statement,
        con=connection,
    )

    return df
