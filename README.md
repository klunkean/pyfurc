# pyfurc
This package enables energetic equilibrium calculations as encountered in mechanical stability problems using AUTO-07p from within python.

# 1 Prerequisites
Please use a Linux system for everything. I have no idea if and how everything works under Windows / MacOS.

## 1.1 Windows Subsystem for Linux (WSL)

* For installing WSL first follow the 6 manual installation steps found here:
https://docs.microsoft.com/en-us/windows/wsl/install-win10
In step 6 make sure to use Ubuntu.

* Install Windows Terminal from the Windows Store

* Open Windows Terminal and create a new Ubuntu Tab (Found in the drop down arrow right next to the plus in the top bar)

**Accessing Windows file system from within Linux**
We can access the windows file system from the`/mnt/c` for example:
`cd /mnt/c/Users/Andre/Desktop` for Andre's Desktop.

**Accessing Linux file system with Windows Explorer**
* Make sure your Linux subsystem is running (open up a Ubuntu Windows Terminal)
* Open up Windows explorer and enter `\\wsl$` into the address bar

## 1.2a Step-by-step WSL guide to installing AUTO-07p
0. Open a Ubuntu Windows Terminal (see above) and install the Fortran compiler `gfortran`, the C++ Compiler `g++` and the compilation utility `make` in the Linux subsystem (prerequisite for AUTO-07p) :
```shell
sudo apt-get update
sudo apt install gfortran
sudo apt install make
sudo apt install g++
```
1. Using your standard browser in Windows, download AUTO-07p via SourceForge:
https://sourceforge.net/projects/auto-07p/
2. In the Ubuntu Terminal, create a directory to store the AUTO-07p code in:

```shell
mkdir ~/.local
mkdir ~/.local/bin
```

2. In the Terminal, move the downloaded file from its download location to the directory we just created. For me, the archive was downloaded to `C:\Users\Andre\Downloads` so I used

```shell
mv /mnt/c/Users/Andre/Downloads/auto07p-0.9.1.tar.gz ~/.local/bin
```
3. Change into the newly created directory 

```shell
cd ~/.local/bin
```

4. Extract the archive

```shell
tar zxvf auto07p-0.9.1.tar.gz
```

5. Change into the 07p directory

```shell
cd ~/.local/bin/auto/07p
```

6. Run

```shell
./configure --enable-plaut=no --enable-plaut04=no
```

7. If configuration was successful, run 
```shell
make
```

8. After compilation is done type `make clean` to remove auxiliary files

9. In a Windows Explorer Window navigate to `\\wsl$\Ubuntu\home\username\.local\bin\auto\07p\cmds` 
    * open the file `auto.env.sh` with a text editor (e.g. notepad++)
    * change the line  
    `AUTO_DIR=$HOME/auto/07p`
    to 
    `AUTO_DIR=$HOME/.local/bin/auto/07p`
    * save and close the file

10. In a Windows Explorer Window navigate to `\\wsl$\Ubuntu\home` 
    * open the file `.bashrc` with a text editor
    * append the line 
    ```shell
    source $HOME/.local/bin/auto/07p/cmds/auto.env.sh
    ```
    * save and close the file

11. Go back to the Ubuntu Terminal and type
```shell
source ~/.bashrc
```
12. First check if it might have worked: 
Type `@r` and hit enter. If your output is something like
```shell
xxx/auto/07p/cmds/@r: cannot open c..: No such file
```
Then it is likely that the installation was successful. Likewise, if the output is 

```shell
@r: command not found
```

something went wrong.

## 1.2b Installing AUTO-07p on Linux
Download AUTO-07p via SourceForge:
https://sourceforge.net/projects/auto-07p/

Once you have downloaded the archive `auto07p-x.x.x.tar.gz`:
1. Extract the archive
2. (optional) Move the extracted directory `auto` to another location. I chose `~/.local/bin`
3. Open a terminal in the directory `~/.local/bin/auto/07p`
4. Run `./configure --enable-plaut=no --enable-plaut04=no`
5. If configuration was successful, run `make` (in the same directory)
6. After compilation is done type `make clean` to remove auxiliary files

To make AUTO-07p commands usable you need to make a change in the environment file `auto/07p/cmds/auto.env.sh`. Open that file and change the line  
```shell
AUTO_DIR=$HOME/auto/07p
```
to 
```shell
AUTO_DIR=$HOME/.local/bin/auto/07p
```

Now source that environment file. If you're using `bash` or something similar, just add the line

```shell
source xyz/auto/07p/cmds/auto.env.sh
```

to your `~/.bashrc` file.

Now close your terminal and open a new one, type `@r` and hit enter. If your output is:

```shell
xyz/auto/07p/cmds/@r: cannot open c..: No such file
```

Then it is likely that the installation was successful. Likewise, if the output is 

```shell
@r: command not found
```

something went wrong.

# 2 Installing pyfurc
You will need python 3.8 or higher for everything to work as intended. This is the version included in the latest Ubuntu LTS release (20.04). I recommend pyenv for managing different python versions if you need to install a newer version.

