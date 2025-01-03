import os
import re
import sys

import pandas as pd
import plotly.figure_factory
from tqdm import tqdm

args = sys.argv[1:]

if args[0] == "sum":
    dirs = args[1:]
    lines = dict()
    valid_files = 0
    modes = []
    for dir in dirs:
        try:
            result = pd.read_csv(f"./pattern_usage/{dir}/result.csv")
            lines[dir] = result["lines"]
            valid_files = result["all files"][0]
            modes.append(result["mode"][0])
        except FileNotFoundError:
            lines[dir] = None
            modes.append(None)
    lines = pd.DataFrame(lines)

    summary = pd.DataFrame(
        columns=[
            "mode",
            "files",
            "percentage",
            "lines_mean",
            "lines_std",
            "lines_min",
            "lines_max",
        ]
    )
    for i, col in enumerate(lines.columns):
        if lines[col].isnull().all():
            summary.loc[col] = [None, 0, 0.0, None, None, None, None]
            continue
        stats = lines[col].dropna().describe()
        summary.loc[col] = [
            modes[i],
            lines[col].notna().sum(),
            float(lines[col].notna().sum()) / float(valid_files) * 100.0,
            stats["mean"],
            stats["std"],
            stats["min"],
            stats["max"],
        ]
    summary.to_csv(f"./pattern_usage/summary.csv", index=True)

    summary.index = summary.index.map(lambda x: x.split("/")[-1])
    fig = plotly.figure_factory.create_table(summary.round(2), index=True)
    fig.update_layout(title="Pattern Usage Summary", autosize=True, width=1000)
    fig.write_image(f"./pattern_usage/summary.png")

    print(f"Results saved to ./pattern_usage/summary.csv, ./pattern_usage/summary.png")
else:
    DIRECTORY = "../gitignore_dataset/ignores"
    PATTERN = str(args[0])
    NAME = args[1]

    print(f"Searching for pattern: {PATTERN}")

    res_dict = dict()
    valid_files = 0

    for pathname, dirnames, filenames in tqdm(os.walk(DIRECTORY), desc="Searching"):
        for filename in filenames:
            if not filename.endswith("gitignore"):
                continue
            filepath = os.path.join(pathname, filename)
            if os.path.isfile(filepath):
                with open(filepath, "r") as file:
                    try:
                        lines = dict()
                        for line_number, line in enumerate(file.read().splitlines()):
                            if PATTERN != "^#" and re.search(r"^#", line):
                                continue
                            orig = line
                            if PATTERN != "^\\!" and re.search(r"^\!", line):
                                line = line[1:]
                            if len(args) > 2:
                                if re.search(PATTERN, line) and all(
                                    not re.search(re.compile(arg), line)
                                    for arg in args[2:]
                                ):
                                    lines[line_number] = orig
                            else:
                                if re.search(PATTERN, line):
                                    lines[line_number] = orig
                        if lines:
                            res_dict[filepath.removeprefix(DIRECTORY)] = lines
                    except UnicodeDecodeError:
                        continue
            valid_files += 1

    if not res_dict:
        print("No matches found.")
        exit()

    if len(args) > 2 and args[2] == "dry":
        print(f"Found {len(res_dict)} matches in {valid_files} files.")
        exit()

    res = pd.DataFrame(res_dict.items(), columns=["file", "lines"])

    result = res.copy()
    result["mode"] = result["lines"].apply(lambda x: max(set(x.values()), key=list(x.values()).count))
    result["lines"] = result["lines"].apply(lambda x: len(x))
    result["all files"] = valid_files
    os.makedirs(f"./pattern_usage/{NAME}", exist_ok=True)
    result.to_csv(f"./pattern_usage/{NAME}/result.csv", index=False)

    samples = res.copy()
    samples.drop(columns=["file"], inplace=True)
    samples["lines"] = samples["lines"].apply(lambda x: list(x.values()))
    samples.to_csv(f"./pattern_usage/{NAME}/samples.csv", index=False)

    print(f"Results saved to ./pattern_usage/{NAME}")
