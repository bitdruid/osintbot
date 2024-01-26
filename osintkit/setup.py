from setuptools import setup, find_packages
from pkg_resources import parse_requirements
from pathlib import Path

from __version__ import __version__

# Get the script path
script_path = Path(__file__).resolve().parent

# Read the requirements file using 'with' statement
with open(script_path / "requirements.txt", encoding="utf-8") as f:
    install_requires = [str(requirement) for requirement in parse_requirements(f)]

setup(
    name='osintkit',
    version=__version__,
    packages=find_packages(),
    install_requires=install_requires,
    entry_points={
        "console_scripts": [
            "osintkit = osintkit.main:main"
        ]
    },
    author='bitdruid',
    author_email='bitdruid@outlook.com',
    description='A Python library for my OSINT-related projects.',
    license='MIT',
)