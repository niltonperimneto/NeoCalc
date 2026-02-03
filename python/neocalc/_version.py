import subprocess
import os

def get_git_version():
    try:
        # Check if we are in a git repo
        cwd = os.path.dirname(os.path.abspath(__file__))
        version = subprocess.check_output(
            ["git", "describe", "--tags", "--always", "--dirty"],
            cwd=cwd, 
            stderr=subprocess.DEVNULL
        ).decode("utf-8").strip()
        return version
    except Exception:
        return None

# Fallback version if git lookup fails
__version__ = get_git_version() or "v2026.2-1"
