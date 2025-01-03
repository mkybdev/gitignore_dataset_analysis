import glob
import os
import random
import subprocess
import re
import sys

N = None

directory = "../gitignore_dataset/restored/*"

if __name__ == "__main__":

    args = sys.argv
    target = None if len(args) == 1 else args[1]

    zip_paths = glob.glob(directory) if target is None else [f"../gitignore_dataset/restored/{target}.zip"]
    random.shuffle(zip_paths)

    if os.path.exists("./result"):
        os.system("rm -rf ./result")
    os.makedirs("./result")

    break_flag = False
    skip_count = 0
    count = 0
    for zip_path in zip_paths:
        num = os.path.basename(zip_path).split(".")[0]
        dir_path = "./result/tmp"
        os.makedirs(dir_path)
        os.system(f"unzip -qq {zip_path} -d {dir_path}")
        file_path = f"{dir_path}/.gitignore"
        target_path = f"./result/{num}"
        os.makedirs(target_path)
        with open(f"{target_path}/path", "w") as fp:
            fp.write(os.path.abspath(f"../gitignore_dataset/restored/{num}.zip"))
        res = subprocess.run(
            [
                "/usr/bin/time",
                "-f",
                "%M,%U",
                "refactorign",
                "-p",
                file_path,
                "-d",
                os.path.abspath(target_path),
                "-r",
            ],
            capture_output=True,
            text=True,
        )
        err = res.stderr
        if err != "":
            if re.match(r"^\d+", err):
                mem, time = err.split(",")
                with open(f"{target_path}/time", "w") as fp:
                    fp.write(time)
                with open(f"{target_path}/memory", "w") as fp:
                    fp.write(mem)
            else:
                if not err.startswith("Invalid pattern found. Aborting."):
                    print(f"{file_path}: {err}")
                with open(f"{target_path}/err", "w") as fe:
                    fe.write(err)
        count += 1
        with open(f"{target_path}/refactorign_report", "r") as frr:
            for line in frr:
                if re.match(r"^Lines reduced by [a-z]+ process: [1-9]", line):
                    print(num)
                    break
        if count % 100 == 0:
            print(f"Processed {count} files.")
        os.system("rm -rf ./result/tmp")
        if not N is None and count == N:
            break_flag = True
            break

    if not break_flag:
        print("Finished all the files.")

    print(f"Skipped {skip_count} files.")
