import subprocess

import pyfurc as pf
import pytest


def test_auto_installation():
    """Check if the AUTO command @r is available with the env generated
    by ``AutoHelper.setup_auto_exec_env()``
    """
    ah = pf.AutoHelper()
    env = ah.setup_auto_exec_env()
    with pytest.raises(subprocess.CalledProcessError) as exc_info:
        subprocess.check_output(
            ["@r"], encoding="utf-8", stderr=subprocess.STDOUT, env=env
        )
        # running @r will either raise a command not found or file not found error.
        assert "No such file" in exc_info.value.output
