import subprocess
import shutil
import re
import typing

# Regexp to parse semantic versioning to avoid dependency on external libraries
# For details, see:https://semver.org/#is-there-a-suggested-regular-expression-regex-to-check-a-semver-string
SEMVER_REGEXP = re.compile(
    r"^(?P<major>0|[1-9]\d*)\."
    r"(?P<minor>0|[1-9]\d*)\."
    r"(?P<patch>0|[1-9]\d*)"
    r"(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)

VersionType = typing.Tuple[int, int, int]


def _version_str_to_tuple(version_str) -> VersionType:
    result = SEMVER_REGEXP.match(version_str)
    return int(result['major']), int(result['minor']), int(result['patch'])


def _get_installed_node_version() -> VersionType:
    """Return the node version installed on the device."""
    local_node_version = (
        subprocess.check_output(["node", "--version"]).strip().decode().lstrip("v")
    )
    return _version_str_to_tuple(local_node_version)


def is_node_installed() -> bool:
    """Checks if node is installed on the device."""
    return shutil.which("node") is not None


if not is_node_installed():
    raise SystemExit("Node is not installed.")

MIN_NODE_VERSION = _version_str_to_tuple('16.0.0')
local_node_version = _get_installed_node_version()

if local_node_version < MIN_NODE_VERSION:
    raise SystemExit(
        f"Node version too old. Current version: {local_node_version}. Max supported version: {MIN_NODE_VERSION}."
    )
