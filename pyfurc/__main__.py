from ctypes import ArgumentError
from pyfurc.tools import AutoHelper, AutoInstaller
import argparse
import sys


if __name__ == "__main__":
    print("Running __main__")
    parser = argparse.ArgumentParser(description="pyfurc setup helpers")
    parser.add_argument(
        "-i",
        "--install-auto",
        help="Run installation of AUTO-07p.",
        action="store_true",
    )
    parser.add_argument(
        "--use-default",
        help=(
            "Deactivate user feedback during installation and "
            "use default choices for all options."
            "Only usable in combination with --install-auto"
        ),
        action="store_true",
    )
    parser.add_argument(
        "--set-auto-dir",
        help="Write a new AUTO-07p directory to the pyfurc config file.",
        action="store_true",
    )
    args = parser.parse_args()
    if len(sys.argv) == 1:
        parser.print_help()

    if args.install_auto:
        if args.set_auto_dir:
            raise ArgumentError("--set-auto-dir has to be used separately.")
        print("Starting AUTO-07p installation script...")
        ai = AutoInstaller()
        ai.install_auto(fast_forward = args.use_default)

    elif args.set_auto_dir:
        if args.use_default:
            print("--use-default can only be used with --install-auto. ",
             "Ignoring.")
        ai = AutoInstaller()
        ai.write_conf()
