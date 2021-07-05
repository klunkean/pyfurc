import subprocess
import os
import glob
import shutil
import urllib.request
from zipfile import ZipFile
import readline
import configparser as cp
from appdirs import AppDirs


class AutoHelper:
    """Helper class for getting the configuration file path and setting up an ``env`` with AUTO-07p executables added to ``PATH``.

    This class is not intended to be used.
    """
    def get_conf_path(self):
        dirs = AppDirs("pyfurc", "klunkean")
        user_dir = dirs.user_data_dir
        conf_name = "pyfurc.conf"
        conf_file_path = os.path.join(user_dir, conf_name)
        return conf_file_path

    def setup_auto_exec_env(self):
        """Sets up AUTO-07p executable PATHs and returns an environment for use with subprocess"""
        conf_file_path = self.get_conf_path()
        config = cp.ConfigParser()
        config.read_file(open(conf_file_path))
        auto_dir = config["pyfurc"]["AUTO_DIR"]

        env = os.environ.copy()
        env["AUTO_DIR"] = auto_dir
        with open(
            os.path.join(auto_dir, "cmds", "auto.env.sh"), "r"
        ) as envf:
            for line in envf.readlines():
                if line.startswith("PATH"):
                    extend = line.split("=")[-1].rstrip()
                    extend = extend.replace("$AUTO_DIR", auto_dir)
                    newpath = env["PATH"] + f":{extend}"
                    env["PATH"] = newpath
        return env

    def check_auto_installation(self):
        ...


