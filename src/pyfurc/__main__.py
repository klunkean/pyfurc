print("In main before imports")
import argparse
import sys

from pyfurc.tools import AutoHelper, AutoInstaller


def main():
    print(72 * "#" + "\n" "running main" "\n" + 72 * "#")
    parser = argparse.ArgumentParser(description="pyfurc setup helpers")
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-i",
        "--install-auto",
        help="Run installation of AUTO-07p.",
        action="store_true",
    )
    parser.add_argument(
        "--use-defaults",
        help=(
            "Deactivate user feedback during installation and "
            "use default choices for all options."
            "Only usable in combination with --install-auto"
        ),
        action="store_true",
    )
    group.add_argument(
        "--set-auto-dir",
        help="Write a new AUTO-07p directory to the pyfurc config file.",
        action="store_true",
    )
    args = parser.parse_args()
    if len(sys.argv) == 1:
        parser.print_help()

    if args.install_auto:
        print("Starting AUTO-07p installation script...")
        ai = AutoInstaller()
        ai.install_auto(fast_forward=args.use_defaults)

    elif args.set_auto_dir:
        if args.use_defaults:
            print("--use-default can only be used with --install-auto. ", "Ignoring.")
        ai = AutoInstaller()
        ai.write_conf()


if __name__ == "__main__":
    main()
