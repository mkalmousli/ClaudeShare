"""Setup and uninstall entry points (kept apart from the everyday commands)."""
import sys


def uninstall(purge: bool, assume_yes: bool) -> int:
    from .uninstall import run as run_uninstall
    return run_uninstall(purge, assume_yes)


def setup() -> int:
    from setup.main import main as run_setup
    sys.argv = ["setup"]
    run_setup()
    return 0
