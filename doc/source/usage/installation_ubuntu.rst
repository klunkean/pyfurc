Installing pyfurc on Ubuntu
***************************
At the end of this guide you will have pyfurc installed on your system.

Introduction
------------
Since pyfurc is also intended for inexperienced users, the following sections
will be very verbose and in-depth. This guide assumes no prior knowledge
of how to use either Python or the Linux command line. Nevertheless
sometimes you may have to use your favourite search engine to look up the
usage of a certain command.

.. attention::

    pyfurc **requires a Linux system** to run. So far
    only **Ubuntu** and **Linux Mint** have been tested.

    For **Windows 10** users we provide
    :doc:`a guide </usage/installation_wsl>` to use
    Ubuntu from within Windows using Windows Subsystem for Linux.

    A Virtual Machine running Ubuntu should work as well.


Installing the Python package manager pip
-----------------------------------------
For the installation of pyfurc we need Python and the python package
manager pip. Python comes shipped with Ubuntu but you may have to install
pip.

First, open a terminal window. WSL users refer to
:ref:`accessing the ubuntu subsystem` on how to do this.

It should look similar to this:

.. image:: /_static/install_guide/ubuntu_home_only.png

|

Now just enter

.. code-block:: bash

    sudo apt install python3-pip

and hit return to install pip.


Now that the package manager pip is installed, we can use it to install
pyfurc.

Installing pyfurc with pip
--------------------------

Installing the pyfurc python package
++++++++++++++++++++++++++++++++++++

Open a terminal or use the one you may have just used to install pip.

Enter the following line

.. code-block:: bash

    pip3 install pyfurc

and pyfurc will be installed.

Installing gfortran
+++++++++++++++++++
The FORTRAN compiler gfortran is needed for pyfurc to run AUTO-07p.
To install it, type

.. code-block:: bash

    sudo apt install gfortran

Additional suggestion: jupyter notebook
+++++++++++++++++++++++++++++++++++++++

Users without much experience in programming may find it more comfortable to
program in a `jupyter notebook <https://jupyter.org/>`_.

One way to install it is using ``pip``:

.. code-block:: bash

    pip install notebook

Then, take a look at
`this guide <https://jupyter.readthedocs.io/en/latest/running.html#running>`_
to get started with jupyter notebook.
