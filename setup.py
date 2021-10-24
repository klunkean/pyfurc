import subprocess

from setuptools import setup
from wheel.bdist_wheel import bdist_wheel


class _bdist_wheel(bdist_wheel):
    def run(self):
        subprocess.check_call(["bash", "-x", "scripts/build-auto-07p.sh"])
        super().run()


setup(cmdclass={"bdist_wheel": _bdist_wheel})
