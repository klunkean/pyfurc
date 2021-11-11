Pyfurc Tutorial -- The Hinged Cantilever
++++++++++++++++++++++++++++++++++++++++

This tutorial first explains some mechanical and mathematical background
and thereafter the basic usage of pyfurc by solving one of
the simplest example problems in elastic stability.

Problem
-------

Consider the rigid cantilever with length :math:`\ell` shown below.
On the top end it is subject to a dead load :math:`P`. On the bottom
end there is a simple support as well as a torsional spring with
stiffness :math:`c_T`.

.. figure:: ../_static/img/hinged_cantilever.svg
    :width: 230
    :align: center

    Fig. 1: Hinged Cantilever

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
which satisfy the above equation. We constrain ourselves to the
sensible choice :math:`0\leq|\varphi|\leq\frac\pi2`.

Apparently, for :math:`\varphi=0`
we can choose an arbitrary value for :math:`P` and the equilibrium
condition is satisfied. This corresponds to the trivial,
non-deflected solution and we will later see that this equilibrium
state is only stable up to a certain point.

For :math:`\varphi\neq0` let us set
:math:`\bar P=\frac {P\ell}{c_\mathrm{T}}` such that the
relation becomes

.. math::

    \bar P = \frac\varphi{\sin\varphi}\,.

With this expression we have fulfilled our task of finding tuples that
satisfy the equilibrium condition. These solutions are plotted below:

.. figure:: ../_static/img/hinged_eq_plot.svg
    :align: center
    :width: 600

    Fig. 2: Equilibrium paths of the hinged cantilever system:
    The red curve corresponds to the non-trivial solutions, the black
    curve to the trivial solution.

As we can see, for :math:`\bar P>1` we have multiple possible
solutions for :math:`\varphi`. Graphically we can identify
:math:`\bar P=1` as a *critical point* or *bifurcation point*.
This is an example of a *pitchfork bifurcation* which is also
found in the pyfurc logo.

Systems like this, which do not have a unique solution for a given
input are not easily tackled computationally. Standard algorithms
may find only one of many solution paths or never converge to a
solution at all. This is where the FORTRAN program `AUTO-07p` comes
into play in which sophisticated algorithms that can handle
non-uniqueness, bifurcations and unstable solutions are implemented.
Pyfurc facilitates this functionality. But before diving in, let us
introduce a more systematic approach to elastic systems than
taking the Newton equilibrium equations.

2. The Total Potential Energy Method
====================================

This section will give a brief introduction to the total potential
energy (TPE) method which provides a way to systematically tackle a
broad class of elastic systems.
For more a more in-depth introduction we recommend the
book by Thompson & Hunt (1973)\ :footcite:p:`thompson1973general`.

The total potential energy :math:`V` of an elastic system is given by
an internal potential energy :math:`U` minus the work done by external
forces. We restrict ourselves to systems which are subject to only one
load :math:`P`. This load does work along a path :math:`\Delta`. The
internal energy as well as the path :math:`\Delta` may be functions
of the degrees of freedom :math:`Q_i` of the system.

Thus the TPE takes the following general form:

.. math::
    V(Q_i, P)=U(Q_i)-P\Delta(Q_i)\,.

|

 .. exercise:: Before you continue...

    What is the only degree of freedom in our example system?

    Try figuring out the TPE of the hinged cantilever.


The TPE method relies on the following two axioms:

- **Axiom 1**:

  A stationary value of the total potential energy with respect to the
  generalized coordinates is necessary and sufficient for the
  equilibrium of the system.

- **Axiom 2**:

  A complete relative minimum of the total potential energy with respect
  to the generalized coordinates is necessary and sufficient for the
  stability of an equilibrium state.

.. .. note::
..     We cannot give a thorough introduction to the notion of stability
..     at this point.
..     Intuitively speaking: A system in a stable equilibrium state will
..     return to this state after a small excitation. An upright pendulum
..     is an example for an unstable equilibrium state.

