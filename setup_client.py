"""
Setupfile for the client
"""
from distutils.core import setup
from setuptools import find_packages

def version() -> str:
    """
    Return the current version
    """
    return "0.0.1"

def requirements() -> list:
    """
    Read the requirements
    """
    return open("requirements.txt", "rt").read().splitlines()

setup(
    # Application name:
    name="digicubes-client",
    # Version number:
    version=version(),
    # Application author details:
    author="Klaas Nebuhr, Marion Nebuhr",
    author_email="klaas.nebuhr@gmail.com",
    # License
    license="Apache License Version 2.0",
    # Packages
    packages=find_packages(include=["digicubes*"], exclude=["digicubes.tests"]),
    zip_safe=True,
    # Include additional files into the package
    include_package_data=False,
    # Details
    description="A easy to use client library for the digicubes plattform",
    long_description=open("README.rst", "r").read(),
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Framework :: AsyncIO",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Operating System :: OS Independent",
    ],
    keywords=(
        "rest digicubes"
    ),
    # Dependent packages (distributions)
    install_requires=requirements(),
)
