import importlib.resources
import os


def setup_auto_exec_env():
    """Sets up AUTO-07p executable PATHs and returns an environment for use with subprocess"""
    env = os.environ.copy()

    # This seems hacky. Don't know how else to find pyfurc.ext when
    # it looks like this:
    # {base_path, e.g. site-packages}
    #    |-- pyfurc
    #       |-- __init__.py
    #       |-- ...
    #    |-- pyfurc.ext
    #       |-- auto-07p

    with importlib.resources.path(__package__, "__init__.py") as pkg_path:
        auto_lib_dir = pkg_path.parents[1].joinpath("pyfurc.ext", "auto-07p", "lib")

    env["LD_LIBRARY_PATH"] = str(auto_lib_dir)
    return env
