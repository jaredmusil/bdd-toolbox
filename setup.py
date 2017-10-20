#!/usr/bin/env python

from cx_Freeze import setup, Executable

includes = []
excludes = []
packages = []
include_files = [r'README.md',
                 r'bin/extra/',
                 r'bin/data/',
                 r'bin/img/']

setup(
    name='BDD Toolbox',
    description='BDD Toolbox',
    author='Jared Musil',
    author_email='jared.musil.kbw5@statefarm.com',
    url='s.f/bdd-toolbox',
    executables = [Executable(r'bin/app.py')],
    options={'build_exe': {'excludes': excludes,
                           'packages': packages,
                           'include_files': include_files}}
)
