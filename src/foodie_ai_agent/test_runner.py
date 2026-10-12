"""Helpers for running pytest in locked-down Windows environments."""

from __future__ import annotations

import os
import sys

import pytest


def main() -> int:
    """Run pytest with third-party plugin autoload disabled.

    Returns:
        Exit code returned by pytest.

    Raises:
        SystemExit: Raised by the Python interpreter when used via ``python -m``.
    """
    os.environ.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")
    return pytest.main(sys.argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
