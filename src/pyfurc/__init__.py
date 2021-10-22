__author__ = "ak"
__version__ = "0.1.7"
import configparser
import os
import warnings

from pyfurc.core import (
    BifurcationProblem,
    BifurcationProblemSolution,
    BifurcationProblemSolver,
    Energy,
    PhysicalQuantity,
)
from pyfurc.tools import AutoHelper, AutoInstaller
from pyfurc.util import (
    AutoCodePrinter,
    AutoOutputReader,
    AutoParameters,
    DataDir,
    HiddenAutoParameters,
    ParamDict,
)

ai = AutoInstaller()
ah = AutoHelper()

conf_exists = ai.check_if_config_exists()
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
    # check autodir
