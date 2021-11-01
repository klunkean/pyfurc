import subprocess

from setuptools import setup
from setuptools.command.build_ext import build_ext
from setuptools.extension import Extension
from setuptools.command.install_lib import install_lib
from distutils.command.install_data import install_data
from distutils import log as distutils_logger
from wheel.bdist_wheel import bdist_wheel
import os
import shutil
from glob import glob


class custom_bdist_wheel(bdist_wheel):
    # def run(self):
    # subprocess.check_call(
    #     ["bash", "-x", "scripts/build-auto-07p.sh"]
    # )
    # super().run()

    def finalize_options(self):
        super().finalize_options()
        # Mark us as not a pure python package
        self.root_is_pure = False


class custom_install_data(install_data):
    def run(self):
        """
        Outfiles are the libraries that were built using cmake
        """
        self.outfiles = self.distribution.data_files


class custom_install_lib(install_lib):
    def run(self):
        self.announce("Moving auto-07p files", level=3)
        self.skip_build = True
        include = []
        # Copy selected files to wheel. Source dist contains the
        # whole directory via MANIFEST.in
        auto_dir = os.path.join("ext", "auto-07p")
        install_auto_dir = os.path.join("pyfurc.ext", "auto-07p")
        exclude_dirs = ["doc", "python", "test", "demos"]
        for root, dirs, files in os.walk(auto_dir):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for f in files:
                target_dir = os.path.join(
                    self.install_dir, root
                ).replace(auto_dir, install_auto_dir)
                os.makedirs(target_dir, exist_ok=True)
                shutil.move(os.path.join(root, f), target_dir)

                include.append(f)

        # self.distribution.data_files = include

        self.distribution.run_command("install_data")

        super().run()


auto_ext = Extension(
    "auto-07p.ext",
    sources=[],
)


class custom_build_ext(build_ext):
    """
    Specialized builder for auto-07p
    """

    special_extension = auto_ext.name

    def log_subprocess_output(self, pipe):
        for line in iter(pipe.readline, b""):  # b'\n'-separated lines
            distutils_logger.debug(str(line, "utf-8"))

    def build_extension(self, ext):
        if ext.name != self.special_extension:
            # Handle unspecial extensions with the parent class' method
            super().build_extension(ext)

        else:
            distutils_logger.info("Executing auto-07p configuration")
            auto_src_dir = "ext/auto-07p"
            configure_cmd = [
                "./configure",
                "--enable-plaut=no",
                "--enable-plaut04=no",
            ]
            configure_process = subprocess.Popen(
                configure_cmd,
                cwd=auto_src_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
            )
            with configure_process.stdout as stdout:
                self.log_subprocess_output(stdout)

            distutils_logger.info("Building auto-07p")
            make_cmd = ["make", "-j3"]
            make_process = subprocess.Popen(
                make_cmd,
                cwd=auto_src_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
            )
            with make_process.stdout as stdout:
                self.log_subprocess_output(stdout)


setup(
    cmdclass={
        "bdist_wheel": custom_bdist_wheel,
        "install_lib": custom_install_lib,
        "install_data": custom_install_data,
        "build_ext": custom_build_ext,
    },
    ext_modules=[auto_ext],
)
