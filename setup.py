#!/usr/bin/env python3

# Copyright 2017 Facundo Batista

# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# For further info, check  http://github.com/facundobatista/certg

"""Set up certg."""

from distutils.core import setup

setup(
    name='certg',
    version='3.2',
    license='GPL-3',
    author='Facundo Batista',
    author_email='facundo@taniquetil.com.ar',
    description='A certificate generator, from a SVG to a lot of PDFs',
    long_description=open('README.rst').read(),
    url='https://github.com/facundobatista/certg',

    packages=["certg"],
    scripts=["bin/certg"],

    install_requires=['progress', 'pyyaml'],
)
