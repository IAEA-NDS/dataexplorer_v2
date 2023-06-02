import sys
import os
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker

DEVENV = True

if DEVENV:
    ## Application file location
    TOP_DIR = "/Users/okumuras/Dropbox/Development/dataexplorer2/"

    ## Dependent modules location
    MODULES_DIR = "/Users/okumuras/Dropbox/Development/"

    ## Data directory linked from the code
    DATA_DIR = "/Users/okumuras/Documents/nucleardata/EXFOR/"

    ## URLs to generate links inside the application
    BASE_URL = "http://127.0.0.1:8050/dataexplorer"
    API_BASE_URL = "http://127.0.0.1:5000/"


else:
    ## Application file location
    TOP_DIR = "/srv/www/dataexplorer2/"

    ## Dependent modules location
    MODULES_DIR = "/srv/data/dataexplorer2/"

    ## Data directory linked from the code
    DATA_DIR = "/srv/data/dataexplorer2/"

    ## URLs to generate links inside the application
    BASE_URL = "https://int-nds.iaea.org/dataexplorer2"
    API_BASE_URL = BASE_URL


MT_PATH_JSON = TOP_DIR + "libraries/datahandle/mf3.json"
MT50_PATH_JSON = TOP_DIR + "libraries/datahandle/mt50.json"
MAPPING_FILE = TOP_DIR + "exfor/datahandle/mapping.json"


EXFOR_DB = DATA_DIR + "exfor.sqlite"
ENDFTAB_DB = DATA_DIR + "endftables.sqlite"
MASTER_GIT_REPO_PATH = DATA_DIR + "exfor_master"
EXFORTABLES_PY_GIT_REPO_PATH = DATA_DIR + "exfortables_py"


## Package locations
EXFOR_PARSER = "exforparser/"
EXFOR_DICTIONARY = "exfor_dictionary/"
ENDF_TABLES = "endftables_sql/"
RIPL3 = "ripl3_json/"


sys.path.append(os.path.join(MODULES_DIR, EXFOR_PARSER))
sys.path.append(os.path.join(MODULES_DIR, EXFOR_DICTIONARY))
sys.path.append(os.path.join(MODULES_DIR, ENDF_TABLES))


MASTER_GIT_REPO_URL = "https://github.com/IAEA-NDS/exfor_master/"


""" Git  """
## In order to get EXFOR compilation history
owner = "IAEA-NDS"
repo = "exfor_master"
ref = "main"
api_token = ""


""" API """
HEADERS = {
    # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://127.0.0.1:5000",
    "content-type": "application/json",
    "X-CSRFToken": "",
}


""" SQL database """
engines = {
    "exfor": db.create_engine("sqlite:///" + EXFOR_DB),
    "endftables": db.create_engine("sqlite:///" + ENDFTAB_DB),
}

engine = db.create_engine("sqlite:///" + EXFOR_DB)  # , echo= True)


session = sessionmaker(autocommit=False, autoflush=True, bind=engines["exfor"])
session_lib = sessionmaker(autocommit=False, autoflush=True, bind=engines["endftables"])
