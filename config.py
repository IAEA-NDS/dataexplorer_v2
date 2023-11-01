import os
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker
import site
import dash

DEVENV = False

if DEVENV:
    ## Application file location
    TOP_DIR = "/Users/okumuras/Dropbox/Development/dataexplorer2/"

    ## Data directory linked from the code
    DATA_DIR = "/Users/okumuras/Documents/nucleardata/EXFOR/"

    ## URLs to generate links inside the application
    # BASE_URL = "http://127.0.0.1:8050"
    API_BASE_URL = "http://127.0.0.1:5000/"


else:
    ## Application file location
    TOP_DIR = "/srv/www/dataexplorer2/"

    ## Data directory linked from the code
    DATA_DIR = "/srv/data/dataexplorer2/"

    ## URLs to generate links inside the application
    # BASE_URL = "https://int-nds.iaea.org"
    API_BASE_URL = "https://int-nds.iaea.org/api/"


## Package locations
# URL_PATH = dash.get_relative_path("/")
SITE_DIR = site.getsitepackages()[0]
EXFOR_PARSER = os.path.join(SITE_DIR, "exforparser")
EXFOR_DICTIONARY = os.path.join(SITE_DIR, "exfor_dictionary")
ENDF_TABLES = os.path.join(SITE_DIR, "endftables_sql")
RIPL3 = os.path.join(SITE_DIR, "ripl3_json")


## Define the location of files ussed in the interface
MT_PATH_JSON = os.path.join(EXFOR_PARSER, "tabulated/mf3.json")
MT50_PATH_JSON = os.path.join(EXFOR_PARSER, "tabulated/mt50.json")

MAPPING_FILE = os.path.join(TOP_DIR, "modules/exfor/mapping.json")
# MASS_RANGE_FILE = os.path.join(TOP_DIR, "submodules/utilities/A_min_max.txt")

## Define the location of data files
EXFOR_DB = os.path.join(DATA_DIR, "exfor.sqlite")
ENDFTAB_DB = os.path.join(DATA_DIR, "endftables.sqlite")
# ENDFTAB_DB = "/Users/okumuras/Desktop/endftables.sqlite"
MASTER_GIT_REPO_PATH = os.path.join(DATA_DIR, "exfor_master")
EXFOR_JSON_GIT_REPO_PATH = os.path.join(DATA_DIR, "exfor_json")
EXFORTABLES_PY_GIT_REPO_PATH = os.path.join(DATA_DIR, "exfortables_py")
ENDFTABLES_PATH = os.path.join(DATA_DIR, "libraries.all/")


MASTER_GIT_REPO_URL = "https://github.com/IAEA-NDS/exfor_master/"


""" Git  """
## In order to get EXFOR compilation history
owner = "IAEA-NDS"
repo = "exfor_master"
ref = "main"
keyFile = open(os.path.join(DATA_DIR, "key.txt"))
api_token = keyFile.readline().rstrip()


""" API """
# HEADERS = {
#     "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
#     # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)",
#     "X-Requested-With": "XMLHttpRequest",
#     "Referer": "https://127.0.0.1:5000",
#     "content-type": "application/json",
#     "X-CSRFToken": "",
# }
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.11 (KHTML, like Gecko) "
    "Chrome/23.0.1271.64 Safari/537.11",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
    "Accept-Encoding": "none",
    "Accept-Language": "en-US,en;q=0.8",
    "Connection": "keep-alive",
}

""" SQL database """
engines = {
    "exfor": db.create_engine("sqlite:///" + EXFOR_DB),
    "endftables": db.create_engine("sqlite:///" + ENDFTAB_DB),
}

# engine = db.create_engine("sqlite:///" + EXFOR_DB, echo=True)


session = sessionmaker(autocommit=False, autoflush=True, bind=engines["exfor"])
session_lib = sessionmaker(autocommit=False, autoflush=True, bind=engines["endftables"])
