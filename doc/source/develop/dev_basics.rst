Developer Guide
===============
If you want to contribute to pyfurc, fork the
`git repository <https://github.com/klunkean/pyfurc>`_ and start from
there.

Due to the customized way this module is built including the FORTRAN library
AUTO-07p, a standard ``pip install -e .`` does not work for developing purposes.
Of course, rebuilding and reinstalling the wheel for developing is tedious.

What works for me when only working on the python part is to use a python
``venv`` and alter its activate script such that the environment variable
``PYTHONPATH`` contains the ``src`` directory of the github repo. On
on importing ``pyfurc``, the local repository directory is then the preferred
location.

For everything to
work you additionally have to copy the ``pyfurc.ext`` and ``pyfurc.libs``
directories from a working wheel into the ``src`` directory.

So just ``pip download --no-deps pyfurc``,
unpack the wheel and copy the mentioned directories into the ``src`` folder.
You now basically have an editable install.

Build process
+++++++++++++
A `fork of AUTO-07p <https://github.com/klunkean/auto-07p>`_ is integrated
into the pyfurc git repository as a git submodule.
The build process uses a customized ``setup.py`` which builds
AUTO-07p from source, compiles everything that is needed into one shared
FORTRAN library ``libauto.so`` which is then shipped with the python wheel.

This build process is carried out using
`cibuildwheel <https://github.com/pypa/cibuildwheel>`_ on a manylinux
image and automated using github actions. The options for this are set in
the ``pyproject.toml`` file and the github actions workflow is defined in
``.github/workflows/tests.yml``.

If you want to build the wheel yourself you may run

.. code-block:: bash

    pipx run cibuildwheel --platform=linux

The source distribution is packed using

.. code-block:: bash

    python -m build . --sdist

Github actions is also used to publish the built wheel and sdist of
every tagged commit to the master branch on PyPI.

Documentation
+++++++++++++
The `documentation <https://pyfurc.readthedocs.io/>`_ is written in
reStructuredText and built using
`Sphinx <https://www.sphinx-doc.org/en/master/>`_.
The docs are hosted on `readthedocs <https://readthedocs.org/>`_ and are
built automatically from the master branch.

Testing
+++++++
`Pytest <https://docs.pytest.org/en/6.2.x/>`_ is used for testing.
