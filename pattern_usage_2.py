import os
import re
import sys

import pandas as pd
import plotly.figure_factory
from tqdm import tqdm

file = sys.argv[1]
args = sys.argv[2:]

if args[0] == "sum":
    dirs = args[1:]
    lines = dict()
    valid_files = 0
    all_freq = []
    freq = []
    modes = []
    for dir in dirs:
        try:
            result = pd.read_csv(f"./pattern_usage_2/{dir}/result.csv")
            lines[dir] = result["lines"]
            valid_files = result["all files"][0]
            all_freq.append(result["all freq"][0])
            freq.append(result["freq"].sum())
            modes.append(result["mode"].mode()[0])
        except FileNotFoundError:
            lines[dir] = None
            modes.append(None)
            all_freq.append(None)
            freq.append(None)
    lines = pd.DataFrame(lines)

    summary = pd.DataFrame(
        columns=[
            "mode",
            "files",
            "file_pct",
            "freq_pct",
            "lines_mean",
            "lines_std",
            "lines_min",
            "lines_max",
        ]
    )
    for i, col in enumerate(lines.columns):
        if lines[col].isnull().all():
            summary.loc[col] = [None, 0, 0.0, 0.0, None, None, None, None]
            continue
        stats = lines[col].dropna().describe()
        summary.loc[col] = [
            modes[i],
            lines[col].notna().sum(),
            float(lines[col].notna().sum()) / float(valid_files) * 100.0,
            float(freq[i]) / float(all_freq[i]) * 100.0,
            stats["mean"],
            stats["std"],
            stats["min"],
            stats["max"],
        ]
    summary.to_csv(f"./pattern_usage_2/summary.csv", index=True)

    summary.index = summary.index.map(lambda x: x.replace("/", "/<br>"))
    fig = plotly.figure_factory.create_table(summary.round(2), index=True)
    fig.update_layout(title="Pattern Usage Summary", autosize=True, width=1000)
    fig.write_image(f"./pattern_usage_2/summary.png")

    print(
        f"Results saved to ./pattern_usage_2/summary.csv, ./pattern_usage_2/summary.png"
    )
else:
    DIRECTORY = file
    PARENT = str(args[0])
    PATTERN = str(args[1])
    NAME = args[2]

    print(f"Searching for pattern: {PATTERN}")

    res_dict = dict()
    valid_files = 0
    valid_parents = 0
    all_freq = 0
    freq_list = []

    for pathname, dirnames, filenames in tqdm(os.walk(DIRECTORY), desc="Searching"):
        for filename in filenames:
            if not filename.endswith("gitignore"):
                continue
            filepath = os.path.join(pathname, filename)
            freq = 0
            if os.path.isfile(filepath):
                with open(filepath, "r") as file:
                    try:
                        lines = dict()
                        for line_number, line in enumerate(file.read().splitlines()):
                            if PATTERN != "^#" and re.search(r"^#", line):
                                continue
                            orig = line
                            if not PATTERN.startswith("^\\!") and re.search(r"^\!", line):
                                line = line[1:]
                            if len(args) > 3 and args[3] != "multi":
                                if re.search(PATTERN, line) and all(
                                    not re.search(re.compile(arg), line)
                                    for arg in args[3:]
                                ):
                                    lines[line_number] = orig
                                    freq += len(re.findall(PATTERN, line))
                            elif len(args) > 3 and args[3] == "multi":
                                if re.search(PATTERN, line) or any(
                                    re.search(re.compile(arg), line) for arg in args[4:]
                                ):
                                    lines[line_number] = orig
                                    freq += len(re.findall(PATTERN, line))
                                    freq += sum(
                                        [
                                            len(re.findall(re.compile(arg), line))
                                            for arg in args[4:]
                                        ]
                                    )
                            else:
                                if re.search(PATTERN, line):
                                    lines[line_number] = orig
                                    freq += len(re.findall(PATTERN, line))
                            if re.search(PARENT, line):
                                all_freq += len(re.findall(PARENT, line))
                        if lines:
                            tmp = len(res_dict)
                            res_dict[filepath.removeprefix(DIRECTORY)] = lines
                            if tmp != len(res_dict):
                                freq_list.append(freq)
                    except UnicodeDecodeError:
                        continue
            valid_files += 1

    if not res_dict:
        print("No matches found.")
        exit()

    if len(args) > 3 and args[3] == "dry":
        print(f"Found {len(res_dict)} matches in {valid_files} files.")
        exit()

    res = pd.DataFrame(res_dict.items(), columns=["file", "lines"])

    result = res.copy()
    result["mode"] = result["lines"].apply(lambda x: max(set(x.values()), key=list(x.values()).count))
    result["lines"] = result["lines"].apply(lambda x: len(x))
    result["all files"] = valid_files
    result["all freq"] = all_freq
    result["freq"] = freq_list
    os.makedirs(f"./pattern_usage_2/{NAME}", exist_ok=True)
    result.to_csv(f"./pattern_usage_2/{NAME}/result.csv", index=False)

    samples = res.copy()
    samples.drop(columns=["file"], inplace=True)
    samples["lines"] = samples["lines"].apply(lambda x: list(x.values()))
    samples.to_csv(f"./pattern_usage_2/{NAME}/samples.csv", index=False)

    print(f"Results saved to ./pattern_usage_2/{NAME}")
