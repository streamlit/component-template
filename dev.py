#!/usr/bin/env python3
"""
A tool to support the maintenance of templates in this repository.
Something like a Makefile but written in Python for easier maintenance.

To list the available commands, run ./dev.py --help.
"""
import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import typing
from pathlib import Path

THIS_DIRECTORY = Path(__file__).parent.absolute()
VERSIONS = ["v1", "v2"]
TEMPLATE_DIRECTORIES = [
    d
    for v in VERSIONS
    if (THIS_DIRECTORY / "templates" / v).is_dir()
    for d in (THIS_DIRECTORY / "templates" / v).iterdir()
    if d.is_dir()
]


# Utilities function
def run_verbose(cmd_args, *args, **kwargs):
    kwargs.setdefault("check", True)
    cwd = kwargs.get("cwd")
    message_suffix = f" [CWD: {Path(cwd).relative_to(THIS_DIRECTORY)}]" if cwd else ""

    print(f"$ {shlex.join(cmd_args)}{message_suffix}", flush=True)
    subprocess.run(cmd_args, *args, **kwargs)


def create_sanitized_copies_excluding_gitignored(
    source_dir_a: Path,
    source_dir_b: Path,
    repo_root: Path,
    destination_base_dir: Path,
) -> typing.Tuple[Path, Path]:
    """
    Create sanitized copies of two directories while excluding files ignored by Git.

    This function is intended for robust, cross-platform directory comparisons (e.g.,
    git diff --no-index) where we want to ignore anything matched by the repository's
    ignore rules (.gitignore, global and excludesfile), but still compare the remaining
    content 1:1.

    Rationale:
    - git diff --no-index does not honor .gitignore rules directly for arbitrary
      directory arguments.
    - Filtering via Git pathspecs is not supported with --no-index in a portable way.
    - By asking Git for the ignored files under source_dir_b (the path inside the
      repo) and excluding those relative paths from BOTH copies, we avoid false
      positives from OS metadata and any user-ignored files.

    Parameters:
    - source_dir_a: First directory to compare (e.g., freshly rendered output).
    - source_dir_b: Second directory to compare (must be within repo_root).
    - repo_root: Root of the Git repository (used to query ignored files).
    - destination_base_dir: Directory where sanitized copies will be created.

    Returns:
    - Tuple[Path, Path]: (sanitized_copy_of_a, sanitized_copy_of_b)
    """
    # Compute the list of ignored files under source_dir_b using Git
    try:
        rel_path_in_repo = source_dir_b.relative_to(repo_root)
        ls_cmd = [
            "git",
            "-C",
            str(repo_root),
            "ls-files",
            "-i",  # list ignored files
            "--exclude-standard",  # honor .gitignore, global ignores, etc.
            "--others",  # show untracked files as well
            "-z",  # null-terminate paths to be robust to special characters
            "--",
            str(rel_path_in_repo),
        ]
        result = subprocess.run(ls_cmd, check=True, stdout=subprocess.PIPE, text=False)
        ignored_absolute_paths = [
            repo_root / p.decode() for p in result.stdout.split(b"\0") if p
        ]
    except (ValueError, subprocess.CalledProcessError):
        # ValueError if source_dir_b is not under repo_root; fallback to no ignores
        ignored_absolute_paths = []

    ignored_relative_to_b = set(
        str(p.relative_to(source_dir_b).as_posix())
        for p in ignored_absolute_paths
        if hasattr(p, "is_relative_to")
        and p.is_relative_to(source_dir_b)
        or (str(p).startswith(str(source_dir_b) + os.sep))
    )

    def build_ignore_filter(source_root: Path):
        def _ignore(dirpath: str, names: typing.List[str]) -> typing.List[str]:
            rel_dir = Path(dirpath).relative_to(source_root)
            to_ignore: typing.List[str] = []
            for name in names:
                candidate = (rel_dir / name).as_posix()
                if candidate in ignored_relative_to_b:
                    to_ignore.append(name)
            return to_ignore

        return _ignore

    sanitized_a = destination_base_dir / "sanitized-output"
    sanitized_b = destination_base_dir / "sanitized-repo"

    shutil.copytree(
        source_dir_a,
        sanitized_a,
        ignore=build_ignore_filter(source_dir_a),
    )
    shutil.copytree(
        source_dir_b,
        sanitized_b,
        ignore=build_ignore_filter(source_dir_b),
    )

    return sanitized_a, sanitized_b


# Commands
def cmd_all_npm_install(args):
    """Install all node dependencies for all templates"""
    for project_dir in TEMPLATE_DIRECTORIES:
        frontend_dir = next(project_dir.glob("*/frontend/"))
        run_verbose(
            [
                "npm",
                "install",
                # 2025-11-07: There is a bug in the postinstall script of a transitive dependency.
                # We can safely ignore the scripts to avoid the bug.
                "--ignore-scripts",
            ],
            cwd=str(frontend_dir),
        )


