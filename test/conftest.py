import pytest

# pyfurc local importer to make pyfurc available as pf in tests
@pytest.fixture(scope="session", autouse=True)
def pf():
    import sys, os
    module_path = os.path.abspath(".")
    if module_path not in sys.path:
        sys.path.insert(1, module_path)

    import pyfurc as pf
    return pf