import os
api_rst_path = os.path.join("source/api/pyfurc.rst")
with open(api_rst_path, "r") as inf:
    lines = inf.readlines()

with open(api_rst_path, "w") as outf:
    i_line = 0
    while i_line<len(lines):
        line = lines[i_line]
        if "pyfurc package" in line:
            heading = "pyfurc API Reference"
            outl = heading+"\n"+len(heading)*"="+"\n"
            i_line += 2
        elif "Submodules" in line:
            outl = ""
            i_line +=2
        else:
            outl = line
            i_line += 1
        outf.write(outl)