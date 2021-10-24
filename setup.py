import subprocess

from setuptools import setup
from wheel.bdist_wheel import bdist_wheel


class _bdist_wheel(bdist_wheel):
    def run(self):
        import os

        print(f"{os.getcwd()=}")
        subprocess.check_call(["pwd"])
        subprocess.check_call(["ls", "-lha", ".", "scripts"])
        subprocess.check_call(["bash", "scripts/build-auto-07p.sh"])
        super().run()


setup(cmdclass={"bdist_wheel": _bdist_wheel})
