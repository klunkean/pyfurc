from sympy import Symbol, Rational, nfloat
from sympy import Expr as spexpr
from sympy import sin as sp_sin
from sympy import pi as sp_pi
import os
from subprocess import Popen, PIPE
from warnings import warn
from appdirs import AppDirs

from pyfurc.util import (
    AutoCodePrinter,
    DataDir,
    ParamDict,
    AutoOutputReader,
)
from pyfurc.tools import AutoHelper


class PhysicalQuantity(Symbol):
    """Fundamental class for degrees of freedom and loads.

    Parameters
    ----------
    name : str
        The name that will be displayed in outputs. When working
        in a jupyter notebook, LaTeX symbols can be displayed, e.g.
        ``\\varphi``.
    quantity_type : str, optional
        One of ``load``, ``dof``, or ``parameter``, by default ``parameter``
    value : float, optional
        Initial value if `quantity_type` is `load` or `dof`.
        Value if `quantity_type` is `parameter`.
        Default is 0.0.
    
    Example
    -------
    Define a degree of freedom with an initial value of 1.0 and a display name "\\\\varphi":
        
        .. code-block:: python

            phi = PhysicalQuantity("\\\\varphi", quantity_type="dof", value=1.0)
    """

    def __new__(cls, name, quantity_type="parameter", value=0.0):
        obj = super().__new__(cls, name)
        possible_quantity_types = ["load", "dof", "parameter"]
        if quantity_type.lower() not in possible_quantity_types:
            raise ValueError(
                "quantity_type has to be one of: "
                + ", ".join(possible_quantity_types)
            )
        obj._name = None
        obj.quantity_type = quantity_type.lower()
        obj.value = value
        return obj

class Energy(spexpr):
    """Container class for energy expressions.

    Parameters
    ----------
    expr : valid sympy Expression e.g. ``sympy.Mul`` or ``sympy.Add`` containing exactly one `pyfurc.core.PhysicalQuantity` with ``quantity_type="load"``
        
    """
    def __init__(self, expr):
        self.expr = expr
        self.dofs = {}
        self.params = {}
        self.ndofs = 0
        self.nparams = 0
        load_defined = 0
        for atom in expr.atoms():
            if type(atom) is PhysicalQuantity:
                if atom.quantity_type == "dof":
                    self.ndofs += 1
                    name = "U({:d})".format(self.ndofs)
                    atom._name = name
                    self.dofs.update(
                        {atom: {"name": name, "value": atom.value}}
                    )

                elif atom.quantity_type == "parameter":
                    self.nparams += 1
                    name = "PAR({:d})".format(self.nparams + 1)
                    atom._name = name
                    self.params.update(
                        {atom: {"name": name, "value": atom.value}}
                    )
                elif atom.quantity_type == "load":
                    name = "PAR(1)"
                    atom._name = name
                    self.load = {
                        atom: {"name": name, "value": atom.value}
                    }
                    load_defined += 1
        if load_defined != 1:
            raise NotImplementedError(
                "You have to define exactly one load. Other cases are not implemented."
            )

    # TODO fix repr and str for pretty printing and print dofs, load and parameters
    def __repr__(self):
        return repr(self.expr)

    # TODO fix repr and str for pretty printing and print dofs, load and parameters
    def __str__(self):
        return str(self.expr)

    def info(self):
        infostr = "Potential energy with {:d} DOF(s):\n".format(
            self.ndofs
        )
        infostr += str(self.expr) + "\n\n"
        infostr += "The DOFs are:\n"
        for dof, dofdict in self.dofs.items():
            infostr += (
                "\t"
                + dof.name
                + " - "
                + "Fortran Name: {:s}".format(dofdict["name"])
                + " - "
                + "Init. Value: {:f}".format(dofdict["value"])
                + "\n"
            )
        infostr += "The parameters are:\n"
        for prm, prmdict in self.params.items():
            infostr += (
                "\t"
                + prm.name
                + " - "
                + "Fortran Name: {:s}".format(prmdict["name"])
                + " - "
                + "Value: {:f}".format(prmdict["value"])
                + "\n"
            )
        infostr += "The load is:\n"
        for load, loaddict in self.load.items():
            infostr += (
                "\t"
                + load.name
                + " - "
                + "Fortran Name: {:s}".format(loaddict["name"])
                + " - "
                + "Init. Value: {:f}".format(loaddict["value"])
                + "\n"
            )
        print(infostr)

    def equilibrium(self):
        eq_exprs = []
        for dof, _ in self.dofs.items():
            try:
                eq = self.expr.diff(dof)
                # eq = nfloat(eq)
            except AttributeError:
                "Expression seems not to be a valid sympy expression."
            eq_exprs.append(eq)
        return eq_exprs

    def set_quantity_value(self, key, value):
        found = False
        for dicti in [self.params, self.dofs, self.load]:
            if key in dicti:
                dicti[key]["value"] = value
                found = True
        if not found:
            raise KeyError("Variable {:s} not found".format(str(key)))


