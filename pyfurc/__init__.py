__author__ = "ak"
__version__ = "0.1.6"
print("Entering __init__")
import os, configparser, warnings

print("Import pyfurc.tools")
from pyfurc.tools import (
    AutoInstaller,
    AutoHelper
)

print("Import pyfurc.core")
from pyfurc.core import (
    PhysicalQuantity,
    Energy,
    BifurcationProblem,
    BifurcationProblemSolver,
    BifurcationProblemSolution,
)

print("Import pyfurc.util")
from pyfurc.util import (
    AutoCodePrinter,
    DataDir,
    ParamDict,
    AutoParameters,
    HiddenAutoParameters,
    AutoOutputReader,
)

print("Initializing Installer/Helper")
ai = AutoInstaller()
ah = AutoHelper()

print("Checking config")
conf_exists = ai.check_if_config_exists()
print("Getting config path")
conf_path = ah.get_conf_path()

if not conf_exists:
    warnings.warn(
        "AUTO-07p installation is unknown since "
        f"no configuration file is present at {conf_path}. \n"
        "pyfurc will not be able to run AUTO-07p. "
        "To specify the path to AUTO-07p run\n"
        "python -m pyfurc --set-auto-dir"
        )
else:
    ...
    #check autodir
    