import glob
import os
import sys


def range_expand(pat: str):
    def cat(l, rg, r):
        res = []
        chars = []
        i = 0
        while i < len(rg):
            if rg[i] == "-":
                chars.extend(chr(x) for x in range(ord(rg[i - 1]), ord(rg[i + 1]) + 1))
                rg = rg[: i - 1] + rg[i + 2 :]
                i -= 2
            i += 1
        chars.extend(rg)
        chars = set(chars)
        for c in chars:
            res.append(l + c + r)
        return set(res)

    res = cat(
        pat[: pat.index("[")],
        pat[pat.index("[") + 1 : pat.index("]")],
        pat[pat.index("]") + 1 :],
    )
    while True:
        tmp = set()
        for p in res.copy():
            if "[" in p and "]" in p:
                res.remove(p)
                tmp |= cat(
                    p[: p.index("[")],
                    p[p.index("[") + 1 : p.index("]")],
                    p[p.index("]") + 1 :],
                )
        if not tmp:
            break
        res |= tmp
    return list(res)


def remove_containment(paths):
    paths = sorted(list(set(paths)))
    res = []
    for i in range(len(paths)):
        if any(
            paths[i].startswith(p + "/") or paths[i].startswith(p.lstrip("/") + "/")
            for p in paths[:i] + paths[i + 1 :]
        ):
            continue
        res.append(paths[i])
    return sorted(list(set(res)))


def remove_slash(paths):
    for i in range(len(paths)):
        if paths[i].endswith("/") and paths[i] != "/":
            paths[i] = paths[i][:-1]
        if paths[i].startswith("/") and "/" in paths[i][1:]:
            paths[i] = paths[i][1:]
    return paths


def simulate(path, file):
    os.makedirs("./validate_tmp")
    os.system(f"unzip -qq {path} -d ./validate_tmp")
    root = "./validate_tmp"
    paths = [
        path_child.removeprefix(root)
        for path_child in glob.glob(
            f"{root}/*", recursive=True, include_hidden=True
        )
    ]
    paths = remove_slash(paths)
    for line in file:
        line = line.strip()
        if line == "" or line.startswith("#"):
            continue
        if line.startswith("!"):
            if not line[1:] in paths:
                paths.append("/" + line[1:])
        paths = remove_slash(paths)
        line_expanded = range_expand(line) if "[" in line else [line]
        line_expanded = remove_slash(line_expanded)
        for l in line_expanded:
            paths = [
                p
                for p in paths
                if not (
                    p.endswith(l)
                    or (
                        "*" in l
                        and (
                            (
                                p.startswith(l[: l.index("*")])
                                and p.endswith(l[l.index("*") + 1 :])
                            )  # a*.txt
                            or not "/"
                            in p.removeprefix(
                                l[: l.rindex("*")]
                            )  # a/b/*
                        )
                    )
                )
            ]
    # print(paths)
    os.system("rm -rf ./validate_tmp")
    return remove_containment(paths)


def is_valid(path, original, refactored):
    return simulate(path, original) == simulate(path, refactored)

if __name__ == "__main__":
    if os.path.exists("./validate_tmp"):
        os.system("rm -rf ./validate_tmp")

    args = sys.argv
    target = None if len(args) == 1 else args[1]

    flag = False
    for case in glob.glob("./result/*") if target is None else glob.glob(f"./result/{target}"):
        if len(glob.glob(case + "/err")) != 0:
            continue
        else:
            with open(case + "/path") as fp:
                path = fp.readline().strip()    # restored zip file path
                with open(case + "/original.gitignore") as fo:
                    original = list(
                        map(lambda l: l.strip().rstrip("\n"), fo.readlines())
                    )
                    with open(case + "/refactored.gitignore") as fr:
                        refactored = list(
                            map(lambda l: l.strip().rstrip("\n"), fr.readlines())
                        )
                        fr.close()
                    fo.close()
                fp.close()
            if original != refactored:
                if not is_valid(path, original, refactored):
                    flag = True
                    print("----------------------------------------")
                    print(f"Invalid refactoring: {case}")
                    print("path: ", path)
                    print("original: ", original)
                    print("refactored: ", refactored)
                    print("original_result: ", simulate(path, original))
                    print("refactored_result: ", simulate(path, refactored))
    if not flag:
        print("All refactored gitignore files are valid.")
