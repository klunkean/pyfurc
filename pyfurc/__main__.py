from tools.install_auto import main as install_auto
from tools.write_conf import write_conf
import argparse

parser = argparse.ArgumentParser(description='pyfurc setup helpers')
parser.add_argument('--install-auto',
                    help='Run install_auto.py.')
