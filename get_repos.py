import os, importlib

try:
    from git import Repo
    HAS_GIT = True
except ImportError:
    print("Couldn't find git, repos won't be cloned or updated if missing")
    HAS_GIT = False

BASE_PATH = "/repos/"

def make_pth(package: str):
    path = BASE_PATH + package + "/" + package

    with open(f'{package}.pth','w',encoding='utf-8') as file:
        file.write(path)
    print(package, "- created .pth file to", path)

def clone_repo(module: str, url: str):
    path = BASE_PATH + module

    if not os.path.exists(path):
        Repo.clone_from(url, path)
        print(module, "- Cloned from", url, "to", path)
    else:
        r = Repo(path).remotes.origin
        p = r.pull()
        if p[0].commit.hexsha != r.repo.head.commit.hexsha:
            print(module, "- pulled new commit: ", p[0].commit.summary)

def check_package(module: str, repo: str):
    try:
        importlib.import_module(module)
    except ModuleNotFoundError:
        print(module, "- Module not found")
        make_pth(module)
        if HAS_GIT:
            clone_repo(module, repo)

check_package("mlib", "Mmesek/mlib")
check_package("mdiscord", "Mmesek/mdiscord")
check_package("MFramework", "Mmesek/MFramework.py")