For installation you will also need the python package manager `pip`. On Ubuntu and similar systems you can install `pip` by typing 
```shell
sudo apt install python3-pip
```

## 2.1 Installation
To install pyfurc type

```shell
pip3 install git+https://git.tu-berlin.de/klunkean/pyfurc
```

## 2.2 Testing
Open up a python 3 console and type `import pyfurc` if there is no error message the installation should have been successful.

# 3 Installing and using Jupyter-Notebook on WSL
This is optional but I really like jupyter-notebooks maybe you do too.

## 3.1 Installation
Open up a Ubuntu Terminal and run
```shell
pip3 install notebook
```
All done! 

In the Ubuntu Terminal now run 
```shell
jupyter notebook
```

The output should contain 
```
http://localhost:8888/?token=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```
somewhere. Copy the part after `token=`, i.e. the `xxxxxx...` from above.

Now open your favorite browser in Windows and navigate to
```
127.0.0.1:8888
```
For future convenience set a password at the bottom of the page! Here you must supply the token we just copied.

Once you have set the password you're redirected to jupyter's landing page showing you the home directory of your Ubuntu file system (should be empty).

On the top right, click "new" -> "python3". 

Now you have a jupyter notebook to play with. Type 
```python
print("Hello World!")
```
in the first cell and hit Ctrl+Enter. 

# 4 A first Example: Hinged cantilever

Consider the following system:

![hinged_cant.png](doc/img/hinged_cant.png)

The total energy in the system is given by
```math
\begin{aligned}
V(\varphi) &= U(\varphi)-P\mathcal E(\varphi)\\&=\frac12 c_\mathrm{T}\varphi^2-F\ell\left(1-\cos\varphi\right)
\end{aligned}
```
## 4.1 Implementing this problem using pyfurc

First we import needed modules

```python
import pyfurc as pf
import sympy as sp
from math import pi
```
### 4.1.1 Defining physical quantities

Let us first define all contained variables as `pyfurc.PhysicalQuantity`.

It is important to set the `quantity_type` kwarg which may be one of `DOF`, `load` or `parameter`. 

The `value` kwarg is optional (default=0.0) and will set the initial values if `quantity_type` is `DOF` or `load`, or the fixed constant value if `quantity_type` is `parameter`. The values can be changed later.


```python
phi = pf.PhysicalQuantity("\\varphi", quantity_type="DOF", value=0.0)
P = pf.PhysicalQuantity("P", quantity_type="load", value=0.0)
cT = pf.PhysicalQuantity("c_T", quantity_type="parameter", value=10/pi)
ell = pf.PhysicalQuantity("ell", quantity_type="parameter", value=0.5)
```

Next we define the energy expression using these quantites as a sympy expression. This is possible since `PhysicalQuantity` is a subclass of `sympy.Symbol`.

### 4.1.2 Defining the energy
First we define the energy as a symbolic expression `V_expr`
```python
V_expr = 1/2*cT*phi**2-P*ell*(1-sp.cos(phi))
```

To use this energy expression for the bifurcation analysis we create a `pyfurc.Energy` object from this expression:


```python
V = pf.Energy(V_expr)
```

We can print information about the energy:


```python
V.info()
```
Output:

    Potential energy with 1 DOF(s):
    -P*ell*(-cos(\varphi) + 1) + 0.5*\varphi**2*c_T
    
    The DOFs are:
    	\varphi - Fortran Name: U(1) - Init. Value: 0.000000
    The parameters are:
    	c_T - Fortran Name: PAR(2) - Value: 3.183099
    	ell - Fortran Name: PAR(3) - Value: 0.500000
    The load is:
    	P - Fortran Name: PAR(1) - Init. Value: 0.000000
    


Or directly access the information dicts `params`, `dofs` or `load`, e.g.:


```python
print(V.params)
```
Output:

    {c_T: {'name': 'PAR(2)', 'value': 3.183098861837907}, ell: {'name': 'PAR(3)', 'value': 0.5}}



The `pyfurc.Energy` class can also determine and output the equilibrium equations as symbolic objects:


```python
V.equilibrium()
```
Output:

```math
[ - P \ell \sin{\left (\varphi \right )} + 1.0 \varphi c_{T}]
```

The derivatives are calculated symbolically using sympy.

### 4.1.3 Defining the Bifurcation Problem

Now having defined a `pyfurc.Energy`, we use this energy to setup our bifurcation problem to be solved. Let us initialize a `pyfurc.BifurcationProblem` with the name `hinged`. The name will be used for the AUTO files.


```python
bf = pf.BifurcationProblem(V, name="hinged")
```

The problem class contains all calculation parameters which can be printed as follows:


```python
bf.print_parameters()
```
Output:

    NTST	: 50
    IAD	: 3
    EPSL	: 1e-07
    EPSU	: 1e-07
    EPSS	: 1e-05
    ITMX	: 8
    ITNW	: 5
    DS	: 0.1
    DSMIN	: 0.001
    DSMAX	: 0.2
    IADS	: 1
    STOP	: []
    NMX	: 200
    RL0	: 0.0
    RL1	: 0.0
    MXBF	: 10
    NPR	: 200
    IID	: 2
    IPLT	: 0
    UZR	: {}
    UZSTOP	: {}
    


