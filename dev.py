#!/usr/bin/env python3

import argparse
from glob import glob
import shlex
import shutil
import subprocess
from pathlib import Path

THIS_DIRECTORY = Path(__file__).parent.absolute()
EXAMPLE_DIRECTORIES = (d for d in (THIS_DIRECTORY / 'examples').iterdir() if d.is_dir())

# Utilities function
def run_verbose(cmd_args, *args, **kwargs):
    kwargs.setdefault("check", True)
    cwd = kwargs.get('cwd')
    message_suffix = f" [CWD: {Path(cwd).relative_to(THIS_DIRECTORY)}]" if cwd else ''

    print(f"$ {shlex.join(cmd_args)}{message_suffix}", flush=True)
    subprocess.run(cmd_args, *args, **kwargs)


# Commands
def cmd_example_npm_install(args):
    """"Install all node dependencies for all examples"""
    for example_dir in EXAMPLE_DIRECTORIES:
        run_verbose(["npm", "install"], cwd=str(example_dir / "frontend"))


def cmd_example_npm_build(args):
    """"Build javascript code for all examples"""
    for example_dir in EXAMPLE_DIRECTORIES:
        run_verbose(["npm", "run", "build"], cwd=str(example_dir / "frontend"))

COMMMANDS = {
    "examples-npm-install": cmd_example_npm_install,
    "examples-npm-build": cmd_example_npm_build,
}

# Parser    
def get_parser():
    parser = argparse.ArgumentParser(prog=__file__)
    subparsers = parser.add_subparsers(dest="subcommand", metavar="COMMAND")
    subparsers.required = True
    for commmand_name, command_fn in COMMMANDS.items():
        subparsers.add_parser(commmand_name, help=command_fn.__doc__).set_defaults(func=command_fn)
    return parser


# Main function
def main():
    parser = get_parser()
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
