import pytest
import pyfurc as pf
import sympy as sp

@pytest.fixture()
def symmetric_bifurcation_problem():
    """Standard BifurcationProblem fixture for testing. Uses hinged cantilever, i.e. symmetric bifurcation with normalized parameters.
    """
    phi = pf.PhysicalQuantity("\\varphi", quantity_type="DOF")
    P = pf.PhysicalQuantity("P", quantity_type="load")
    
    # first bifurcation point will be at exactly P = 1, phi = 0
    V = pf.Energy(1/2*phi**2-P*(1-sp.cos(phi)))
    
    bf = pf.BifurcationProblem(V, name="hinged_cantilever")
    # Set maximum load to double the critical load
    bf.set_parameter("RL1", 2.)
    
    return bf