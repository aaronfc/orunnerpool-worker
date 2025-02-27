#!/usr/bin/env python3
"""
Release script for orunnerpool-worker.

This script automates the process of:
1. Updating the version in pyproject.toml and __init__.py
2. Building the package
3. Uploading it to PyPI

Usage:
    python release.py [major|minor|patch]
    
Example:
    python release.py patch  # Increments the patch version (0.1.2 -> 0.1.3)
    python release.py minor  # Increments the minor version (0.1.2 -> 0.2.0)
    python release.py major  # Increments the major version (0.1.2 -> 1.0.0)
"""

import re
import sys
import subprocess
import os
from pathlib import Path


def get_current_version():
    """Extract the current version from pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    content = pyproject_path.read_text()
    version_match = re.search(r'version\s*=\s*"([^"]+)"', content)
    if not version_match:
        raise ValueError("Could not find version in pyproject.toml")
    return version_match.group(1)


def update_version(current_version, release_type):
    """
    Update the version based on the release type.
    
    Args:
        current_version (str): Current version string (e.g., "0.1.2")
        release_type (str): One of "major", "minor", or "patch"
        
    Returns:
        str: New version string
    """
    major, minor, patch = map(int, current_version.split('.'))
    
    if release_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif release_type == "minor":
        minor += 1
        patch = 0
    elif release_type == "patch":
        patch += 1
    else:
        raise ValueError(f"Invalid release type: {release_type}. Must be one of: major, minor, patch")
    
    return f"{major}.{minor}.{patch}"


def update_pyproject_toml(new_version):
    """Update the version in pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    content = pyproject_path.read_text()
    updated_content = re.sub(
        r'(version\s*=\s*)"([^"]+)"',
        f'\\1"{new_version}"',
        content
    )
    pyproject_path.write_text(updated_content)
    print(f"Updated pyproject.toml with version {new_version}")


def update_init_py(new_version):
    """Update the version in orunnerpool/__init__.py."""
    init_path = Path("orunnerpool/__init__.py")
    content = init_path.read_text()
    updated_content = re.sub(
        r'(__version__\s*=\s*)"([^"]+)"',
        f'\\1"{new_version}"',
        content
    )
    init_path.write_text(updated_content)
    print(f"Updated orunnerpool/__init__.py with version {new_version}")


def build_package():
    """Build the package using build."""
    print("Building package...")
    subprocess.run(["python", "-m", "build"], check=True)
    print("Package built successfully")


def upload_to_pypi():
    """Upload the package to PyPI using twine."""
    print("Uploading to PyPI...")
    subprocess.run(["python", "-m", "twine", "upload", "dist/*"], check=True)
    print("Package uploaded successfully")


def check_dependencies():
    """Check if required dependencies are installed."""
    missing_deps = []
    
    # Check for build
    try:
        import build
        print(f"Found build package version {build.__version__}")
    except ImportError:
        missing_deps.append("build")
    
    # Check for twine
    try:
        import twine
        print(f"Found twine package version {twine.__version__}")
    except ImportError:
        missing_deps.append("twine")
    
    if missing_deps:
        for dep in missing_deps:
            print(f"Error: '{dep}' package is not installed. Install it with: pip install {dep}")
        sys.exit(1)


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ["major", "minor", "patch"]:
        print("Usage: python release.py [major|minor|patch]")
        sys.exit(1)
    
    release_type = sys.argv[1]
    
    # Check if build and twine are installed
    check_dependencies()
    
    # Get current version and calculate new version
    current_version = get_current_version()
    new_version = update_version(current_version, release_type)
    
    # Confirm with user
    print(f"Current version: {current_version}")
    print(f"New version: {new_version}")
    confirmation = input("Do you want to proceed? [y/N]: ")
    
    if confirmation.lower() != 'y':
        print("Release cancelled")
        sys.exit(0)
    
    # Update version in both files
    update_pyproject_toml(new_version)
    update_init_py(new_version)
    
    # Build the package
    build_package()
    
    # Ask for confirmation before uploading to PyPI
    confirmation = input("Do you want to upload to PyPI? [y/N]: ")
    if confirmation.lower() == 'y':
        upload_to_pypi()
    else:
        print("Upload cancelled. Package has been built and is available in the dist/ directory.")


if __name__ == "__main__":
    main() 