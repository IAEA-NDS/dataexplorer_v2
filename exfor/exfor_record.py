import requests
import git

import sys

sys.path.append("../")
from config import MASTER_GIT_REPO_PATH, owner, repo, api_token, API_BASE_URL, HEADERS


# --------------------------------------------------------------- #
#             Record
# --------------------------------------------------------------- #
def get_record(entnum):
    url = API_BASE_URL + "exfor/entry/" + entnum

    try:
        r = requests.get(url, headers=HEADERS, verify=False)
        return r.json()

    except:
        raise Exception


def get_git_history(entnum):
    # Create a GitPython Repo object for the repository
    repo = git.Repo(MASTER_GIT_REPO_PATH)
    filepath = f"exforall/{entnum[0:3]}/{entnum}.x4"

    # Run the git log -p command for the file and capture the output
    output = repo.git.execute(["git", "log", "-p", "--", filepath])

    return output


def get_git_history_api(entnum):
    ## Get commit history from Github REST API
    path = f"exforall/{entnum[0:3]}/{entnum}.x4"
    commits = []
    page = 1
    while True:
        # e.g. https://api.github.com/repos/shinokumura/exfor_master/commits?path=exforall/224/22449.x4&page=1
        url = f"https://api.github.com/repos/{owner}/{repo}/commits?path={path}&page={page}"
        response = requests.get(url, headers={"Authorization": f"Token {api_token}"})
        if response.status_code != 200:
            print(f"Error: {response.status_code} {response.reason}")
            break
        new_commits = response.json()
        if len(new_commits) == 0:
            break
        commits += new_commits
        page += 1

    simple_history = {}

    for n in range(len(commits)):
        commit_dict = {
            "message": commits[n]["commit"]["message"],
            "sha": commits[n]["sha"],
            "html_url": commits[n]["html_url"],
            "api_url": commits[n]["url"],
        }
        simple_history[n] = commit_dict

    return simple_history


def compare_commits_api(entnum, commits):
    # Compare commits from Github REST API
    # https://api.github.com/repos/shinokumura/exfor_master/compare/c6dd95093cedb4be62e2814bb8d80ffccfed2713...0dda483cd04058da0c0dbcd4b72a7b07a42c7f56
    # 2 2005-03-24 c6dd95093cedb4be62e2814bb8d80ffccfed2713
    # Error: File not found in diff
    # 1 2006-06-16 0dda483cd04058da0c0dbcd4b72a7b07a42c7f56
    # Error: File not found in diff
    # 0 2006-07-20 5c5a62f3fe62dccc6542c2618557e77e468885ff
    path = f"exforall/{entnum[0:3]}/{entnum}.x4"

    if len(commits) == 1:
        print(f"Error: File does not have at least 2 commits")
        exit()

    for n in reversed(range(len(commits))):
        nth_sha = commits[n]["sha"]
        nplus1_sha = commits[n - 1]["sha"]

        url = f"https://api.github.com/repos/{owner}/{repo}/compare/{nth_sha}...{nplus1_sha}"
        response = requests.get(url, headers={"Authorization": f"Token {api_token}"})

        if response.status_code != 200:
            print(f"Error: {response.status_code} {response.reason}")
            exit()
        diff = response.json()

        for file_diff in diff["files"]:
            if file_diff["filename"] == path:
                return file_diff["patch"]
        else:
            ## Since earlier Commits contains most of the EXFOR entry and the Github REST API returns only top 300 files
            print("Error: File not found in diff")
