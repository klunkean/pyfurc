import os
import shutil
from subprocess import PIPE, Popen
from warnings import warn

from sympy import Expr as spexpr
from sympy import Rational, Symbol, nfloat
from sympy import pi as sp_pi
from sympy import sin as sp_sin

from pyfurc.tools import setup_auto_exec_env
from pyfurc.util import (
    AutoCodePrinter,
    AutoOutputReader,
    AutoParameters,
    DataDir,
    HiddenAutoParameters,
)


class PhysicalQuantity(Symbol):
    """Fundamental class for degrees of freedom, loads and parameters.

    Using the shortcut classes `pyfurc.Dof`, `pyfurc.Load` and `pyfurc.Parameter`
    is recommended.

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
    """

    def __new__(cls, name, quantity_type, value=0.0):
        obj = super().__new__(cls, name)
        possible_quantity_types = ["load", "dof", "parameter"]
        if quantity_type.lower() not in possible_quantity_types:
            raise ValueError(
                "quantity_type has to be one of: " + ", ".join(possible_quantity_types)
            )
        obj._name = None
        obj.quantity_type = quantity_type.lower()
        obj.value = value
        return obj


class Dof(PhysicalQuantity):
    """Class used for defining degrees of freedom. Shortcut for
    ``PhysicalQuantity(name, quantity_type="dof")``

    Parameters
    ----------
    name : str
        The name that will be displayed in outputs. When working
        in a jupyter notebook, LaTeX symbols can be displayed, e.g.
        ``\\varphi``.
    value : float, optional
        Initial value of the degree of freedom.
        Default is 0.0.

    Example
    -------
    Define a degree of freedom with an initial value of 1.0 and a display name "\\\\varphi":

        .. code-block:: python

            phi = Dof("\\\\varphi", value=1.0)
    """

    def __new__(cls, name, value=0.0):
        obj = super().__new__(cls, name, "dof", value=value)
        return obj


class Load(PhysicalQuantity):
    """Class used for defining degrees of freedom. Shortcut for
    ``PhysicalQuantity(name, quantity_type="load")``

    Parameters
    ----------
    name : str
        The name that will be displayed in outputs. When working
        in a jupyter notebook, LaTeX symbols can be displayed, e.g.
        ``\\varphi``.
    value : float, optional
        Initial value of the load.
        Default is 0.0.

    Example
    -------
    Define a Load with display name "P":

        .. code-block:: python

            phi = Load("P")
    """

    def __new__(cls, name, value=0.0):
        obj = super().__new__(cls, name, "load", value=value)
        return obj


class Parameter(PhysicalQuantity):
    def __new__(cls, name, value=0.0):
        obj = super().__new__(cls, name, "parameter", value=value)
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
            if isinstance(atom, (Dof, Load, Parameter)):
                if atom.quantity_type == "dof":
                    self.ndofs += 1
                    name = f"U({self.ndofs:d})"
                    atom._name = name
                    self.dofs.update({atom: {"name": name, "value": atom.value}})

                elif atom.quantity_type == "parameter":
                    self.nparams += 1
                    name = f"PAR({self.nparams + 1:d})"
                    atom._name = name
                    self.params.update({atom: {"name": name, "value": atom.value}})
                elif atom.quantity_type == "load":
                    name = "PAR(1)"
                    atom._name = name
                    self.load = {atom: {"name": name, "value": atom.value}}
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
        infostr = f"Potential energy with {self.ndofs:d} DOF(s):\n"
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
            raise KeyError(f"Variable {str(key):s} not found")


