import glob
import re
import pandas as pd
import subprocess
import os
import pickle

import numpy as np
from matplotlib import pyplot as plt
import japanize_matplotlib
import seaborn as sns
import warnings

warnings.filterwarnings("ignore")

if __name__ == "__main__":
    data_list: list[dict] = []
    dec = []
    if os.path.exists("./inspection_dump.pkl"):
        with open("./inspection_dump.pkl", "rb") as f:
            data_list = pickle.load(f)
            dec = [data["dec"] for data in data_list if data["dec"] > 0]
    else:
        ok = 0
        data_list = []
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
                            # if num > 0:
                            #     print(f"{case}: {process} {num}")
                            if (
                                not re.match(
                                    r"^Lines reduced by (.+) process: (\d+)$", line
                                )
                                is None
                            ):
                                data[process] = num
                            if data.get("max") is None or data["max"][1] < num:
                                data["max"] = (process, num)
                data_list.append(data)

        with open("./inspection_dump.pkl", "wb") as f:
            pickle.dump(data_list, f)

        dec = [data["dec"] for data in data_list if data["dec"] > 0]

        print(f"ok: {ok}, err: {err}, total: {ok + err}, rate: {ok / (ok + err)}")
        print(f"dec: {len(dec)}, rate: {len(dec) / ok}")

        print(f"top: {sorted(dec, reverse=True)[:10 if len(dec) > 10 else len(dec)]}")
        print(pd.Series(dec).describe())

    processes = ["preprocess", "containment", "re_include", "merge", "postprocess"]
    colors = sns.color_palette("Set1", n_colors=len(processes), desat=0.75)
    markers = ["*", "o", "D", "v", "s"]
    hatches = ["*", "x", "+", "O", "."]

    for process in processes:
        print(f"{process}:")
        print(
            pd.Series(
                [
                    data[process]
                    for data in data_list
                    if not data.get(process) is None and data[process] > 0
                ]
            ).describe()
        )

    # 凡例設定
    plt.rcParams["legend.fancybox"] = False  # 丸角OFF
    plt.rcParams["legend.framealpha"] = 1  # 透明度の指定、0で塗りつぶしなし
    plt.rcParams["legend.edgecolor"] = "black"  # edgeの色を変更

    # 共通のプロット領域設定
    left = 0.15  # 左端の位置 (0〜1, 図全体に対する割合)
    width = 0.8  # プロット領域の幅 (0〜1)
    bottom = 0.15  # 下端の位置
    height = 0.8  # プロット領域の高さ

    fig_dec = plt.figure(dpi=300, figsize=(1.414 * 5, 5))
    ax1 = fig_dec.add_axes([left, bottom, width, height])
    n, bins, patches = ax1.hist(
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
        edgecolor="black",
        linewidth=0.75,
    )
    for patch_set, hatch in zip(patches, hatches):
        for patch in patch_set.patches:
            patch.set_hatch(hatch)
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
    from matplotlib.patches import Rectangle

    leg = ax1.legend(
        [rf"{label}" for label in labels],
        fontsize=11,
    )
    for patch in leg.get_patches():
        patch.set_height(13)
        patch.set_y(-3)
    plt.savefig("./inspection/dec.png")
    plt.close()

    fig_dec_mem = plt.figure(dpi=300, figsize=(1.414 * 5, 5))
    ax1 = fig_dec_mem.add_axes([left, bottom, width, height])
    for process, color, marker in zip(processes, colors, markers):
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
            alpha=0.75,
            marker=marker,
        )
    ax1.set_xlabel(
        "削減された行数", labelpad=10, fontdict={"fontsize": 12, "fontweight": "bold"}
    )
    ax1.set_ylabel(
        r"$\boldsymbol{\times}$ : メモリ使用量（MB）",
        labelpad=10,
        fontdict={"fontsize": 12, "fontweight": "bold"},
    )
    # ax1.set_yscale("log")
    # ax1.set_yticks([0.1, 1, 10, 100, 1000, 10000])
    ax1.set_ylim(bottom=0)
    ax1.set_xticks(np.arange(0, max(dec) + 1, 1))
    ax1.xaxis.get_major_ticks()[0].label1.set_visible(False)
    plt.grid(ls=":", lw=0.5)
    labels = [
        "$\mathtt{"
        + ("RE\_INCLUDE" if process == "re_include" else process.upper())
        + "}$"
        for process in processes
    ]
    ax1.legend(
        [rf"{label}" for label in labels],
        fontsize=11,
    )
    plt.savefig("./inspection/dec_mem.png")
    plt.close()

    fig_dec_time = plt.figure(dpi=300, figsize=(1.414 * 5, 5))
    ax1 = fig_dec_time.add_axes([left, bottom, width, height])
    for process, color, marker in zip(processes, colors, markers):
        ax1.scatter(
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
            alpha=0.75,
            marker=marker,
        )
    ax1.set_xlabel(
        "削減された行数", labelpad=10, fontdict={"fontsize": 12, "fontweight": "bold"}
    )
    ax1.set_ylabel(
        r"$\boldsymbol{\bigcirc}$ : 実行時間（秒）",
        labelpad=10,
        fontdict={"fontsize": 12, "fontweight": "bold"},
    )
    # ax1.set_yscale("log")
    # ax1.set_yticks([0.001, 0.01, 0.1, 1, 10, 100])
    ax1.set_ylim(bottom=0)
    ax1.set_xticks(np.arange(0, max(dec) + 1, 1))
    ax1.xaxis.get_major_ticks()[0].label1.set_visible(False)
    plt.grid(ls=":", lw=0.5)
    labels = [
        "$\mathtt{"
        + ("RE\_INCLUDE" if process == "re_include" else process.upper())
        + "}$"
        for process in processes
    ]
    ax1.legend(
        [rf"{label}" for label in labels],
        fontsize=11,
    )
    plt.savefig("./inspection/dec_time.png")
    plt.close()

    fig_dirs_mem = plt.figure(dpi=300, figsize=(1.414 * 5, 5))
    ax1 = fig_dirs_mem.add_axes([left, bottom, width, height])
    for process, color, marker in zip(processes, colors, markers):
        ax1.scatter(
            [data["dirs"] / 1e6 for data in data_list if data["max"][0] == process],
            [data["memory"] / 1000 for data in data_list if data["max"][0] == process],
            s=50,
            color=color,
            alpha=0.75,
            marker=marker,
            zorder=1,
        )
    dirs = [data["dirs"] / 1e6 for data in data_list]
    p_mem = np.polyfit(dirs, [data["memory"] / 1000 for data in data_list], 1)
    p_time = np.polyfit(dirs, [data["time"] for data in data_list], 1)
    f_mem, f_time = np.poly1d(p_mem), np.poly1d(p_time)
    x = np.linspace(0, max(dirs) + 0.5, 100)
    ax1.plot(x, f_mem(x), color="black", linestyle="dashed", lw=1, alpha=0.2, zorder=0)
    ax1.set_yticks(np.arange(0, 1800 + 1, 200))
    ax1.set_xlim(0, max(dirs) + 0.5)
    ax1.xaxis.get_major_ticks()[0].label1.set_visible(False)
    ax1.set_ylim(bottom=0)
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
    plt.grid(ls=":", lw=0.5)
    labels = [
        "$\mathtt{"
        + ("RE\_INCLUDE" if process == "re_include" else process.upper())
        + "}$"
        for process in processes
    ]
    ax1.legend(
        [rf"{label}" for label in labels],
        fontsize=11,
    )
    plt.savefig("./inspection/dirs_mem.png")
    plt.close()

    fig_dirs_time = plt.figure(dpi=300, figsize=(1.414 * 5, 5))
    ax1 = fig_dirs_time.add_axes([left, bottom, width, height])
    for process, color, marker in zip(processes, colors, markers):
        ax1.scatter(
            [data["dirs"] / 1e6 for data in data_list if data["max"][0] == process],
            [data["time"] for data in data_list if data["max"][0] == process],
            s=50,
            color=color,
            alpha=0.75,
            marker=marker,
            zorder=1,
        )
    dirs = [data["dirs"] / 1e6 for data in data_list]
    p_mem = np.polyfit(dirs, [data["memory"] / 1000 for data in data_list], 1)
    p_time = np.polyfit(dirs, [data["time"] for data in data_list], 1)
    f_mem, f_time = np.poly1d(p_mem), np.poly1d(p_time)
    x = np.linspace(0, max(dirs) + 0.5, 100)
    ax1.plot(x, f_time(x), color="black", linestyle="dashed", lw=1, alpha=0.2, zorder=0)
    ax1.set_yticks(np.arange(0.0, 22.5 + 1, 2.5))
    ax1.set_xlim(0, max(dirs) + 0.5)
    ax1.xaxis.get_major_ticks()[0].label1.set_visible(False)
    ax1.set_ylim(bottom=0)
    ax1.set_xlabel(
        "ディレクトリ数（百万）",
        labelpad=10,
        fontdict={"fontsize": 12, "fontweight": "bold"},
    )
    ax1.set_ylabel(
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
    ax1.legend(
        [rf"{label}" for label in labels],
        fontsize=11,
    )
    plt.savefig("./inspection/dirs_time.png")
    plt.close()

    fig_dirs_dec = plt.figure(dpi=300, figsize=(1.414 * 5, 5))
    ax1 = fig_dirs_dec.add_axes([left, bottom, width, height])
    for process, color, marker in zip(processes, colors, markers):
        plt.scatter(
            [
                data["dirs"] / 1e6
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
            alpha=0.75,
            marker=marker,
        )
    plt.xlabel(
        "ディレクトリ数（百万）",
        labelpad=10,
        fontdict={"fontsize": 12, "fontweight": "bold"},
    )
    plt.ylabel(
        "削減された行数", labelpad=10, fontdict={"fontsize": 12, "fontweight": "bold"}
    )
    # plt.xscale("log")
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

    # fig_mem_time = plt.figure(dpi=300, figsize=(1.414 * 5, 5))
    # ax1 = fig_mem_time.add_axes([left, bottom, width, height])
    # for process, color in zip(processes, colors):
    #     plt.scatter(
    #         [data["memory"] / 1000 for data in data_list if data["max"][0] == process],
    #         [data["time"] for data in data_list if data["max"][0] == process],
    #         s=50,
    #         color=color,
    #         alpha=0.5,
    #     )
    # plt.xlabel(
    #     "メモリ使用量（MB）",
    #     labelpad=10,
    #     fontdict={"fontsize": 12, "fontweight": "bold"},
    # )
    # plt.ylabel(
    #     "実行時間（秒）", labelpad=10, fontdict={"fontsize": 12, "fontweight": "bold"}
    # )
    # plt.grid(ls=":", lw=0.5)
    # labels = [
    #     "$\mathtt{"
    #     + ("RE\_INCLUDE" if process == "re_include" else process.upper())
    #     + "}$"
    #     for process in processes
    # ]
    # plt.legend([rf"{label}" for label in labels], fontsize=11)
    # plt.savefig("./inspection/mem_time.png")
    # plt.close()
