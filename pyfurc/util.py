from sympy.printing.fortran import FCodePrinter
from time import localtime
from datetime import date
from os import system, path
from pandas import read_csv

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

    def _print_Zero(self,expr):
        return "0.0d0"


class DataDir(object):
    def __init__(self, base_dir="./", name=""):
        self.date = date.today()
        self.time = localtime()
        self.date_time = "".join(
            [
                str(self.date.year),
                str(self.date.month),
                str(self.date.day),
                "_",
                "{:02.0f}".format(self.time[3]),
                "{:02.0f}".format(self.time[4]),
                "{:02.0f}".format(self.time[5]),
            ]
        )
        self.directory = "".join([base_dir + name + "_", self.date_time, "/"])
        self.codedir = self.directory + "code/"
        self.dirCreated = False

    def create(self):
        system("".join(["mkdir ", self.directory]))
        self.dirCreated = True

    def dir(self):
        return self.directory

    def __str__(self):
        return self.directory

    def createSubDir(self, name):
        system("".join(["mkdir ", self.directory, "/", name]))
        if not self.dirCreated:
            self.dirCreated = True
            system("".join(["mkdir ", self.directory]))
        return self.directory + "/" + name + "/"


class ParamDict(dict):
    def __str__(self):
        out = ""
        for name, val in self.items():
            out += "{:s}\t: {:s}\n".format(name, str(val))
        return out


class AutoOutputReader(object):
    def __init__(self, dirc):
        self.dirc = dirc
        self.outfile7 = path.join(self.dirc, "fort.7")

    def read_raw_data(self):
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
        with open(self.outfile7, "r") as data_file:
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