Refer to the AUTO documentation for detailed descriptions of the parameters. The names are identical with the names used in the AUTO `c.xxx` file

To change a parameter we use the `set_parameter(name, value)` method. For example we set the maximum load `RL1`, as above, to a value of `12.73`:


```python
bf.set_parameter("RL1", 12.73)
```
### 4.1.4 Defining the solver

Having defined the problem we can instantiate a `BifurcationProblemSolver` object which handles the AUTO code generation and execution.


```python
solver = pf.BifurcationProblemSolver(bf)
```

To solve the problem we call the `solve()` method:


```python
solver.solve()
```

Output:

    Running AUTO on problem hinged
    ------------------------------------------------------------------------
    gfortran -fopenmp -O -c hinged.f90 -o hinged.o
    gfortran -fopenmp -O hinged.o -o hinged.exe /home/andre/localtu/prog/auto/07p/lib/*.o
    Starting hinged ...
    
      BR    PT  TY  LAB    PAR(1)        L2-NORM         U(1)     
       1     1  EP    1   0.00000E+00   0.00000E+00   0.00000E+00
       1    33  BP    2   6.36620E+00   0.00000E+00   0.00000E+00
       1    65  EP    3   1.27662E+01   0.00000E+00   0.00000E+00
    
      BR    PT  TY  LAB    PAR(1)        L2-NORM         U(1)     
       2    59  EP    4   1.28314E+01   1.90442E+00   1.90442E+00
    
      BR    PT  TY  LAB    PAR(1)        L2-NORM         U(1)     
       2    59  EP    5   1.28314E+01   1.90442E+00  -1.90442E+00
    
     Total Time    0.628E-02
    hinged ... done
    
    ------------------------------------------------------------------------


The `BifurcationProblem` we just solved now has an attribute `solution` which (for now) only contains raw data we can plot manually (you need to install `matplotlib` for this: `pip3 install matplotlib`)


```python
import matplotlib.pyplot as plt
for dat in bf.solution.raw_data:
    plt.plot(dat["U(1)"], dat["PAR(1)"])
```

Output:

![png](doc/img/hinged_bifurcation_plot.png)


The post-processing capabilities are to be extended soon.

## 4.2 Summary and whole code

This is what we have done:

* Define `PhysicalQuantity` objects and set values
* Define `Energy` Object
* Define `BifurcationProblem` object and set parameters
* Define `BifurcationProblemSolver` object and call `solve` method
* Plot results from `BifurcationProblem.solution` 

## 4.3 Runnable Code:
```python
import pyfurc as pf
import sympy as sp
from math import pi
import matplotlib.pyplot as plt

# Physical quantities
phi = pf.PhysicalQuantity("\\varphi", quantity_type="DOF", value=0.0)
P = pf.PhysicalQuantity("P", quantity_type="load", value=0.0)
cT = pf.PhysicalQuantity("c_T", quantity_type="parameter", value=10/pi)
ell = pf.PhysicalQuantity("ell", quantity_type="parameter", value=0.5)

# Energy
V_expr = 1/2*cT*phi**2-P*ell*(1-sp.cos(phi))
V = pf.Energy(V_expr)

# BifurcationProblem
bf = pf.BifurcationProblem(V, name="hinged")
bf.set_parameter("RL1", 12.73)  #set maximum load

# BifurcationProblemSolver
solver = pf.BifurcationProblemSolver(bf)
solver.solve()  # solve problem

# Plot solution (manually)
for dat in bf.solution.raw_data:
    plt.plot(dat["U(1)"], dat["PAR(1)"])
```

Output 

    Running AUTO on problem hinged
    ------------------------------------------------------------------------
    gfortran -fopenmp -O -c hinged.f90 -o hinged.o
    gfortran -fopenmp -O hinged.o -o hinged.exe /home/andre/localtu/prog/auto/07p/lib/*.o
    Starting hinged ...
    
      BR    PT  TY  LAB    PAR(1)        L2-NORM         U(1)     
       1     1  EP    1   0.00000E+00   0.00000E+00   0.00000E+00
       1    33  BP    2   6.36620E+00   0.00000E+00   0.00000E+00
       1    65  EP    3   1.27662E+01   0.00000E+00   0.00000E+00
    
      BR    PT  TY  LAB    PAR(1)        L2-NORM         U(1)     
       2    59  EP    4   1.28314E+01   1.90442E+00   1.90442E+00
    
      BR    PT  TY  LAB    PAR(1)        L2-NORM         U(1)     
       2    59  EP    5   1.28314E+01   1.90442E+00  -1.90442E+00
    
     Total Time    0.530E-02
    hinged ... done
    
    ------------------------------------------------------------------------

# pyfurc roadmap:

* Add support for continuous systems (Ritz)
* Automatic assembly of the Hessian, symbolic determination of critical points
* Automatic evaluation of the stability of equilibrium paths
* Expand postprocessing capabilities