class BifurcationProblem:
    """Class for holding information on a bifurcation problem.

    Objects of this class are defined by their :class:`pyfurc.core.Energy` expression and their ``name``. 
    Upon instantiation a :class:`pyfurc.core.ParamDict` is created that holds default values for the calculations in AUTO-07p.

    Parameters
    ----------
    energy : :class:`pyfurc.core.Energy`
        The energy of the system containing at least one dof and one load.
    name : str, optional
        Name of the bifurcation problem. The calculation output folder will contain this name.


    Variables
    ---------
    :ivar pyfurc.core.Energy energy: The energy expression passed on instantiation.
    :ivar dict dofs: Reference to ``energy.dofs``, dictionary holding ``dof`` names and values. 
    :ivar pyfurc.util.Paramdict problem_parameters: AUTO-7p calculation parameters.
    :ivar str problem_name: Name of the bifurcation problem passed on instantiation. The calculation output folder will contain this name.
    """
    def __init__(self, energy, name="pyfurc_problem"):
        self.energy = energy
        self.dofs = energy.dofs
        self._solved = False
        self.problem_name = name
        self.problem_parameters = ParamDict()
        self.problem_parameters.update(
            {
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
        )

        self._other_parameters = ParamDict()
        self._other_parameters.update(
            {
                "NDIM": self.energy.ndofs,
                "NPAR": self.energy.nparams + 1,
                "NBC": 0,
                "NINT": 0,
                "JAC": 0,
                "ICP": [1],
                "ILP": 0,
                "ISP": 1,
                "IRS": 0,
                "IPS": 0,
            }
        )

        self._f_printer = AutoCodePrinter()

    def set_parameter(self, param, value):
        other = False
        if param in self._other_parameters.keys():
            warn(
                "Changing this parameter is not recommended. Results may be unpredictable."
            )
            other = True
        try:
            dict_to_change = (
                self.problem_parameters
                if not other
                else self._other_parameters
            )
            default_type = type(dict_to_change[param])
            if not (type(value) == default_type):
                if default_type == float and type(value) == int:
                    value = float(value)
                else:
                    raise TypeError(
                        "Parameter "
                        + param
                        + " must be of type "
                        + default_type
                    )
            dict_to_change[param] = value

        except KeyError:
            raise KeyError("Unknown key " + param)

    def set_quantity_value(self, param, value):
        """Set values for a :class:`pyfurc.core.PhysicalQuantity`. Shortcut for ``self.energy.set_quantity_value``

        Parameters
        ----------
        param : :class:`pyfurc.core.PhysicalQuantity`
            The quantity with the value to be changed. 
        value : float
            The value.
        """
        self.energy.set_quantity_value(param, value)

    def _fortran_equilibriums(self):
        equis = self.energy.equilibrium()
        fort_eqs = []
        for i, eq in enumerate(equis):
            fort_eq = (
                "F({:d})=".format(i + 1)
                + self._f_printer.doprint(eq).lstrip()
            )
            fort_eqs.append(fort_eq)
        return fort_eqs


class BifurcationProblemSolver:
    def __init__(self, bf_problem):
        self.problem = bf_problem
        self._f_printer = AutoCodePrinter()
        self._f_ind = "  "
        self.ah = AutoHelper()

    def _f_func(self):
        eq_exprs = self.problem._fortran_equilibriums()

        code = "SUBROUTINE FUNC(NDIM,U,ICP,PAR,IJAC,F,DFDU,DFDP)\n\n"
        code += self._f_ind + "IMPLICIT NONE\n"
        code += (
            self._f_ind + "INTEGER, INTENT(IN) :: NDIM, IJAC, ICP(*)\n"
        )
        code += (
            self._f_ind
            + "DOUBLE PRECISION, INTENT(IN) :: U(NDIM), PAR(*)\n"
        )
        code += (
            self._f_ind + "DOUBLE PRECISION, INTENT(OUT) :: F(NDIM)\n"
        )
        code += (
            self._f_ind
            + "DOUBLE PRECISION, INTENT(INOUT) :: DFDU(NDIM,NDIM),DFDP(NDIM,*)\n\n"
        )
        # body
        for expr in eq_exprs:
            code += self._f_ind + expr + "\n"
        # end body
        code += "\nEND SUBROUTINE FUNC"
        return code

    def _f_stpnt(self):
        code = "SUBROUTINE STPNT(NDIM,U,PAR,T)\n\n"
        code += self._f_ind + "IMPLICIT NONE\n"
        code += self._f_ind + "INTEGER, INTENT(IN) :: NDIM\n"
        code += (
            self._f_ind
            + "DOUBLE PRECISION, INTENT(INOUT) :: U(NDIM),PAR(*)\n"
        )
        code += self._f_ind + "DOUBLE PRECISION, INTENT(IN) :: T\n\n"
        # body
        for _, load_info in self.problem.energy.load.items():
            code += (
                self._f_ind
                + load_info["name"]
                + " = "
                + self._f_printer.doprint(load_info["value"]).lstrip()
                + "\n"
            )

        code += "\n"

        for _, para_dict in self.problem.energy.params.items():
            code += (
                self._f_ind
                + para_dict["name"]
                + " = "
                + self._f_printer.doprint(para_dict["value"]).lstrip()
                + "\n"
            )

        code += "\n"

        for _, dof_dict in self.problem.energy.dofs.items():
            code += (
                self._f_ind
                + dof_dict["name"]
                + " = "
                + self._f_printer.doprint(dof_dict["value"]).lstrip()
                + "\n"
            )

        # end body
        code += "\nEND SUBROUTINE STPNT"
        return code

    def _f_bcnd(self):
        code = "SUBROUTINE BCND(NDIM,PAR,ICP,NBC,U0,U1,FB,IJAC,DBC)\n\n"
        code += self._f_ind + "IMPLICIT NONE\n"
        code += (
            self._f_ind
            + "INTEGER, INTENT(IN) :: NDIM, ICP(*), NBC, IJAC\n"
        )
        code += (
            self._f_ind
            + "DOUBLE PRECISION, INTENT(IN) :: PAR(*), U0(NDIM), U1(NDIM)\n"
        )
        code += (
            self._f_ind + "DOUBLE PRECISION, INTENT(OUT) :: FB(NBC)\n"
        )
        code += (
            self._f_ind
            + "DOUBLE PRECISION, INTENT(INOUT) :: DBC(NBC,*)\n\n"
        )
        code += "END SUBROUTINE BCND"
        return code

    def _f_icnd(self):
        code = "SUBROUTINE ICND(NDIM,PAR,ICP,NINT,U,UOLD,UDOT,UPOLD,FI,IJAC,DINT)\n\n"
        code += self._f_ind + "IMPLICIT NONE\n"
        code += (
            self._f_ind
            + "INTEGER, INTENT(IN) :: NDIM, ICP(*), NINT, IJAC\n"
        )
        code += self._f_ind + "DOUBLE PRECISION, INTENT(IN) :: PAR(*)\n"
        code += (
            self._f_ind
            + "DOUBLE PRECISION, INTENT(IN) :: U(NDIM), UOLD(NDIM), UDOT(NDIM), UPOLD(NDIM)\n"
        )
        code += (
            self._f_ind + "DOUBLE PRECISION, INTENT(OUT) :: FI(NINT)\n"
        )
        code += (
            self._f_ind
            + "DOUBLE PRECISION, INTENT(INOUT) :: DINT(NINT,*)\n\n"
        )
        code += "END SUBROUTINE ICND"
        return code

    def _f_fopt(self):
        code = "SUBROUTINE FOPT(NDIM,U,ICP,PAR,IJAC,FS,DFDU,DFDP)\n\n"
        code += self._f_ind + "IMPLICIT NONE\n"
        code += (
            self._f_ind + "INTEGER, INTENT(IN) :: NDIM, ICP(*), IJAC\n"
        )
        code += (
            self._f_ind
            + "DOUBLE PRECISION, INTENT(IN) :: U(NDIM), PAR(*)\n"
        )
        code += self._f_ind + "DOUBLE PRECISION, INTENT(OUT) :: FS\n"
        code += (
            self._f_ind
            + "DOUBLE PRECISION, INTENT(INOUT) :: DFDU(NDIM),DFDP(*)\n\n"
        )
        code += "END SUBROUTINE FOPT"
        return code

    def _f_pvls(self):
        code = "SUBROUTINE PVLS(NDIM,U,PAR)\n\n"
        code += self._f_ind + "IMPLICIT NONE\n"
        code += self._f_ind + "INTEGER, INTENT(IN) :: NDIM\n"
        code += (
            self._f_ind + "DOUBLE PRECISION, INTENT(IN) :: U(NDIM)\n"
        )
        code += (
            self._f_ind
            + "DOUBLE PRECISION, INTENT(INOUT) :: PAR(*)\n\n"
        )
        code += "END SUBROUTINE PVLS"
        return code

    def write_func_file(self, basedir="./", silent=False):
        fname = os.path.join(
            basedir, self.problem.problem_name + ".f90"
        )
        code = self._f_func() + "\n\n"
        code += self._f_stpnt() + "\n\n"
        code += self._f_bcnd() + "\n\n"
        code += self._f_icnd() + "\n\n"
        code += self._f_fopt() + "\n\n"
        code += self._f_pvls()
        with open(fname, "w") as outfile:
            outfile.write(code)
        if not silent:
            print("File {:s} written.".format(fname))

    def write_const_file(self, basedir="./", silent=False):
        fname = os.path.join(basedir, "c." + self.problem.problem_name)
        params = {}
        params.update(self.problem.problem_parameters)
        params.update(self.problem._other_parameters)
        with open(fname, "w") as outfile:
            for name, val in params.items():
                outstr = name + "\t=\t" + str(val) + "\n"
                outfile.write(outstr)

        if not silent:
            print("File {:s} written.".format(fname))

    def solve(self):
        ddir = DataDir(name=self.problem.problem_name)
        ddir.create()
        dirc = str(ddir)
        self.solution_dir = dirc
        self.write_func_file(basedir=dirc, silent=True)
        self.write_const_file(basedir=dirc, silent=True)
        self.run_auto(dirc)
        self.problem._solved = True
        self.problem.solution = BifurcationProblemSolution()
        self.problem.solution.read_solution(dirc)

    def run_auto(self, dirc):
        print("Running AUTO on problem " + self.problem.problem_name)
        print("-" * 72)
        env = self.ah.setup_auto_exec_env()
        command = ["@r", self.problem.problem_name]
        process = Popen(
            command,
            stdout=PIPE,
            stderr=PIPE,
            cwd=dirc,
            bufsize=1,
            universal_newlines=True,
            env=env,
        )
        out, err = process.communicate()
        print(out)
        print(err)
        print("-" * 72)


class BifurcationProblemSolution:
    def __init__(self):
        pass

    def read_solution(self, dirc):
        self.reader = AutoOutputReader(dirc)
        self.raw_data = self.reader.read_raw_data()
