pyfurc User Guide
====================
Welcome to pyfurc's documentation and user guide.

What is pyfurc?
===============
pyfurc is a python module that facilitates calculations for non-linear
mechanical systems exhibiting bifurcations with the generalized 
path-following FORTRAN program `AUTO-07p <http://indy.cs.concordia.ca/auto/>`_
directly in python. 

Using  `sympy <https://docs.sympy.org/latest/index.html>`_ functionality,
energy expressions, degrees of freedom and loads are defined and 
equilibrium equations are automatically derived symbolically.

On that basis, pyfurc generates FORTRAN code for the problem, 
calls the AUTO routines and reads the result into a 
`pandas <https://pandas.pydata.org/docs/user_guide/index.html>`_ DataFrame
for post-processing in python.

Solving a bifurcation problem can be this simple:

::

   import pyfurc as pf
   import sympy as sp
   import matplotlib.pyplot as plt

   phi = pf.PhysicalQuantity("\\varphi", quantity_type="DOF")
   P = pf.PhysicalQuantity("P", quantity_type="load")
   cT = 10/3.1415
   ell = 0.5

   V = pf.Energy(1/2*cT*phi**2-P*ell*(1-sp.cos(phi)))
   bf = pf.BifurcationProblem(V, name="hinged_cantilever")
   bf.set_parameter("RL1", 12.73)  #set maximum load

   solver = pf.BifurcationProblemSolver(bf)
   solver.solve()  # solve problem

   for dat in bf.solution.raw_data:
      plt.plot(dat["U(1)"], dat["PAR(1)"])


Contents
========
.. toctree::
   :maxdepth: 3

   usage/quickstart.rst
   usage/installation.rst
   usage/install_auto.rst
   usage/wsl.rst
   api/apidoc