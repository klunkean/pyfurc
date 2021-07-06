from ctypes import ArgumentError
from pyfurc.tools import AutoHelper, AutoInstaller
import argparse
import sys


if __name__=="__main__":
    parser = argparse.ArgumentParser(description='pyfurc setup helpers')
    parser.add_argument('-i', '--install-auto',
                        help='run guided installation of AUTO-07p.',
                        action='store_true')
    parser.add_argument('--set-auto-dir',
                        help='write a new AUTO-07p directory to the pyfurc config file.',
                        action='store_true')
    args = parser.parse_args()
    if args.install_auto and args.set_auto_dir:
        raise ArgumentError("I can only take one argument at a time.")
    elif len(sys.argv) == 1:
        parser.print_help()

    
    if args.install_auto:
        ai = AutoInstaller()
        ai.install_auto()
    elif args.set_auto_dir:
        ai = AutoInstaller()
        ai.write_conf()