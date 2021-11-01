import importlib.resources
import os


def setup_auto_exec_env():
    """Sets up AUTO-07p executable PATHs and returns an environment for use with subprocess"""
    env = os.environ.copy()

    if "AUTO_DIR" in env:
        auto_dir = env["AUTO_DIR"]
    else:
        # This seems hacky. Don't know how else to find pyfurc-ext when
        # it looks like this:
        # |{base_path, e.g. site-packages}
        #    |-- pyfurc
        #       |-- __init__.py
        #       |-- ...
        #    |-- pyfurc-ext
        #       |-- auto-07p

        with importlib.resources.path(
            __package__, "__init__.py"
        ) as pkg_path:
            auto_dir = pkg_path.parents[1].joinpath(
                "pyfurc.ext", "auto-07p"
            )

        env["AUTO_DIR"] = auto_dir

    with open(os.path.join(auto_dir, "cmds", "auto.env.sh")) as envf:
        for line in envf.readlines():
            if line.startswith("PATH"):
                extend = line.split("=")[-1].rstrip()
                extend = extend.replace("$AUTO_DIR", str(auto_dir))
                newpath = env["PATH"] + f":{extend}"
                env["PATH"] = newpath
    return env
