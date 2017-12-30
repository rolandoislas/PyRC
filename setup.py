#!/usr/bin/env python3

from distutils.core import setup

from setuptools import find_packages

from src.data import constants

setup(name="pyrc",
      version=constants.VERSION,
      description="Twitch Python IRC Client",
      install_requires=[],
      packages=find_packages(),
      include_package_data=True,
      scripts=["src/pyrc"]
      )
