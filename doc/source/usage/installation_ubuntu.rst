Installing pyfurc on Ubuntu
***************************
At the end of this guide you ideally have a working environment to use
pyfurc in. 

Introduction
------------
Since pyfurc is intended for inexperienced users, the following sections
will be very verbose and in-depth. This guide assumes no prior knowledge
of how to use either python or the Linux command line. Nevertheless 
sometimes you may have to use your favourite search engine to look up the
usage of a certain command. 

.. note::

    pyfurc **requires a Linux system** to run. So far
    only **Ubuntu** and **Linux Mint** have been tested.

    For **Windows 10** users we provide 
    :doc:`a guide </usage/installation_wsl>` to use
    Ubuntu from within Windows using Windows Subsystem for Linux.


Installing the Prerequisites
----------------------------

For the installation of pyfurc we need Python and the python package 
manager pip. Python comes shipped with Ubuntu but you may have to install
pip. Open a terminal, enter

::

    sudo apt install python3-pip

and hit return. You 