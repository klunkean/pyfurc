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
        self.skip_build = True
        include = []
        distutils_logger.info("Moving auto-07p files")
        # Copy library to wheel. Source dist contains the
        # whole ext/auto-07p directory via MANIFEST.in
        auto_lib_dir = os.path.join(self.distribution.bin_dir, "lib")
        auto_lib_file = os.path.join(auto_lib_dir, "libauto.so")
        install_auto_dir = os.path.join("pyfurc.ext", "auto-07p")
        # include AUTO license file
        license_file = os.path.join(
            self.distribution.bin_dir, "LICENSE"
        )
        license_target_dir = os.path.join(
            self.install_dir, install_auto_dir
        )
        os.makedirs(license_target_dir, exist_ok=True)
        shutil.move(license_file, license_target_dir)

        lib_target_dir = os.path.join(
            self.install_dir, install_auto_dir, "lib"
        )
        os.makedirs(lib_target_dir, exist_ok=True)
        shutil.move(auto_lib_file, lib_target_dir)

        self.distribution.data_files = [
            os.path.join(
                lib_target_dir, os.path.basename(auto_lib_file)
            ),
            os.path.join(
                license_target_dir, os.path.basename(license_file)
            ),
        ]
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

    def log_subprocess_output(self, pipe, debug=False):
        for line in iter(pipe.readline, ""):  # b'\n'-separated lines
            if debug:
                distutils_logger.info(line.rstrip("\n"))
            else:
                distutils_logger.debug(line.rstrip("\n"))

    def build_extension(self, ext):
        if ext.name != self.special_extension:
            # Handle unspecial extensions with the parent class' method
            super().build_extension(ext)

        else:
            distutils_logger.info("Executing auto-07p configuration")
            auto_src_dir = os.path.join("ext", "auto-07p")
            # flags needed for building on a different machine than
            # the one running the code
            env = os.environ.copy()
            env["FFLAGS"] = "-Wall -fPIC"
            manylinux_build_tag = "x86_64-redhat-linux"
            target_build_tag = "x86_64-pc-linux-gnu"
            clean_cmd = [
                "make",
                "superclean"
            ]
            clean_process = subprocess.Popen(
                clean_cmd,
                cwd=auto_src_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
            )
            with clean_process.stdout as stdout, clean_process.stderr as stderr:
                self.log_subprocess_output(stdout, debug=True)
                self.log_subprocess_output(stderr, debug=True)

            configure_cmd = [
                "./configure",
                "--enable-plaut=no",
                "--enable-plaut04=no",
                "--enable-plaut04-qt=no",
                "--enable-gui=no",
                "--without-openmp",
                "--without-mpi",
                f"--host={target_build_tag}",
            ]

            configure_process = subprocess.Popen(
                configure_cmd,
                cwd=auto_src_dir,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
            )
            with configure_process.stdout as stdout:
                self.log_subprocess_output(stdout, debug=True)

            distutils_logger.info("Building auto-07p")
            make_cmd = ["make", "-j3"]
            make_process = subprocess.Popen(
                make_cmd,
                cwd=auto_src_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
            )
            with make_process.stdout as stdout:
                self.log_subprocess_output(stdout, debug=True)

            distutils_logger.info("Building auto-07p library")
            auto_lib_dir = os.path.join(auto_src_dir, "lib")
            build_lib_cmd = [
                "gfortran",
                "-v",
                "-shared",
                "-o",
                os.path.join(auto_lib_dir, "libauto.so"),
            ] + [f for f in glob(os.path.join(auto_lib_dir, "*.o"))]

            build_lib_process = subprocess.Popen(
                build_lib_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
            )

            with build_lib_process.stdout as stdout:
                self.log_subprocess_output(stdout, debug=True)

            self.distribution.bin_dir = os.path.join(auto_src_dir)


setup(
    cmdclass={
        "bdist_wheel": custom_bdist_wheel,
        "install_lib": custom_install_lib,
        "install_data": custom_install_data,
        "build_ext": custom_build_ext,
    },
    ext_modules=[auto_ext],
)