class BifurcationProblem:
    """Class for holding information on a bifurcation problem.

    Objects of this class are defined by their :class:`pyfurc.core.Energy`
    expression and their ``name``. Upon instantiation a
    :class:`pyfurc.util.AutoParameters` is created that holds default
    values for the calculations in AUTO-07p.

    Parameters
    ----------
    energy : :class:`pyfurc.core.Energy`
        The energy of the system containing at least one dof and one load.
    name : str, optional
        Name of the bifurcation problem. The calculation output folder
        will contain this name and a timestamp.

    Variables
    ---------
    :ivar pyfurc.core.Energy energy: The energy expression passed on instantiation.
    :ivar dict dofs: Reference to ``energy.dofs``, dictionary holding ``dof`` names and values.
    :ivar pyfurc.util.ProblemParameters problem_parameters: AUTO-7p calculation parameters.
    :ivar str problem_name: Name of the bifurcation problem passed on instantiation. The calculation output folder will contain this name.
    """

    def __init__(self, energy, name="pyfurc_problem", params=None):
        self.energy = energy
        self.dofs = energy.dofs
        self._solved = False
        self.problem_name = name
        self.problem_parameters = AutoParameters()
        if params is not None:
            self.problem_parameters.update(params)

        self._other_parameters = HiddenAutoParameters()
        self._other_parameters.update(
            {
                "NDIM": self.energy.ndofs,
                "NPAR": self.energy.nparams + 1,
            }
        )

        self._f_printer = AutoCodePrinter()

    def set_parameter(self, param, value):
        """Recommended way of changing values in ``problem_parameters``.

        Parameters
        ----------
        param : str
            Name of the parameter to change.
            See :class:`pyfurc.util.AutoParameters` for details.
        value :
            The value to set ``param`` to.

        Raises
        ------
        TypeError
            If ``value`` has the wrong type.
        KeyError
            If ``param`` is not a valid parameter name.


        .. Note::

            You can also directly change the keys in ``problem_parameters``,
            e.g. ``bf.problem_parameters[param] = value``.
            This will, however, bypass the type and key checks.

        Example
        -------
        >>> print(bf.problem_parameters["RL1"])
        0.0
        >>> bf.set_parameter("RL1", 1.0)
        >>> print(bf.problem_parameters["RL1"])
        1.0
        """
        other = False
        if param in self._other_parameters.keys():
            warn(
                "Changing this parameter is not recommended. Results may be unpredictable."
            )
            other = True
        try:
            dict_to_change = (
                self.problem_parameters if not other else self._other_parameters
            )
            default_type = type(dict_to_change[param])
            if not (type(value) == default_type):
                if default_type == float and type(value) == int:
                    value = float(value)
                else:
                    raise TypeError(
                        "Parameter " + param + " must be of type " + str(default_type)
                    )
            dict_to_change[param] = value

        except KeyError:
            raise KeyError("Unknown key " + param)

    def set_quantity_value(self, param, value):
        """Set values for a :class:`pyfurc.core.PhysicalQuantity` which
        is contained in the ``BifurcationProblem.energy`` expression.
        Shortcut for ``BifurcationProblem.energy.set_quantity_value``.

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
            fort_eq = f"F({i + 1:d})=" + self._f_printer.doprint(eq).lstrip()
            fort_eqs.append(fort_eq)
        return fort_eqs


class BifurcationProblemSolver:
    def __init__(self, bf_problem):
        self.problem = bf_problem
        self._f_printer = AutoCodePrinter()
        self._f_ind = "  "

    def _f_func(self):
        eq_exprs = self.problem._fortran_equilibriums()

        code = "SUBROUTINE FUNC(NDIM,U,ICP,PAR,IJAC,F,DFDU,DFDP)\n\n"
        code += self._f_ind + "IMPLICIT NONE\n"
        code += self._f_ind + "INTEGER, INTENT(IN) :: NDIM, IJAC, ICP(*)\n"
        code += self._f_ind + "DOUBLE PRECISION, INTENT(IN) :: U(NDIM), PAR(*)\n"
        code += self._f_ind + "DOUBLE PRECISION, INTENT(OUT) :: F(NDIM)\n"
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
        code += self._f_ind + "DOUBLE PRECISION, INTENT(INOUT) :: U(NDIM),PAR(*)\n"
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
        code += self._f_ind + "INTEGER, INTENT(IN) :: NDIM, ICP(*), NBC, IJAC\n"
        code += (
            self._f_ind + "DOUBLE PRECISION, INTENT(IN) :: PAR(*), U0(NDIM), U1(NDIM)\n"
        )
        code += self._f_ind + "DOUBLE PRECISION, INTENT(OUT) :: FB(NBC)\n"
        code += self._f_ind + "DOUBLE PRECISION, INTENT(INOUT) :: DBC(NBC,*)\n\n"
        code += "END SUBROUTINE BCND"
        return code

    def _f_icnd(self):
        code = "SUBROUTINE ICND(NDIM,PAR,ICP,NINT,U,UOLD,UDOT,UPOLD,FI,IJAC,DINT)\n\n"
        code += self._f_ind + "IMPLICIT NONE\n"
        code += self._f_ind + "INTEGER, INTENT(IN) :: NDIM, ICP(*), NINT, IJAC\n"
        code += self._f_ind + "DOUBLE PRECISION, INTENT(IN) :: PAR(*)\n"
        code += (
            self._f_ind
            + "DOUBLE PRECISION, INTENT(IN) :: U(NDIM), UOLD(NDIM), UDOT(NDIM), UPOLD(NDIM)\n"
        )
        code += self._f_ind + "DOUBLE PRECISION, INTENT(OUT) :: FI(NINT)\n"
        code += self._f_ind + "DOUBLE PRECISION, INTENT(INOUT) :: DINT(NINT,*)\n\n"
        code += "END SUBROUTINE ICND"
        return code

    def _f_fopt(self):
        code = "SUBROUTINE FOPT(NDIM,U,ICP,PAR,IJAC,FS,DFDU,DFDP)\n\n"
        code += self._f_ind + "IMPLICIT NONE\n"
        code += self._f_ind + "INTEGER, INTENT(IN) :: NDIM, ICP(*), IJAC\n"
        code += self._f_ind + "DOUBLE PRECISION, INTENT(IN) :: U(NDIM), PAR(*)\n"
        code += self._f_ind + "DOUBLE PRECISION, INTENT(OUT) :: FS\n"
        code += (
            self._f_ind + "DOUBLE PRECISION, INTENT(INOUT) :: DFDU(NDIM),DFDP(*)\n\n"
        )
        code += "END SUBROUTINE FOPT"
        return code

    def _f_pvls(self):
        code = "SUBROUTINE PVLS(NDIM,U,PAR)\n\n"
        code += self._f_ind + "IMPLICIT NONE\n"
        code += self._f_ind + "INTEGER, INTENT(IN) :: NDIM\n"
        code += self._f_ind + "DOUBLE PRECISION, INTENT(IN) :: U(NDIM)\n"
        code += self._f_ind + "DOUBLE PRECISION, INTENT(INOUT) :: PAR(*)\n\n"
        code += "END SUBROUTINE PVLS"
        return code

    def write_func_file(self, basedir="./", silent=False):
        fname = os.path.join(basedir, self.problem.problem_name + ".f90")
        code = self._f_func() + "\n\n"
        code += self._f_stpnt() + "\n\n"
        code += self._f_bcnd() + "\n\n"
        code += self._f_icnd() + "\n\n"
        code += self._f_fopt() + "\n\n"
        code += self._f_pvls()
        with open(fname, "w") as outfile:
            outfile.write(code)
        if not silent:
            print(f"File {fname:s} written.")

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
            print(f"File {fname:s} written.")

    def solve(self):
        ddir = DataDir(name=self.problem.problem_name)
        ddir.create_dir()
        dirc = str(ddir)
        self.solution_dir = dirc
        self.write_func_file(basedir=dirc, silent=True)
        self.write_const_file(basedir=dirc, silent=True)
        self.run_auto(dirc)
        self.problem._solved = True
        self.problem.solution = BifurcationProblemSolution()
        self.problem.solution.read_solution(dirc)

    def run_auto(self, dirc):
        p_name = self.problem.problem_name
        print(f"Compiling FORTRAN source for problem {p_name}")
        env = setup_auto_exec_env()
        auto_lib_dir = env["LD_LIBRARY_PATH"]
        compile_cmd = [
            "gfortran",
            "-O",
            "-c",
            f"{p_name}.f90",
            "-o",
            f"{p_name}.o",
        ]
        print(" ".join(compile_cmd))

        # ["@r", self.problem.problem_name]
        try:
            compile_process = Popen(
                compile_cmd,
                stderr=PIPE,
                stdout=PIPE,
                cwd=dirc,
            )
            out, err = compile_process.communicate()
        except FileNotFoundError:
            # This should mean gfortran is not installed
            raise OSError(
                "Something went wrong when calling the "
                "Fortran compiler. Maybe gfortran is not installed?"
            )

        print(f"Linking...")
        link_cmd = [
            "gfortran",
            f"-L{auto_lib_dir}",
            "-O",
            f"{p_name}.o",
            "-lauto",
            "-o",
            f"{p_name}.out",
        ]
        print(" ".join(link_cmd))

        link_process = Popen(link_cmd, cwd=dirc, stderr=PIPE, stdout=PIPE, env=env)

        out, err = link_process.communicate()
        print(f"Running executable {p_name}")
        parameters = open(os.path.join(dirc, f"c.{p_name}"))
        run_cmd = [f"./{p_name}.out"]
        run_process = Popen(
            run_cmd,
            cwd=dirc,
            stderr=PIPE,
            stdout=PIPE,
            stdin=parameters,
            env=env,
            universal_newlines=True,
        )

        out, err = run_process.communicate()
        print(out)
        print(err)

    def delete_last_solution(self):
        shutil.rmtree(self.solution_dir)


class BifurcationProblemSolution:
    def __init__(self):
        pass

    def read_solution(self, dirc):
        self.reader = AutoOutputReader(dirc)
        self.raw_data = self.reader.read_raw_data()
