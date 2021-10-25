import importlib.resources
import os


def setup_auto_exec_env():
    """Sets up AUTO-07p executable PATHs and returns an environment for use with subprocess"""
    env = os.environ.copy()

    if "AUTO_DIR" in env:
        auto_dir = env["AUTO_DIR"]
    else:
        with importlib.resources.path(__package__, "auto-07p") as auto_dir_path:
            auto_dir = str(auto_dir_path)
        env["AUTO_DIR"] = auto_dir

    with open(os.path.join(auto_dir, "cmds", "auto.env.sh")) as envf:
        for line in envf.readlines():
            if line.startswith("PATH"):
                extend = line.split("=")[-1].rstrip()
                extend = extend.replace("$AUTO_DIR", auto_dir)
                newpath = env["PATH"] + f":{extend}"
                env["PATH"] = newpath
    return env
