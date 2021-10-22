import os
from datetime import datetime as dt

from pandas import read_csv
from sympy.printing.fortran import FCodePrinter


class AutoCodePrinter(FCodePrinter):
    """Subclass of ``sympy.FCodePrinter`` with necessary parameters set
    for printing AUTO-07p FORTRAN code.

    See Also
    --------
    :doc:`Sympy Code Generation <sympy:modules/codegen>`
    """

    def __init__(self):
        settings = {"source_format": "free", "standard": 95}
        super().__init__(settings=settings)

    def _print_Symbol(self, expr):
        try:
            name = expr._name
        except AttributeError:
            name = expr.name
        return name

    def _print_Zero(self, expr):
        return "0.0d0"


class DataDir:
    def __init__(self, base_dir="./", name=""):
        self.date_time = dt.now().strftime(r"%Y%m%d_%H%M%S")
        self.directory = os.path.join(base_dir, f"{name}_{self.date_time}")
        self.codedir = self.directory + "code/"
        self.dir_created = False

    def create_dir(self):
        os.mkdir(self.directory)
        self.dir_created = True

    def dir(self):
        return self.directory

    def __str__(self):
        return self.directory

    def create_subdir(self, name):
        os.mkdir(os.path.join(self.directory, name))
        if not self.dir_created:
            self.dir_created = True
            os.mkdir(self.directory)
        return self.directory + "/" + name + "/"


class ParamDict(dict):
    def __str__(self):
        out = ""
        for name, val in self.items():
            out += f"{name:s}\t: {str(val):s}\n"
        return out


