__author__ = "ak"
__version__ = "0.1.2"
import os

from pyfurc.core import (
    PhysicalQuantity,
    Energy,
    BifurcationProblem,
    BifurcationProblemSolver,
    BifurcationProblemSolution,
)

from pyfurc.util import (
    AutoCodePrinter,
    DataDir,
    ParamDict,
    AutoOutputReader,
)

os.environ["PATH"] += os.pathsep + "/home/andre/ASDF"