==================
Installation Guide
==================
At the end of this guide you ideally have a working environment to use pyfurc
in. 

Introduction
============
Since pyfurc is intended for inexperienced users, the following sections
will be very verbose and in-depth. This guide assumes no prior knowledge
of how to use either python or the Linux command line. Nevertheless 
sometimes you may have to use your favourite search engine to look up the
usage of a certain command. 

pyfurc **requires a Linux system** to run. So far
only **Ubuntu** and **Linux Mint** have been tested.

For **Windows 10** users we provide :doc:`a guide </usage/wsl>` to use Ubuntu from within 
Windows  using Windows Subsystem for Linux.

Prerequisites
=============

AUTO-07p
********

.. note::
   From here on we assume a running Ubuntu system. 
   
   Windows 10 users go :doc:`here </usage/wsl>` first.

As a python interface to `AUTO-07p <http://indy.cs.concordia.ca/auto/>`_ 
(`GitHub <https://github.com/auto-07p/auto-07p>`_), pyfurc relies on a
working installation of AUTO-07p. The installation will be covered in this section.

AUTO-07p relies on FORTRAN and C++ for which compilers have to be installed.

In a Ubuntu Terminal enter

::

   sudo apt-get update

and hit return to update the software repositories.
Enter your password when asked.

After updating the repositories is done, enter

::

   sudo apt install gfortran, make, g++

to install the compilers.

Short version for experienced Users
-----------------------------------
.. note::
   This short version is intended for experienced users.

   A step by step guide for Windows Subsystem for Linux users 
   can be found below.

1. Download AUTO-07p via 
   `SourceForge <https://sourceforge.net/projects/auto-07p/>`_

2. Extract the archive ``auto07p-x.x.x.tar.gz``:
   
3. Move the extracted directory to a location where you want `auto`
   to be installed.

   I chose ``~/.local/bin``, replace this with your choice in the following steps.
4. Open a terminal in the directory ``~/.local/bin/auto/07p``
5. Run 
   ::

      ./configure --enable-plaut=no --enable-plaut04=no

6. If configuration was successful, run 
   :: 

      make
      
   in the same directory.

7. After compilation is done type 
   ::

      make clean 
      
   to remove auxiliary files

8. To make AUTO-07p commands usable you need to make a change in the 
   environment file ``auto/07p/cmds/auto.env.sh``. 
   Open that file and change the line

   ::
   
      AUTO_DIR=$HOME/auto/07p

   to the following line. Make sure to insert the directory you chose for
   installation.

   ::
   
      AUTO_DIR=$HOME/.local/bin/auto/07p

9. Source that environment file. If you're using bash or something 
   similar, just add the line

   ::
   
      source $HOME/.local/bin/auto/07p/cmds/auto.env.sh

   to your ``~/.bashrc`` file. Make sure to insert the directory you chose for
   installation.

10. Close your terminal and open a new one, type
    ::
      
      @r 
      
    If your output is:
    ::
   
      xyz/auto/07p/cmds/@r: cannot open c..: No such file
   
    Then it is likely that the installation was **successful**. 
    Likewise, if the output is
    ::
   
      @r: command not found
   
    something went wrong.