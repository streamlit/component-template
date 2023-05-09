#!/usr/bin/env python3

import argparse
from glob import glob
import shlex
import subprocess
from pathlib import Path
import json
import sys

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

def check_deps(template_package_json, current_package_json):
    return (
        check_deps_section(template_package_json, current_package_json, 'dependencies') + 
        check_deps_section(template_package_json, current_package_json, 'devDependencies')
    )

def check_deps_section(template_package_json, current_package_json, section_name):
    current_package_deps = current_package_json.get(section_name, dict())
    template_package_deps = template_package_json.get(section_name, dict())
    errors = []
    
    for k, v in template_package_deps.items():
        if k not in current_package_deps:
            errors.append(f'Missing [{k}:{v}] in {section_name!r} section')
            continue
        current_version = current_package_deps[k]
        if current_version != v:
            errors.append(f'Invalid version of {k!r}. Expected: {v!r}. Current: {current_version!r}')
    return errors


def cmd_example_check_deps(args):
    """Checks that dependencies of examples match the template"""
    tempalte_deps = json.loads((THIS_DIRECTORY / "template" / "my_component" / "frontend" / "package.json").read_text())
    examples_package_jsons = sorted(d / "frontend"/ "package.json" for d in EXAMPLE_DIRECTORIES)
    exit_code = 0
    for examples_package_json in examples_package_jsons:
        example_deps = json.loads(examples_package_json.read_text())
        errors = check_deps(tempalte_deps, example_deps)
        if errors:
            print(f"Found erorr in {examples_package_json.relative_to(THIS_DIRECTORY)!s}")
            print("\n".join(errors))
            print()
            exit_code = 1
    if exit_code == 0:
        print("No errors")
            
    sys.exit(exit_code)

COMMMANDS = {
    "examples-npm-install": cmd_example_npm_install,
    "examples-npm-build": cmd_example_npm_build,
    "examples-check-deps": cmd_example_check_deps,
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
