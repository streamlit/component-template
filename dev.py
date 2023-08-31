#!/usr/bin/env python3
"""
A tool to support the maintenance of templates and examples in this repository.
Something like a Makefile but written in Python for easier maintenance.

To list the available commands, run ./dev.py --help.
"""
import argparse
import glob
import tempfile
import typing
import shlex
import subprocess
from pathlib import Path
import json
import sys
import shutil
import os

THIS_DIRECTORY = Path(__file__).parent.absolute()
EXAMPLE_DIRECTORIES = [d for d in (THIS_DIRECTORY / 'examples').iterdir() if d.is_dir()]
TEMPLATE_DIRECTORIES = [
    THIS_DIRECTORY / "template",
    THIS_DIRECTORY / "template-reactless",
]


# Utilities function
def run_verbose(cmd_args, *args, **kwargs):
    kwargs.setdefault("check", True)
    cwd = kwargs.get('cwd')
    message_suffix = f" [CWD: {Path(cwd).relative_to(THIS_DIRECTORY)}]" if cwd else ''

    print(f"$ {shlex.join(cmd_args)}{message_suffix}", flush=True)
    subprocess.run(cmd_args, *args, **kwargs)


# Commands
def cmd_all_npm_install(args):
    """Install all node dependencies for all examples"""
    for project_dir in EXAMPLE_DIRECTORIES + TEMPLATE_DIRECTORIES:
        frontend_dir = next(project_dir.glob("*/frontend/"))
        run_verbose(["npm", "install"], cwd=str(frontend_dir))


def cmd_all_npm_build(args):
    """Build javascript code for all examples and templates"""
    for project_dir in EXAMPLE_DIRECTORIES + TEMPLATE_DIRECTORIES:
        frontend_dir = next(project_dir.glob("*/frontend/"))
        run_verbose(["npm", "run", "build"], cwd=str(frontend_dir))


def cmd_e2e_build_images(args):
    """Build docker images for each component e2e tests"""
    for project_dir in EXAMPLE_DIRECTORIES + TEMPLATE_DIRECTORIES:
        e2e_dir = next(project_dir.glob("**/e2e/"), None)
        if e2e_dir and os.listdir(e2e_dir):
            # Define the image tag for the docker image
            streamlit_version = args.streamlit_version if not args.streamlit_wheel_file else 'custom'
            image_tag = (
                f"component-template:py-{args.python_version}-st-{streamlit_version}-component-{project_dir.parts[-1]}"
            )
            # Build the docker image with specified build arguments
            docker_args = [
                "docker",
                "build",
                ".",
                f"--build-arg=PYTHON_VERSION={args.python_version}",
                f"--tag={image_tag}",
                "--progress=plain",
            ]
            if args.streamlit_wheel_file:
                buildcontext_path = THIS_DIRECTORY / "buildcontext"
                shutil.rmtree(buildcontext_path, ignore_errors=True)
                buildcontext_path.mkdir()
                shutil.copy(args.streamlit_wheel_file, buildcontext_path)
                docker_args.extend([
                    f"--target=e2e_whl",
                ])
            else:
                docker_args.extend([
                    f"--build-arg=STREAMLIT_VERSION={args.streamlit_version}",
                    f"--target=e2e_pip",
                ])
            run_verbose(
                docker_args,
                env={**os.environ, "DOCKER_BUILDKIT": "1"},
            )


def cmd_e2e_run(args):
    """Run e2e tests for all examples and templates in separate docker images"""
    for project_dir in EXAMPLE_DIRECTORIES + TEMPLATE_DIRECTORIES:
        container_name = project_dir.parts[-1]
        image_tag = (
            f"component-template:py-{args.python_version}-st-{args.streamlit_version}-component-{container_name}"
        )
        e2e_dir = next(project_dir.glob("**/e2e/"), None)
        if e2e_dir and os.listdir(e2e_dir):
            run_verbose([
                "docker",
                "run",
                "--tty",
                "--rm",
                "--name", container_name,
                "--volume", f"{e2e_dir.parent}/:/component/",
                image_tag,
                "/bin/sh", "-c",  # Run a shell command inside the container
                "find /component/dist/ -name '*.whl' | xargs -I {} echo '{}[devel]' | xargs pip install && " # Install whl package and dev dependencies
                f"pytest -s --browser webkit --browser chromium --browser firefox --reruns 5 --capture=no"  # Run pytest
            ])


