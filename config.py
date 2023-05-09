import sqlalchemy as db
from sqlalchemy.orm import sessionmaker

DEVENV = True

if DEVENV:
    ## Data directory linked from the code
    TOP_DIR = "/Users/okumuras/Documents/nucleardata/EXFOR/"

    EXFOR_DB = TOP_DIR + "exfor.sqlite"
    ENDFTAB_DB = TOP_DIR + "endftables.sqlite"
    ## to generate URL inside the application
    BASE_URL = "http://127.0.0.1:8050/dataexplorer"
    API_BASE_URL = "http://127.0.0.1:5000/"

else:
    ## Data directory linked from the code
    TOP_DIR = "/srv/data/"
    EXFOR_DB =TOP_DIR + "dataexplorer2/exfor.sqlite"
    ENDFTAB_DB = TOP_DIR + "dataexplorer2/endftables.sqlite"

    ## to generate URL inside the application
    BASE_URL = "https://int-nds.iaea.org/dataexplorer2"
    API_BASE_URL = BASE_URL



## Local file location
MT_PATH_JSON = "libraries2023/datahandle/mf3.json"
MAPPING_FILE = "exfor/datahandle/mapping.json"


MASTER_GIT_REPO_PATH = TOP_DIR + "exfor_master"
EXFORTABLES_PY_GIT_REPO_PATH = TOP_DIR + "exfortables_py"

MASTER_GIT_REPO_URL = "https://github.com/IAEA-NDS/exfor_master/"
JSON_GIT_REPO_URL = "https://github.com/IAEA-NDS/exfor_json/"
TABLE_GIT_REPO_URL = "https://github.com/shinokumura/exfortables_py/"



""" Git  """
## In order to get EXFOR compilation history
owner = "shinokumura"
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
