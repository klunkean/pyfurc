import pytest
import os
import pyfurc as pf

def test_conf_path():
    auto_path = pf.get_conf_path()
    print(auto_path)
    assert os.path.exists(auto_path)

def test_auto_installation():
    env = pf.setup_auto_exec_env()
    print(env)