class AutoParameters(ParamDict):
    """Dictionary holding the AUTO-07p calculation parameters.
    Upon instantiation default values will be set.

    The following table gives a list of parameter names and their default
    values. The short explanations are taken from the
    `AUTO-07p manual <https://depts.washington.edu/bdecon/workshop2012/auto-tutorial/documentation/auto07p%20manual.pdf>`_.
    Please refer to the AUTO-07p manual for more detailed explanations.

    ========= ======= ===========
    Parameter Default Explanation
    ========= ======= ===========
    NTST      50      The number of mesh intervals used for discretization.
    IAD       3       This constant controls the mesh adaption.
                      ``IAD=3`` is the strongly recommended value.
    EPSL      1e-07   Relative convergence criterion for equation
                      parameters in the Newton/Chord method.
                      Recommended value range: ``10E-7`` to ``10E-6``.
    EPSU      1e-07   Relative convergence criterion for solution
                      components in the Newton/Chord method.
                      Recommended value range: ``10E-7`` to ``10E-6``.
    EPSS      1e-05   Relative arclength convergence criterion for the
                      detection of special solutions. Recommended value
                      range: ``10E-5`` to ``10E-4``. Generally, ``EPSS``
                      should be approximately 100 to 1000 times the value
                      of ``EPSL``, ``EPSU``.
    ITMX      8       The maximum number of iterations allowed in the
                      accurate location of special solutions, such as
                      bifurcations, folds, and user output points,
                      by Müller’s method with bracketing. The recommended
                      value is ``ITMX=8``
    ITNW      5       The maximum number of combined Newton-Chord
                      iterations. When this maximum is reached, the step
                      will be retried with half the stepsize. The
                      recommended value is ``ITNW=5``, but ``ITNW=7`` may
                      be used for “difficult” problems
    DS        0.1     Pseudo-arclength stepsize to be used for the first
                      attempted step along any family.
                      ``DSMIN`` ≤ | ``DS`` | ≤ ``DSMAX`` must hold.
    DSMIN     0.001   Minimum allowable absolute value of the
                      pseudo-arclength stepsize.
    DSMAX     0.2     Maximum allowable absolute value of the
                      pseudo-arclength stepsize.
    IADS      1       This constant controls the frequency of adaption of
                      the pseudo-arclength stepsize.

                            - ``IADS=0``: fixed pseudo-arclength stepsize ``DS``.
                            - ``IADS>0``: Adapt the pseudo-arclength stepsize after every ``IADS`` steps.
    ICP       [1]     For each equation type and for each continuation
                      calculation there is a typical (“ge
                      The array ICP designates these free parameters.
                      The parameter that appears first in the ICP list
                      is called the “principal continuation parameter”.
    STOP      []      This constant adds stopping conditions
    NMX       200     The maximum number of steps to be taken along any
                      family.
    RL0       0.0     The lower bound on the principal continuation
                      parameter. Typically this will be the load.
    RL1       0.0     The upper bound on the principal continuation
                      parameter.
    MXBF      10      Maximum number of bifurcations to be treated.
    NPR       200     This constant can be used to regularly write
                      ``fort.8`` plotting and restart data. IF ``NPR>0``
                      then such output is written every ``NPR`` steps.
                      If ``NPR=0`` or if ``NPR``≥``NMX`` then no such
                      output is written.
    IID       2       This constant controls the amount of diagnostic
                      output printed in ``fort.9``. See the AUTO-07p manual
                      for details.
    IPLT      0       This constant allows redefinition of the principal
                      solution measure, i.e. the error norm. See the
                      AUTO-07p manual for details.
    UZR       {}      This constant allows the setting of parameter values
                      which labeled plotting and restart information is to
                      be written in the ``fort.8`` output-file. See the
                      AUTO-07p manual for details.
    UZSTOP    {}      This constant specifies parameter values in the same
                      way as ``UZR`` above, but the computation will always
                      terminate if any solution point that is specified is
                      encountered.
    ========= ======= ===========
    """

    def __init__(self):
        default_parameters = {
            "NTST": 50,
            "IAD": 3,
            "EPSL": 1e-7,
            "EPSU": 1e-7,
            "EPSS": 1e-5,
            "ITMX": 8,
            "ITNW": 5,
            "DS": 0.1,
            "DSMIN": 1e-3,
            "DSMAX": 0.2,
            "IADS": 1,
            "ICP": [1],
            "STOP": "[]",
            "NMX": 200,
            "RL0": 0.0,
            "RL1": 0.0,
            "MXBF": 10,
            "NPR": 200,
            "IID": 2,
            "IPLT": 0,
            "UZR": "{}",
            "UZSTOP": "{}",
        }
        self.update(default_parameters)


class HiddenAutoParameters(ParamDict):
    def __init__(self):
        default_parameters = {
            "NBC": 0,
            "NINT": 0,
            "JAC": 0,
            "ILP": 0,
            "ISP": 1,
            "IRS": 0,
            "IPS": 0,
        }

        self.update(default_parameters)


class AutoOutputReader:
    def __init__(self, dirc):
        self.dirc = dirc
        self.outfile7 = os.path.join(self.dirc, "fort.7")

    def read_raw_data(self):
        # TODO Rewrite without pandas (Big chunky bloaty module for reading csv)
        line_numbers = self.find_table_lines()
        data = []
        for lines in line_numbers:
            start, stop = lines
            df = read_csv(
                self.outfile7,
                header=1,
                skiprows=start - 1,
                nrows=stop - start,
                delim_whitespace=True,
            )
            data.append(df)
        return data

    def find_table_lines(self):
        searching_for_start = 1
        line_numbers = []
        with open(self.outfile7) as data_file:
            for line_number, line in enumerate(data_file.readlines()):
                if searching_for_start:
                    if not line.lstrip().startswith("0"):
                        start_line = line_number - 1  # table header starts with 0
                        searching_for_start = 0
                else:
                    if line.lstrip().startswith("0"):
                        end_line = line_number - 1
                        line_numbers.append([start_line, end_line])
                        searching_for_start = 1
            if not searching_for_start:  # last table since there is no zero at the end
                line_numbers.append([start_line, line_number])
        return line_numbers
