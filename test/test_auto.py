import pytest
import os
import pyfurc as pf
from subprocess import Popen, PIPE


def test_conf_path():
    """Check if config file exists / if ``AutoHelper.get_conf_path()``
    works.
    """
    ah = pf.AutoHelper()
    auto_path = ah.get_conf_path()
    print(auto_path)
    assert os.path.exists(auto_path)


def test_auto_installation():
    """Check if the AUTO command @r is available with the env generated
    by ``AutoHelper.setup_auto_exec_env()``
    """
    ah = pf.AutoHelper()
    env = ah.setup_auto_exec_env()
    command = ["@r"]
    process = Popen(
        command,
        stdout=PIPE,
        stderr=PIPE,
        bufsize=1,
        universal_newlines=True,
        env=env,
    )
    _, err = process.communicate()

    # running @r will either raise a command not found or file not found error.
    assert "No such file" in err