class AutoInstaller:
    """Class for managing download and installation of AUTO-07p.

    This class is not intended to be used. The install script is called when running ``python -m pyfurc --install-auto``
    """
    def __init__(self):
        self.ah = AutoHelper()

    def get_default_install_dir(self):
        home_dir = os.getenv("HOME")
        default_dir = os.path.join(home_dir, ".local/bin")
        return default_dir

    def get_default_auto_dir(self):
        default_install_dir = self.get_default_install_dir()
        default_auto_dir = os.path.join(default_install_dir, "auto-07p")
        return default_auto_dir

    def check_if_config_exists(self):
        conf_path = self.ah.get_conf_path()
        return os.path.exists(conf_path)

    def check_if_auto_dir_is_valid(self, auto_dir):
        env_path = os.path.join(auto_dir, "cmds/auto.env.sh")
        if not os.path.exists(env_path):
            out_str = (
                f"Given auto directory {auto_dir} is invalid. "
                "Check your config."
            )
            return -1, out_str
        else:
            return 0, ""

    def get_auto_archive(self, target_dir):
        zipname = "auto.zip"
        target_path = os.path.abspath(os.path.join(target_dir, zipname))
        url = "https://github.com/auto-07p/auto-07p/archive/refs/heads/master.zip"
        urllib.request.urlretrieve(url, target_path)
        return target_path

    def unpack_auto_archive(self, archive_path, target_dir):
        zip_path, _ = os.path.split(archive_path)

        with ZipFile(archive_path, "r") as zip_ref:
            zip_ref.extractall(zip_path)
            auto_dir_name = zip_ref.infolist()[0].filename

        path_to_auto_dir = os.path.join(zip_path, auto_dir_name)

        auto_dir_name = os.path.split(self.get_default_auto_dir())[-1]
        os.rename(
            path_to_auto_dir, os.path.join(target_dir, auto_dir_name)
        )
        return path_to_auto_dir

    def run_sh_with_output(self, command, directory):
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

    def run_auto_configure(self, auto_dir):
        command = [
            "sh",
            "configure",
            "--enable-plaut=no",
            "--enable-plaut04=no",
        ]

        return self.run_sh_with_output(command, auto_dir)

    def run_make_auto(self, auto_dir):
        command = ["make"]

        return self.run_sh_with_output(command, auto_dir)

    def run_make_clean(self,auto_dir):
        command = ["make", "clean"]

        return self.run_sh_with_output(command, auto_dir)

    def set_up_env_for_sh(self, auto_dir):
        env_file = os.path.join(auto_dir, "cmds/auto.env.sh")
        with open(env_file, "r") as ef:
            env_content = ef.read()
        env_content = env_content.replace(
            "AUTO_DIR=$HOME/auto/07p", f"AUTO_DIR={auto_dir}"
        )
        with open(env_file, "w") as ef:
            ef.write(env_content)

        bashrc_file = os.path.join(os.getenv("HOME"), ".bashrc")

        try:
            text = f"\n#AUTO-07p commands\nsource {env_file}"
            with open(bashrc_file, "a") as bf:
                bf.write(text)
            return 0
        except FileNotFoundError:
            return -1

    def install_auto(self):
        try:
            readline.set_completer_delims(" \t\n=")
            readline.parse_and_bind("tab: complete")
            home_dir = os.getenv("HOME")

            all_done = False

            state_fun_dict = {
                "configure_auto": {
                    "fun": self.run_auto_configure,
                    "output": "Running AUTO-07p configure script...",
                    "next_state": "build_auto",
                },
                "build_auto": {
                    "fun": self.run_make_auto,
                    "output": "Running make...",
                    "next_state": "make_clean",
                },
                "make_clean": {
                    "fun": self.run_make_clean,
                    "output": "Running make clean...",
                    "next_state": "chmod",
                },
            }

            state = "check_prerequisites"
            while not all_done:
                if state == "check_prerequisites":
                    print("Checking for prerequisites...")
                    preqs = ["gfortran", "gcc", "make"]
                    not_there = []
                    for p in preqs:
                        if not shutil.which(p):
                            not_there.append(p)
                    if len(not_there) > 0:
                        print(f"{', '.join(not_there)} not installed.")
                        print(
                            "Please install these programs before rerunning "
                            "this script.\n"
                            "On Ubuntu run the following command:\n"
                            f"sudo apt update && sudo apt install {' '.join(not_there)}"
                        )
                        state = "abort"
                    else:
                        print("Done.")
                        state = "download_archive"

                elif state == "download_archive":
                    # Get auto-archive from github
                    try:
                        print(
                            "Downloading AUTO-07p archive from github..."
                        )
                        auto_archive_path = self.get_auto_archive(home_dir)
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

                    default_install_dir = self.get_default_install_dir()
                    default_auto_dir = self.get_default_auto_dir()
                    while not target_done:
                        # Select installation directory
                        use_default = input(
                            f"Use default install directory ({default_install_dir}) ([y]/n)? "
                        )
                        if use_default.lower() in ["y", ""]:
                            target_dir = default_install_dir
                            target_done = True
                            auto_dir = default_auto_dir

                        elif use_default.lower() == "n":
                            user_dir = input(
                                f"Where should we install to? (absolute path)\n"
                            )
                            user_dir = os.path.abspath(user_dir)
                            target_dir = user_dir
                            auto_dir = os.path.join(
                                target_dir,
                                os.path.split(default_auto_dir)[-1],
                            )
                            target_done = True
                        else:
                            print("Invalid input.")

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
                                "auto-07p already present in target directory "
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
                        except OSError as e:
                            print(
                                "Could not create directory {target_dir}."
                            )
                            print(e)
                            state = "abort"

                elif state == "extract_archive":
                    state = "abort"
                    print(f"Extracting archive to {target_dir}")
                    try:
                        self.unpack_auto_archive(
                            auto_archive_path, target_dir
                        )
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
                        for outline in state_fun_dict[state]["fun"](
                            auto_dir
                        ):
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

                elif state == "chmod":
                    cmd_path = os.path.join(auto_dir, "cmds")
                    try:
                        print("chmod executables...")
                        for f in glob.glob(
                            os.path.join(cmd_path, "@*")
                        ):
                            os.chmod(f, 0o774)
                        print("Done")
                        state = "configure_env"
                    except Exception as e:
                        print("Something went wrong:")
                        print(e)
                        state = "abort"

                elif state == "configure_env":
                    try:
                        print("Writing config file...")
                        self.write_conf(auto_dir=auto_dir)
                        state = "finished"
                    except Exception as e:
                        print("Something went wrong:")
                        print(e)
                        state = "abort"

                elif state == "abort":
                    print("Aborting...")
                    all_done = True

                elif state == "finished":
                    print(
                        f"AUTO-07p successfully installed to {auto_dir}."
                    )
                    print(
                        "If you want to run AUTO-07p commands in your shell "
                        "outside of pyfurc, you need to source the appropriate "
                        f"environment file in {auto_dir}/cmds."
                    )
                    all_done = True
        except KeyboardInterrupt:

            print("\nInstallation manually aborted...")
            try:
                # remove archive if downloaded
                os.remove(auto_archive_path)
                print(f"Deleted downloaded archive {auto_archive_path}")
            except NameError:
                pass

    def write_conf(self, auto_dir=None):
        all_done = False
        state = "get_auto_dir"
        try:
            while not all_done:
                if state == "get_auto_dir":
                    # auto tab completion on paths
                    readline.set_completer_delims(" \t\n=")
                    readline.parse_and_bind("tab: complete")

                    if auto_dir is None:
                        default_dir = self.get_default_auto_dir()
                        auto_dir_input_done = False
                        while not auto_dir_input_done:
                            auto_dir = input(
                                "Please enter the path to the "
                                "AUTO-07p base directory.\n"
                                "Leave empty if you chose the default directory "
                                "during installation "
                                f"({default_dir}).\n"
                            )
                            if auto_dir == "":
                                auto_dir = default_dir
                            code, output = self.check_if_auto_dir_is_valid(
                                auto_dir
                            )
                            if code == 0:
                                auto_dir_input_done = True
                            else:
                                print(output)
                    state = "write_conf"

                elif state == "write_conf":
                    # get config file path
                    conf_file_path = self.ah.get_conf_path()
                    config = cp.ConfigParser()
                    config.read(conf_file_path)

                    config["pyfurc"] = {"AUTO_DIR": auto_dir}

                    basedir = os.path.dirname(conf_file_path)

                    if not os.path.exists(basedir):
                        os.makedirs(basedir)

                    with open(conf_file_path, "w") as conf_file:
                        config.write(conf_file)

                    state = "done"

                elif state == "abort":
                    print("Aborted.")
                    all_done = True

                elif state == "done":
                    print(f"Written config file to {conf_file_path}")
                    all_done = True
        except KeyboardInterrupt:
            print("Aborted.")