def cmd_all_npm_build(args):
    """Build javascript code for all templates"""
    for project_dir in TEMPLATE_DIRECTORIES:
        frontend_dir = next(project_dir.glob("*/frontend/"))
        run_verbose(["npm", "run", "build"], cwd=str(frontend_dir))


class CookiecutterVariant(typing.NamedTuple):
    replay_file: Path
    repo_directory: Path
    cookiecutter_dir: Path


COOKIECUTTER_VARIANTS = [
    CookiecutterVariant(
        replay_file=THIS_DIRECTORY
        / ".github"
        / "replay-files"
        / "v1"
        / "template.json",
        repo_directory=THIS_DIRECTORY / "templates" / "v1" / "template",
        cookiecutter_dir=THIS_DIRECTORY / "cookiecutter" / "v1",
    ),
    CookiecutterVariant(
        replay_file=THIS_DIRECTORY
        / ".github"
        / "replay-files"
        / "v1"
        / "template-reactless.json",
        repo_directory=THIS_DIRECTORY / "templates" / "v1" / "template-reactless",
        cookiecutter_dir=THIS_DIRECTORY / "cookiecutter" / "v1",
    ),
    CookiecutterVariant(
        replay_file=THIS_DIRECTORY
        / ".github"
        / "replay-files"
        / "v2"
        / "template.json",
        repo_directory=THIS_DIRECTORY / "templates" / "v2" / "template",
        cookiecutter_dir=THIS_DIRECTORY / "cookiecutter" / "v2",
    ),
    CookiecutterVariant(
        replay_file=THIS_DIRECTORY
        / ".github"
        / "replay-files"
        / "v2"
        / "template-reactless.json",
        repo_directory=THIS_DIRECTORY / "templates" / "v2" / "template-reactless",
        cookiecutter_dir=THIS_DIRECTORY / "cookiecutter" / "v2",
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
                f"Generating template with replay file: {cookiecutter_variant.replay_file.relative_to(THIS_DIRECTORY)}"
            )
            run_verbose(
                [
                    "cookiecutter",
                    "--replay-file",
                    str(cookiecutter_variant.replay_file),
                    "--output-dir",
                    str(output_dir),
                    str(cookiecutter_variant.cookiecutter_dir),
                ]
            )
            try:
                print(
                    f"Comparing rendered template with local version: {str(cookiecutter_variant.repo_directory)}"
                )
                output_template = (
                    Path(output_dir)
                    / replay_file_content["cookiecutter"]["package_name"]
                )
                # Create sanitized copies excluding all files ignored by git in the repo
                sanitized_output, sanitized_repo = (
                    create_sanitized_copies_excluding_gitignored(
                        output_template,
                        cookiecutter_variant.repo_directory,
                        THIS_DIRECTORY,
                        Path(output_dir),
                    )
                )
                run_verbose(
                    [
                        "git",
                        "--no-pager",
                        "diff",
                        "--no-index",
                        str(sanitized_output),
                        str(sanitized_repo),
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
            print(
                f"Generating template with replay file: {cookiecutter_variant.replay_file.relative_to(THIS_DIRECTORY)}"
            )
            run_verbose(
                [
                    "cookiecutter",
                    "--replay-file",
                    str(cookiecutter_variant.replay_file),
                    "--output-dir",
                    str(output_dir),
                    str(cookiecutter_variant.cookiecutter_dir),
                ]
            )
            print(
                f"Copying rendered templates to {str(cookiecutter_variant.repo_directory.relative_to(THIS_DIRECTORY))!r}"
            )
            shutil.rmtree(cookiecutter_variant.repo_directory, ignore_errors=True)
            shutil.copytree(output_template, cookiecutter_variant.repo_directory)
            print()


COMMANDS = {
    "all-npm-install": {"fn": cmd_all_npm_install},
    "all-npm-build": {"fn": cmd_all_npm_build},
    "templates-check-not-modified": {"fn": cmd_check_templates_using_cookiecutter},
    "templates-update": {"fn": cmd_update_templates},
}


# Parser
def get_parser():
    parser = argparse.ArgumentParser(prog=__file__, description=__doc__)
    subparsers = parser.add_subparsers(dest="subcommand", metavar="COMMAND")
    subparsers.required = True
    for command_name, command_info in COMMANDS.items():
        command_fn = command_info["fn"]
        subparser = subparsers.add_parser(command_name, help=command_fn.__doc__)

        for arg_name, arg_default, arg_help in command_info.get("arguments", []):
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
