import configparser as cp
from appdirs import AppDirs
import os
import readline

def get_conf_path():
    dirs = AppDirs("pyfurc", "klunkean")
    user_dir = dirs.user_data_dir
    conf_name = "pyfurc.conf"
    conf_file_path = os.path.join(user_dir, conf_name)
    return conf_file_path

def get_default_install_dir():
    home_dir = os.getenv("HOME")
    default_dir = os.path.join(home_dir, ".local/bin")
    return default_dir

def get_default_auto_dir():
    default_install_dir = get_default_install_dir()
    default_auto_dir = os.path.join(default_install_dir, "auto_07p")
    return default_auto_dir

def check_if_config_exists():
    conf_path = get_conf_path()
    return os.path.exists(conf_path)

def check_if_auto_dir_is_valid(auto_dir):
    env_path = os.path.join(auto_dir,"cmds/auto.env.sh")
    if not os.path.exists(env_path):
        out_str = (
            f"Given auto directory {auto_dir} is invalid. "
            "Check your config."
        )
        return -1, out_str
    else:
        return 0, ""
    

def write_conf(auto_dir = None):
    all_done = False
    state = "get_auto_dir"
    try:
        while not all_done:
            if state == "get_auto_dir":
                # auto tab completion on paths
                readline.set_completer_delims(' \t\n=')
                readline.parse_and_bind("tab: complete")

                if auto_dir is None:
                    default_dir = get_default_auto_dir()
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
                        code, output = check_if_auto_dir_is_valid(auto_dir)
                        if code == 0:
                            auto_dir_input_done = True
                        else:
                            print(output)
                state = "write_conf"

            elif state == "write_conf":
                # get config file path
                conf_file_path = get_conf_path()
                config = cp.ConfigParser()
                config.read(conf_file_path)

                config["pyfurc"] = {"AUTO_DIR":auto_dir}

                basedir = os.path.dirname(conf_file_path)

                if not os.path.exists(basedir):
                    os.makedirs(basedir)      

                with open(conf_file_path ,"w") as conf_file:
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
    
