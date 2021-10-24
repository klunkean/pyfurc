import subprocess

from setuptools import setup
from wheel.bdist_wheel import bdist_wheel


class _bdist_wheel(bdist_wheel):
    def run(self):
        subprocess.check_call(["bash", "-x", "scripts/build-auto-07p.sh"])
        super().run()

    def finalize_options(self):
        super().finalize_options()
        # Mark us as not a pure python package
        self.root_is_pure = False

    def get_tag(self):
        python, abi, plat = super().get_tag()
        # We just call external commands, no need to specify the python minor version
        python, abi = "py3", "none"
        return python, abi, plat


setup(cmdclass={"bdist_wheel": _bdist_wheel})