Equilibrium
###########

Mathematically the first axiom translates to

.. math::
    \frac{\partial V}{\partial Q_i} = 0 \quad\Leftrightarrow\quad \textrm{Equilibrium}.

Thus, to find equilibrium states of a system we need to

1. identify/define the degrees of freedom,
2. formulate the TPE expression
3. and take its first derivatives w.r.t. all degrees of freedom.

The result is a set of equations (as many as there are
degrees of freedom), the solutions of which correspond to all
equilibrium states of the system.

Let us perform these three steps for our example system from above:

1. The system has only one degree of freedom, the bottom support
   restricts translatory movement in horizontal and vertical
   direction but allows for rotational movement. The
   sensible choice is setting :math:`Q_1=\varphi`.
2. We neglect gravitational potential energy and find that the only
   potential energy in the system is inside the torsional spring,
   thus:

   .. math::
       U(\varphi) = \frac12c_\mathrm{T}\varphi^2

   The force :math:`P` does work along the displacement

   .. math::
       \Delta(\varphi) = \ell(1-\cos\varphi)

   Combining these results gives the TPE

   .. math::
       V(\varphi, P) = \frac12c_\mathrm{T}\varphi^2-P\ell(1-\cos\varphi)

3. Taking the derivative w.r.t to all degrees of freedom, i.e.
   :math:`\varphi`, and applying the first axiom yields:

   .. math::
       \frac{\partial V}{\partial\varphi} = c_\mathrm{T}\varphi - P\ell\sin\varphi=0

The above result is exactly the same equilibrium equation we found by
using Newton's equation of motion. But we got there through a more
systematic approach which
translates well to more complicated systems with more degrees of
freedom.

Stability
#########

The second axiom states that for an equilibrium state to be stable
it has to be a local minimum. Mathematically we can assert this by
taking a Taylor series expansion about an equilibrium state.

Let us suppose we have found an equilibrium state :math:`\bar Q` of
a system with one degree of freedom :math:`Q` using
the above method.
The change in energy
when altering the equilibrium state :math:`\bar Q` by a small amount
:math:`\varepsilon` then reads

.. math::
    V(\bar Q+\varepsilon)-V(\bar Q)=
    \frac1{2!}\frac{\partial^2 V}{\partial Q^2}\bigg|_{Q=\bar Q}\varepsilon^2
    + \frac1{3!}\frac{\partial^3 V}{\partial Q^3}\bigg|_{Q=\bar Q}\varepsilon^3
    + \frac1{4!}\frac{\partial^4 V}{\partial Q^4}\bigg|_{Q=\bar Q}\varepsilon^4+\ldots

Note that the first derivative is missing in the expression above since
for an equilibrium state it has to vanish according to axiom 1. We are
also omitting the load parameter :math:`P` for brevity.

Now for :math:`V(\bar Q)` to be a minimum, i.e. for :math:`\bar Q`
to be a **stable equilibrium** state after axiom 2,
the above change in energy has to be positive for any
:math:`\varepsilon`.
This means that the first nonzero term in the series expansion must be
positive for any :math:`\varepsilon`. It thus has to be a term with an
even power of :math:`\varepsilon` and a positive corresponding
coefficient.

If the whole series is zero the equilibrium is called
**neutrally stable**. Any other case is called an
**unstable equilibrium**.

If

.. math::
    \frac{\partial^2 V}{\partial Q^2}\bigg|_{Q=\bar Q}=0

in an equilibrium state :math:`\bar Q` then the energy function
is locally flat. This implies a change in the system's stability and
is called **singular** or **bifurcation** point.

Let us check the stability for the equilibrium states of our example
system.

.. raw:: html
   :file: ../_static/plotly_graphics/hinged_energy_graph.html
.. Energy surface :math:`V(\varphi, \bar P)` for the Hinged Cantilever

Literature
==========

.. footbibliography::