def cmd_docker_images_cleanup(args):
    """Cleanup docker images and containers"""
    for project_dir in EXAMPLE_DIRECTORIES + TEMPLATE_DIRECTORIES:
        container_name = project_dir.parts[-1]
        image_name = (
            f"component-template:py-{args.python_version}-st-{args.streamlit_version}-component-{container_name}"
        )
        e2e_dir = next(project_dir.glob("**/e2e/"), None)
        if e2e_dir and os.listdir(e2e_dir):
            # Remove the associated Docker image
            run_verbose(["docker", "rmi", image_name])


def cmd_all_python_build_package(args):
    """Build wheel packages for all examples and templates"""
    final_dist_directory = (THIS_DIRECTORY / "dist")
    final_dist_directory.mkdir(exist_ok=True)
    for project_dir in EXAMPLE_DIRECTORIES + TEMPLATE_DIRECTORIES:
        run_verbose([sys.executable, "setup.py", "bdist_wheel", "--universal", "sdist"], cwd=str(project_dir))

        wheel_file = next(project_dir.glob("dist/*.whl"))
        shutil.copy(wheel_file, final_dist_directory)


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
    template_deps = json.loads((THIS_DIRECTORY / "template" / "my_component" / "frontend" / "package.json").read_text())
    examples_package_jsons = sorted(next(d.glob("*/frontend/package.json")) for d in EXAMPLE_DIRECTORIES)
    exit_code = 0
    for examples_package_json in examples_package_jsons:
        example_deps = json.loads(examples_package_json.read_text())
        errors = check_deps(template_deps, example_deps)
        if errors:
            print(f"Found error in {examples_package_json.relative_to(THIS_DIRECTORY)!s}")
            print("\n".join(errors))
            print()
            exit_code = 1
    if exit_code == 0:
        print("No errors")

    sys.exit(exit_code)


def cmd_check_test_utils(args):
    """Check that e2e utils files are identical"""
    file_list = glob.glob('**/e2e_utils.py', recursive=True)
    if file_list:
        reference_file = file_list[0]
    else:
        print("Cannot find e2e_utils.py files")
        sys.exit(1)

    for file_path in file_list:
        run_verbose([
            "git",
            "--no-pager",
            "diff",
            "--no-index",
            str(reference_file),
            str(file_path),
        ])


class CookiecutterVariant(typing.NamedTuple):
    replay_file: Path
    repo_directory: Path


COOKIECUTTER_VARIANTS = [
    CookiecutterVariant(
        replay_file=THIS_DIRECTORY / ".github" / "replay-files" / "template.json",
        repo_directory=THIS_DIRECTORY / "template",
    ),
    CookiecutterVariant(
        replay_file=THIS_DIRECTORY / ".github" / "replay-files" / "template-reactless.json",
        repo_directory=THIS_DIRECTORY / "template-reactless",
    ),
]


def cmd_check_templates_using_cookiecutter(args):
    """Checks that templates have been generated by cookiecutter and have no unwanted changes."""
    if shutil.which("cookiecutter") is None:
        raise SystemExit("cookiecutter is not installed")

    for cookiecutter_variant in COOKIECUTTER_VARIANTS:
        replay_file_content = json.loads(cookiecutter_variant.replay_file.read_text())

        with tempfile.TemporaryDirectory() as output_dir:
            print(
                f"Generating template with replay file: {cookiecutter_variant.replay_file.relative_to(THIS_DIRECTORY)}")
            run_verbose(
                [
                    "cookiecutter",
                    "--replay-file",
                    str(cookiecutter_variant.replay_file),
                    "--output-dir",
                    str(output_dir),
                    str(THIS_DIRECTORY / "cookiecutter"),
                ]
            )
            try:
                print(f"Comparing rendered template with local version: {str(cookiecutter_variant.repo_directory)}")
                output_template = (
                        Path(output_dir) / replay_file_content["cookiecutter"]["package_name"]
                )
                run_verbose(
                    [
                        "git",
                        "--no-pager",
                        "diff",
                        "--no-index",
                        str(output_template),
                        str(cookiecutter_variant.repo_directory),
                    ]
                )
            except subprocess.CalledProcessError:
                print("The rendered template contains unexpected changes files.")
                print("To refresh, do the following:")
                print()
                render_cmd = ["./dev.py", "templates-update"]
                print(f"  $ {shlex.join(render_cmd)}")
                sys.exit(1)
        print("All correct. The template directory does not require refreshing.")
        print()


