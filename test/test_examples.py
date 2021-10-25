import pyfurc as pf


def test_solving_symmetric(symmetric_bifurcation_problem):
    bf = symmetric_bifurcation_problem
    solver = pf.BifurcationProblemSolver(bf)
    solver.solve()
    tol = 1e-5
    # Critical Point is at P=1.
    assert abs(bf.solution.raw_data[1]["PAR(1)"][0] - 1.0) < tol
    assert abs(bf.solution.raw_data[2]["PAR(1)"][0] - 1.0) < tol
    solver.delete_last_solution()
