import glob
import re
import pandas as pd
import subprocess

import numpy as np
from matplotlib import pyplot as plt
import japanize_matplotlib
import seaborn as sns

if __name__ == "__main__":
    ok = 0
    data_list = []
    dec = []
    err = 0
    for case in glob.glob("./result/*"):
        if len(glob.glob(f"{case}/err")) != 0:
            err += 1
        else:
            ok += 1
            data = dict()
            with open(f"{case}/path") as fp:
                path = fp.readline().strip()
                res = subprocess.run(
                    ["unzip", "-t", path], capture_output=True, text=True
                )
                data["dirs"] = int(len(res.stdout.split("\n"))) - 2
                fp.close()
            with open(f"{case}/original.gitignore") as fo:
                original = fo.readlines()
                data["original"] = len(original)
                with open(f"{case}/refactored.gitignore") as fr:
                    refactored = fr.readlines()
                    data["dec"] = len(original) - len(refactored)
                    if original != refactored:
                        dec.append(data["dec"])
                    fr.close()
                fo.close()
            with open(f"{case}/time") as ft:
                data["time"] = float(ft.readline())
                ft.close()
            with open(f"{case}/memory") as fm:
                data["memory"] = int(fm.readline())
                fm.close()
            with open(f"{case}/refactorign_report") as frr:
                for line in map(str.strip, frr.readlines()):
                    els = re.match(r"Lines reduced by (.+) process: (\d+)", line)
                    if not els is None:
                        process, num = els.group(1), int(els.group(2))
                        data[process] = num
                        if data.get("max") is None or data["max"][1] < num:
                            data["max"] = (process, num)
            data_list.append(data)

    print(f"ok: {ok}, err: {err}, total: {ok + err}, rate: {ok / (ok + err)}")
    print(f"dec: {len(dec)}, rate: {len(dec) / ok}")

    print(f"top: {sorted(dec, reverse=True)[:10 if len(dec) > 10 else len(dec)]}")
    print(pd.Series(dec).describe())

    processes = ["preprocess", "containment", "re_include", "merge", "postprocess"]
    colors = sns.color_palette("Set1", n_colors=len(processes), desat=0.75)

    for process in processes:
        print(f"{process}:")
        print(
            pd.Series(
                [data[process] for data in data_list if data["dec"] > 0]
            ).describe()
        )

    # 軸設定
    plt.rcParams["xtick.direction"] = "in"  # x軸の目盛りの向き
    plt.rcParams["ytick.direction"] = "in"  # y軸の目盛りの向き
    plt.rcParams["xtick.top"] = True  # x軸の上部目盛り
    plt.rcParams["ytick.right"] = True  # y軸の右部目盛り

    # 凡例設定
    plt.rcParams["legend.fancybox"] = False  # 丸角OFF
    plt.rcParams["legend.framealpha"] = 1  # 透明度の指定、0で塗りつぶしなし
    plt.rcParams["legend.edgecolor"] = "black"  # edgeの色を変更

    # 共通のプロット領域設定
    left = 0.1  # 左端の位置 (0〜1, 図全体に対する割合)
    width = 0.8  # プロット領域の幅 (0〜1)
    bottom = 0.15  # 下端の位置
    height = 0.75  # プロット領域の高さ

    fig_dec = plt.figure(dpi=300, figsize=(1.414 * 5, 5))
    ax1 = fig_dec.add_axes([left, bottom, width, height])
    plt.hist(
        tuple(
            tuple(
                data["dec"]
                for data in data_list
                if data["max"][0] == process and data["dec"] > 0
            )
            for process in processes
        ),
        bins=max(dec),
        range=(0.5, max(dec) + 0.5),
        histtype="barstacked",
        color=colors,
    )
    plt.xticks(np.arange(1, max(dec) + 1, 1))
    plt.xlabel(
        "削減された行数",
        labelpad=10,
        fontdict={"fontsize": 12, "fontweight": "bold"},
    )
    plt.ylabel(
        "ファイル数", labelpad=10, fontdict={"fontsize": 12, "fontweight": "bold"}
    )
    plt.grid(ls=":", lw=0.5)
    labels = [
        "$\mathtt{"
        + ("RE\_INCLUDE" if process == "re_include" else process.upper())
        + "}$"
        for process in processes
    ]
    plt.legend([rf"{label}" for label in labels], fontsize=11)
    plt.savefig("./inspection/dec.png")
    plt.close()

    fig_dec_mem_time = plt.figure(dpi=300, figsize=(1.414 * 5, 5))
    ax1 = fig_dec_mem_time.add_axes([left, bottom, width, height])
    ax2 = ax1.twinx()
    for process, color in zip(processes, colors):
        ax1.scatter(
            [
                data["dec"]
                for data in data_list
                if data["max"][0] == process and data["dec"] > 0
            ],
            [
                data["memory"] / 1000
                for data in data_list
                if data["max"][0] == process and data["dec"] > 0
            ],
            s=50,
            color=color,
            alpha=0.5,
            marker="x",
        )
        ax2.scatter(
            [
                data["dec"]
                for data in data_list
                if data["max"][0] == process and data["dec"] > 0
            ],
            [
                data["time"]
                for data in data_list
                if data["max"][0] == process and data["dec"] > 0
            ],
            s=50,
            color=color,
            alpha=0.5,
            marker="o",
        )
    ax1.set_xlabel(
        "削減された行数", labelpad=10, fontdict={"fontsize": 12, "fontweight": "bold"}
    )
    ax1.set_ylabel(
        r"$\boldsymbol{\times}$ : メモリ使用量（MB）",
        labelpad=10,
        fontdict={"fontsize": 12, "fontweight": "bold"},
    )
    ax2.set_ylabel(
        r"$\boldsymbol{\bigcirc}$ : 実行時間（秒）",
        labelpad=10,
        fontdict={"fontsize": 12, "fontweight": "bold"},
    )
    ax1.set_yscale("log")
    plt.xticks(np.arange(0, max(dec) + 1, 1))
    plt.grid(ls=":", lw=0.5)
    labels = [
        "$\mathtt{"
        + ("RE\_INCLUDE" if process == "re_include" else process.upper())
        + "}$"
        for process in processes
    ]
    ax2.legend([rf"{label}" for label in labels], fontsize=11)
    plt.savefig("./inspection/dec_mem_time.png")
    plt.close()

    fig_dirs_mem_time = plt.figure(dpi=300, figsize=(1.5 * 5, 5))
    ax1 = fig_dirs_mem_time.add_axes([left, bottom, 0.6, height])
    ax2 = ax1.twinx()
    for process, color in zip(processes, colors):
        ax1.scatter(
            [data["dirs"] / 1e6 for data in data_list if data["max"][0] == process],
            [data["memory"] / 1000 for data in data_list if data["max"][0] == process],
            s=50,
            color=color,
            alpha=0.5,
            marker="x",
        )
        ax2.scatter(
            [data["dirs"] / 1e6 for data in data_list if data["max"][0] == process],
            [data["time"] for data in data_list if data["max"][0] == process],
            s=50,
            color=color,
            alpha=0.5,
            marker="o",
        )
    ax1.set_xlabel(
        "ディレクトリ数（百万）",
        labelpad=10,
        fontdict={"fontsize": 12, "fontweight": "bold"},
    )
    ax1.set_ylabel(
        r"$\boldsymbol{\times}$ : メモリ使用量（MB）",
        labelpad=10,
        fontdict={"fontsize": 12, "fontweight": "bold"},
    )
    ax2.set_ylabel(
        r"$\boldsymbol{\bigcirc}$ : 実行時間（秒）",
        labelpad=10,
        fontdict={"fontsize": 12, "fontweight": "bold"},
    )
    plt.grid(ls=":", lw=0.5)
    labels = [
        "$\mathtt{"
        + ("RE\_INCLUDE" if process == "re_include" else process.upper())
        + "}$"
        for process in processes
    ]
    ax2.legend(
        [rf"{label}" for label in labels],
        fontsize=11,
        loc="upper left",
        bbox_to_anchor=(1.1, 1.1),
    )
    plt.savefig("./inspection/dirs_mem_time.png")
    plt.close()

    fig_dirs_dec = plt.figure(dpi=300, figsize=(1.414 * 5, 5))
    ax1 = fig_dirs_dec.add_axes([left, bottom, width, height])
    for process, color in zip(processes, colors):
        plt.scatter(
            [
                data["dirs"]
                for data in data_list
                if data["max"][0] == process and data["dec"] > 0
            ],
            [
                data["dec"]
                for data in data_list
                if data["max"][0] == process and data["dec"] > 0
            ],
            s=50,
            color=color,
            alpha=0.5,
        )
    plt.xlabel(
        "ディレクトリ数",
        labelpad=10,
        fontdict={"fontsize": 12, "fontweight": "bold"},
    )
    plt.ylabel(
        "削減された行数", labelpad=10, fontdict={"fontsize": 12, "fontweight": "bold"}
    )
    plt.xscale("log")
    plt.yticks(np.arange(0, max(dec) + 1, 1))
    plt.grid(ls=":", lw=0.5)
    labels = [
        "$\mathtt{"
        + ("RE\_INCLUDE" if process == "re_include" else process.upper())
        + "}$"
        for process in processes
    ]
    plt.legend([rf"{label}" for label in labels], fontsize=11)
    plt.savefig("./inspection/dirs_dec.png")
    plt.close()

    fig_mem_time = plt.figure(dpi=300, figsize=(1.414 * 5, 5))
    ax1 = fig_mem_time.add_axes([left, bottom, width, height])
    for process, color in zip(processes, colors):
        plt.scatter(
            [data["memory"] / 1000 for data in data_list if data["max"][0] == process],
            [data["time"] for data in data_list if data["max"][0] == process],
            s=50,
            color=color,
            alpha=0.5,
        )
    plt.xlabel(
        "メモリ使用量（MB）",
        labelpad=10,
        fontdict={"fontsize": 12, "fontweight": "bold"},
    )
    plt.ylabel(
        "実行時間（秒）", labelpad=10, fontdict={"fontsize": 12, "fontweight": "bold"}
    )
    plt.grid(ls=":", lw=0.5)
    labels = [
        "$\mathtt{"
        + ("RE\_INCLUDE" if process == "re_include" else process.upper())
        + "}$"
        for process in processes
    ]
    plt.legend([rf"{label}" for label in labels], fontsize=11)
    plt.savefig("./inspection/mem_time.png")
    plt.close()