def cmd_update_templates(args):
    """Updates rendered templates using cookiecutter template"""
    if shutil.which("cookiecutter") is None:
        raise SystemExit("cookiecutter is not installed")

    for cookiecutter_variant in COOKIECUTTER_VARIANTS:
        replay_file_content = json.loads(cookiecutter_variant.replay_file.read_text())

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_dir = Path(tmp_dir) / "output-dir"
            output_template = (
                    output_dir / replay_file_content["cookiecutter"]["package_name"]
            )
            print(f"Generating template with replay file: {cookiecutter_variant.replay_file.relative_to(THIS_DIRECTORY)}")
            run_verbose(
                [
                    "cookiecutter",
                    "--replay-file",
                    str(cookiecutter_variant.replay_file),
                    "--output-dir",
                    str(output_dir),
                    str(THIS_DIRECTORY / "cookiecutter"),
                ]
            )
            print(f"Copying rendered templates to {str(cookiecutter_variant.repo_directory.relative_to(THIS_DIRECTORY))!r}")
            shutil.rmtree(cookiecutter_variant.repo_directory, ignore_errors=True)
            shutil.copytree(output_template, cookiecutter_variant.repo_directory)
            print()


ARG_STREAMLIT_VERSION = ("--streamlit-version", "latest", "Streamlit version for which tests will be run.")
ARG_STREAMLIT_WHEEL_FILE = ("--streamlit-wheel-file", "", "")
ARG_PYTHON_VERSION = ("--python-version", os.environ.get("PYTHON_VERSION", "3.11.4"), "Python version for which tests will be run.")

COMMANDS = {
    "all-npm-install": {
        "fn": cmd_all_npm_install
    },
    "all-npm-build": {
        "fn": cmd_all_npm_build
    },
    "all-python-build-package": {
        "fn": cmd_all_python_build_package
    },
    "examples-check-deps": {
        "fn": cmd_example_check_deps
    },
    "templates-check-not-modified": {
        "fn": cmd_check_templates_using_cookiecutter
    },
    "templates-update": {
        "fn": cmd_update_templates
    },
    "e2e-utils-check": {
        "fn": cmd_check_test_utils
    },
    "e2e-build-images": {
        "fn": cmd_e2e_build_images,
        "arguments": [
            ARG_STREAMLIT_VERSION,
            ARG_STREAMLIT_WHEEL_FILE,
            ARG_PYTHON_VERSION,
        ]
    },
    "e2e-run-tests": {
        "fn": cmd_e2e_run,
        "arguments": [
            ARG_STREAMLIT_VERSION,
            ARG_PYTHON_VERSION,
        ]
    },
    "docker-images-cleanup": {
        "fn": cmd_docker_images_cleanup,
        "arguments": [
            (*ARG_STREAMLIT_VERSION[:2], f"Streamlit version used to create the Docker resources"),
            (*ARG_STREAMLIT_WHEEL_FILE[:2], f""),
            (*ARG_PYTHON_VERSION[:2], f"Python version used to create the Docker resources")
        ]
    }
}


# Parser
def get_parser():
    parser = argparse.ArgumentParser(prog=__file__, description=__doc__)
    subparsers = parser.add_subparsers(dest="subcommand", metavar="COMMAND")
    subparsers.required = True
    for command_name, command_info in COMMANDS.items():
        command_fn = command_info['fn']
        subparser = subparsers.add_parser(command_name, help=command_fn.__doc__)

        for arg_name, arg_default, arg_help in command_info.get('arguments', []):
            subparser.add_argument(arg_name, default=arg_default, help=arg_help)

        subparser.set_defaults(func=command_fn)

    return parser


# Main function
def main():
    parser = get_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
