from setuptools import setup, find_packages

from __version__ import __version__

from pkg_resources import parse_requirements
import os
scriptpath = os.path.dirname(os.path.realpath(__file__))
install_requires = [str(requirement) for requirement in parse_requirements(open(scriptpath + "/requirements.txt"))]

setup(
    name='osintkit',
    version=__version__,
    packages=find_packages(),
    install_reqires=install_requires,
    entry_points={
        "console_scripts": [
            "osintkit = osintkit.osintkit:main"
        ]
    },
    author='bitdruid',
    author_email='bitdruid@outlook.com',
    description='A Python library for my OSINT-related projects.',
    license='MIT',
)