"""
Setup file for the digicubes package
"""
from setuptools import setup, find_namespace_packages

def version() -> str:
    """
    Returns the current version of the digicubes server
    """
    return "0.1.2"

def requirements() -> list:
    """
    Returns an array of required packages für the server.
    """
    return open("requirements.txt", "rt").read().splitlines()

setup(
    # Application name:
    name="digicubes-server",
    # Version number:
    version=version(),
    # Application author details:
    author="Klaas Nebuhr, Marion Nebuhr",
    author_email="klaas.nebuhr@gmail.com",
    # License
    license="Apache License Version 2.0",
    # Entry Points
    entry_points={
        'console_scripts' : [
            'start_digicubes=digicubes.server.commandline:run',
            'digicubes=digicubes.server.commandline:evaluate_command'
        ]
    },
    # Packages
    packages=find_namespace_packages(
        include=["digicubes*"]
    ),
    zip_safe=False,
    # Include additional files into the package
    include_package_data=True,
    # Details
    description="The digicubes api server",
    long_description=open("README.rst", "r").read(),
    long_description_content_type='text/x-rst',
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Framework :: AsyncIO",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Operating System :: OS Independent",
    ],
    keywords=(
        "rest digicubes api learning platform"
    ),
    # Dependent packages (distributions)
    install_requires=requirements(),
)
