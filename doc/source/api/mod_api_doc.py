import os

api_rst_path = os.path.join("source/api/pyfurc.rst")
with open(api_rst_path) as inf:
    lines = inf.readlines()

with open(api_rst_path, "w") as outf:
    i_line = 0
    while i_line < len(lines):
        line = lines[i_line]
        if "pyfurc package" in line:
            heading = "pyfurc Reference"
            introduction = """\
                This is the reference page for classes and methods in the
                pyfurc package. It is automatically rendered from
                docstrings in the source code.
                """
            outl = heading + "\n" + len(heading) * "=" + "\n"
            outl += introduction + "\n"
            i_line += 3
        elif "Submodules" in line:
            outl = ""
            i_line += 2
        else:
            outl = line
            i_line += 1
        outf.write(outl)
