from __future__ import annotations

import re

_PIP_INSTALL_RE = re.compile(
    r"""(?ix)
    ^\s*
    pip(?:3)?                # pip / pip3
    \s+install
    \s+
    (?P<spec>\S+)            # first argument to pip install
    """
)


def infer_pypi_project_from_piplink(pip_link: str | None) -> str | None:
    """Infer the PyPI project name from a compiled catalog `pipLink` string.

    This is intentionally conservative: it refuses URL/git-based installs and
    strips common version specifiers and extras.
    """
    if not isinstance(pip_link, str) or not pip_link.strip():
        return None
    m = _PIP_INSTALL_RE.match(pip_link)
    if not m:
        return None
    spec = m.group("spec").strip().strip('"').strip("'")
    if not spec:
        return None
    if "://" in spec or spec.startswith("git+"):
        return None
    base = spec.split("==", 1)[0].split(">=", 1)[0].split("<=", 1)[0].split("~=", 1)[0]
    base = base.split("[", 1)[0]
    base = base.strip()
    return base or None
