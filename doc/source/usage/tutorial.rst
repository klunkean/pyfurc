Pyfurc Tutorial -- The Hinged Cantilever
++++++++++++++++++++++++++++++++++++++++

This tutorial explains the basic usage of pyfurc by solving one of
the simplest example problems.

Problem
-------

Consider the rigid cantilever with length :math:`\ell` shown below.
On the top end it is subject to a dead load :math:`P`. On the bottom
end there is a simple support as well as a torsional spring with
stiffness :math:`c_T`.

.. image:: ../_static/img/hinged_cantilever.svg
    :width: 230

|

The angle :math:`\varphi` measures the rotation of the cantilever
with respect to the vertical axis.

Our aim is to find a relationship between the load :math:`P` and
the cantilever rotation :math:`\varphi`.

1. The Introductory Mechanics Approach
======================================

The moment equilibrium taken in the deflected position
(shown right in the figure above) dictates that

.. math::

    P\ell\sin\varphi-c_\mathrm{T}\varphi=0\,.

We now have the task to find all valid tuples :math:`(P,\varphi)`
which satisfy the above equation. Apparently, for :math:`\varphi=0`
we can choose an arbitrary value for :math:`P` and the equilibrium
condition is satisfied. This corresponds to the trivial,
non-deflected solution.

For :math:`\varphi\neq0` let us set
:math:`\bar P=\frac {P\ell}{c_\mathrm{T}}` such that the
relation becomes

.. math::

    \bar P = \frac\varphi{\sin\varphi}\,.
