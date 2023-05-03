import sqlalchemy as db
from sqlalchemy.orm import sessionmaker

DEVENV = True


if DEVENV:
    TOP_DIR = "/Users/okumuras/Documents/nucleardata/EXFOR/"
    MT_PATH = "libraries2022/datahandle/MT.dat"


else:
    TOP_DIR = "/srv/data/"
    MT_PATH = "/srv/www/exforpyplot/datahandle/MT.dat"


MT_PATH_JSON = "libraries2023/datahandle/mf3.json"
MAPPING_FILE = "exfor/datahandle/mapping.json"
MASTER_GIT_REPO_PATH = TOP_DIR + "exfor_master"
JSON_GIT_REPO_PATH = TOP_DIR + "exfor_json"
EXFORTABLES_PY_GIT_REPO_PATH = TOP_DIR + "exfortables_py"

MASTER_GIT_REPO_URL = "https://github.com/IAEA-NDS/exfor_master/"
JSON_GIT_REPO_URL = "https://github.com/IAEA-NDS/exfor_json/"
BASE_URL = "http://127.0.0.1:8050/dataexplorer"


""" Git  """
owner = "IAEA-NDS"
repo = "exfor_master"
ref = "main"
api_token = ""

""" API """
API_BASE_URL = "http://127.0.0.1:5000/"
HEADERS = {
    # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://127.0.0.1:5000",
    "content-type": "application/json",
    "X-CSRFToken": "",
}


""" SQL database """
EXFOR_DB = "/Users/okumuras/Dropbox/Development/exforparser/exfor.sqlite"
ENDFTAB_DB = "/Users/okumuras/Desktop/endftables.sqlite"

engines = {
    "exfor": db.create_engine("sqlite:///" + EXFOR_DB),
    "endftables": db.create_engine("sqlite:///" + ENDFTAB_DB),
}

engine = db.create_engine("sqlite:///" + EXFOR_DB)  # , echo= True)


session = sessionmaker(autocommit=False, autoflush=True, bind=engines["exfor"])
session_lib = sessionmaker(autocommit=False, autoflush=True, bind=engines["endftables"])
