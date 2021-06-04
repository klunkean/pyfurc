import subprocess
import os
import shutil
import urllib.request
from zipfile import ZipFile


def get_auto_archive(target_dir):
    zipname = "auto.zip"
    target_path = os.path.abspath(os.path.join(target_dir, zipname))
    url = "https://github.com/auto-07p/auto-07p/archive/refs/heads/master.zip"
    urllib.request.urlretrieve(url, target_path)
    return target_path


def unpack_auto_archive(archive_path, target_dir):
    zip_path, _ = os.path.split(archive_path)

    with ZipFile(archive_path, "r") as zip_ref:
        zip_ref.extractall(zip_path)
        auto_dir_name = zip_ref.infolist()[0].filename

    path_to_auto_dir = os.path.join(zip_path, auto_dir_name)

    os.rename(path_to_auto_dir, os.path.join(target_dir, "auto_07p"))
    return path_to_auto_dir

def run_sh_with_output(command, directory):
    proc = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=directory,
        universal_newlines=True,
    )

    for stdout_line in iter(proc.stdout.readline, ""):
        yield stdout_line.rstrip()
    proc.stdout.close()
    return_code = proc.wait()

    if return_code:
        raise subprocess.CalledProcessError(return_code, command)

def run_auto_configure(auto_dir):
    command = [
                "sh",
                "configure",
                "--enable-plaut=no",
                "--enable-plaut04=no",
            ]
    
    return run_sh_with_output(command, auto_dir)

    

def run_make_auto(auto_dir):
    command = [
            "make"
        ]

    return run_sh_with_output(command, auto_dir)

def run_make_clean(auto_dir):
    command = [
            "make",
            "clean"
        ]

    return run_sh_with_output(command, auto_dir)

def main():
    home_dir = os.getenv("HOME")
    default_install_dir = os.path.join(home_dir, ".local/bin/")
    all_done = False

    state_fun_dict = {
            "configure_auto" : {
                "fun": run_auto_configure,
                "output": "Running AUTO-07p configure script...",
                "next_state": "build_auto"
            },
            "build_auto" :  {
                "fun": run_make_auto,
                "output": "Running make...",
                "next_state": "make_clean"
            },
            "make_clean" : {
                "fun": run_make_clean,
                "output": "Running make clean...",
                "next_state": "abort"
            },
    }
    
    state = "check_prerequisites"
    while not all_done:
        if state == "check_prerequisites":
            state = "abort"

        elif state == "download_archive":
            # Get auto-archive from github
            try:
                print("Downloading AUTO-07p archive from github...")
                # auto_archive_path = get_auto_archive(home_dir)
                auto_archive_path = "/home/andre/Downloads/auto.zip"
                print("Done.\n")
                state = "extract_archive_prep"
            except:
                print(
                    (
                        "Something went wrong while trying "
                        "to download AUTO-07p from github. \n"
                        "Is github down or do you have no internet connection?"
                    )
                )
                state = "abort"

        elif state == "extract_archive_prep":
            # extract archive to installation directory
            create_dir = False
            target_done = False
            while not target_done:
                # Select installation directory
                use_default = input(
                    f"Use default install directory ({default_install_dir}) ([y]/n)? "
                )
                if use_default.lower() in ["y", ""]:
                    target_dir = default_install_dir
                    target_done = True

                elif use_default.lower() == "n":
                    user_dir = input(
                        f"Where should we install to? (absolute path)\n"
                    )
                    user_dir = os.path.abspath(user_dir)
                    target_dir = user_dir
                    target_done = True
                else:
                    print("Invalid input.")

            auto_dir = os.path.join(target_dir, "auto_07p")
            if not os.path.exists(target_dir):
                # selected directory does not exist, create?
                target_dir_does_not_exist_done = False
                while not target_dir_does_not_exist_done:
                    create = input(
                        (
                            f"Target directory {target_dir} does not exist. "
                            "Try to create? ([y]/n) "
                        )
                    )
                    if create.lower() in ["y", ""]:
                        create_dir = True
                        target_dir_does_not_exist_done = True
                        state = "extract_archive"
                    elif create.lower() == "n":
                        create_dir = False
                        target_dir_does_not_exist_done = True
                        state = "abort"
                    else:
                        print("Invalid input.")

            elif os.path.exists(auto_dir):
                overwrite_done = False
                while not overwrite_done:
                    overwrite = input(
                        "auto_07p already present in target directory "
                        "Overwrite? ([y]/n]) "
                    )
                    if overwrite.lower() in ["y", ""]:
                        overwrite_done = True
                        shutil.rmtree(auto_dir)
                        state = "extract_archive"

                    elif overwrite.lower() == "n":
                        overwrite_done = True
                        state = "abort"
                    else:
                        print("Invalid input.\n")
            else:
                state = "extract_archive"

            if create_dir:
                try:
                    os.makedirs(target_dir)
                    state = "extracht_archive"
                except OSError:
                    print("Could not create directory {target_dir}.\n")
                    state = "abort"

        elif state == "extract_archive":
            state = "abort"
            print(f"Extracting archive to {target_dir}")
            try:
                unpack_auto_archive(auto_archive_path, target_dir)
                # os.remove(auto_archive_path)
                print("Done.")
                state = "configure_auto"
            except Exception as e:
                print("Something went wrong while extracting:")
                print(e)
                state = "abort"

        elif state in state_fun_dict.keys():
            print(state_fun_dict[state]["output"])
            try:
                for outline in state_fun_dict[state]["fun"](auto_dir):
                    print(outline)
                status = 0
                print("Done.\n")

            except subprocess.CalledProcessError as e:
                print("An Error has occured:")
                print(e)
                status = -1
            
            if status == 0:
                state = state_fun_dict[state]["next_state"]
            else:
                state = "abort"

        elif state == "abort":
            print("Aborting...")
            all_done = True


if __name__ == "__main__":
    main()
