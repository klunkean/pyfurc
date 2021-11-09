pyfurc Documentation
====================
Welcome to pyfurc's documentation and user guide.

What is pyfurc?
+++++++++++++++
pyfurc is a python module that facilitates calculations for non-linear
mechanical systems exhibiting bifurcations with the generalized
path-following FORTRAN library
`AUTO-07p <http://indy.cs.concordia.ca/auto/>`_ directly in python.

Energy expressions, degrees of freedom and loads are defined
using  `sympy <https://docs.sympy.org/latest/index.html>`_'s
symbolic math processing functionality, and equilibrium equations
are automatically derived symbolically.

pyfurc then

1. generates FORTRAN code for the bifurcation problem,
2. links it with the AUTO-07p library,
3. runs the executable
4. and reads the result into a
   `pandas <https://pandas.pydata.org/docs/user_guide/index.html>`_
   DataFrame for post-processing in python.

The basic functionality looks like this:

.. image:: /_static/img/pyfurc_diagram.png
   :width: 500px
   :align: center

|

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

To get started, check out the Quickstart section below or see the
:ref:`in-depth user guide<User Guide>`.

Quickstart
++++++++++
Prerequisites:

* Running Linux distribution with gfortran installed
* Python 3.8.2+
* pip

For installing pyfurc run

::

   pip3 install pyfurc

.. note::

   If you get an error during installation, make sure you are using
   the most recent version of pip.

Contents
++++++++

.. toctree::
   :maxdepth: 3

   usage/index
   develop/dev_basics
   api/pyfurc
   license
