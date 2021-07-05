Manually installing AUTO-07p on Ubuntu
**************************************

.. note::
   This guide assumes a running Ubuntu system. 

As a python interface to `AUTO-07p <http://indy.cs.concordia.ca/auto/>`_ 
(`GitHub <https://github.com/auto-07p/auto-07p>`_), pyfurc relies on a
working installation of AUTO-07p. 

.. note::
   It is recommended to use the provided installation script to install AUTO-07p

   ::

      python3 -m pyfurc --install-auto

The manual installation will be covered in the following sections.

AUTO-07p Prerequisites
----------------------
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


Installing AUTO-07p
-------------------

1. ``cd`` into the directory you want AUTO-07p to be installed in
   (e.g. ``~/.local/bin``) and clone the AUTO-07p github repository:
   
   .. code-block:: bash

      git clone https://github.com/auto-07p/auto-07p.git
   
   
2. ``cd`` into the ``auto-07p`` directory and run
   
   .. code-block:: bash

      ./configure --enable-plaut=no --enable-plaut04=no

3. If configuration was successful, run 
   
   .. code-block:: bash

      make
      
   in the same directory.

4. After compilation is done type 
   
   .. code-block:: bash

      make clean 
      
   to remove auxiliary files

Making AUTO-07p usable with pyfurc
----------------------------------

If you successfully completed the above installation of AUTO-07p, you have
to configure pyfurc such that it can find your AUTO-07p installation.

The recommended way is to run

.. code-block:: bash

   python3 -m pyfurc --set-auto-dir

You can also manually edit your pyfurc configuration file. On Ubuntu
it is expected in  ``~/.local/share/pyfurc/pyfurc.conf``. This file only
contains one variable and looks like this:

``pyfurc.conf``

.. code-block:: bash

   [pyfurc]
   auto_dir = /path/to/auto_07p




.. 5. To make AUTO-07p commands usable you need to make a change in the 
..    environment file ``auto-07p/cmds/auto.env.sh``. 
..    Open that file and change the line

..    ::
   
..       AUTO_DIR=$HOME/auto/07p

..    to the following line. Make sure to insert the directory you chose for
..    installation.

..    ::
   
..       AUTO_DIR=$HOME/.local/bin/auto/07p
   
.. 6. Source the environment file. If you're using bash or something 
..    similar, just add the line

..    ::
   
..       source $HOME/.local/bin/auto/07p/cmds/auto.env.sh

..    to your ``~/.bashrc`` file. Make sure to insert the directory you chose for
..    installation.

.. 7.  Close your terminal and open a new one, type
..     ::
      
..       @r 
      
..     If your output is:
..     ::
   
..       xyz/auto/07p/cmds/@r: cannot open c..: No such file
   
..     Then it is likely that the installation was **successful**. 
..     Likewise, if the output is
..     ::
   
..       @r: command not found
   
..     something went wrong.