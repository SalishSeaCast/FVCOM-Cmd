# Copyright 2013-2017 The Salish Sea MEOPAR Contributors
# and The University of British Columbia

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    https://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""FVCOM-Cmd -- FVCOM command processor
"""
import sys
from setuptools import find_packages, setup

from fvcom_cmd import __pkg_metadata__

python_classifiers = [
    'Programming Language :: Python :: {0}'.format(py_version)
    for py_version in ['2', '2.7', '3', '3.4', '3.5']
]
other_classifiers = [
    'Development Status :: ' + __pkg_metadata__.DEV_STATUS,
    'License :: OSI Approved :: Apache Software License',
    'Programming Language :: Python :: Implementation :: CPython',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: POSIX :: Linux',
    'Operating System :: Unix',
    'Environment :: Console',
    'Intended Audience :: Science/Research',
    'Intended Audience :: Education',
    'Intended Audience :: Developers',
    'Intended Audience :: End Users/Desktop',
]
try:
    long_description = open('README.rst', 'rt').read()
except IOError:
    long_description = ''
install_requires = [
    # see environment-dev.yaml for conda environment dev installation
    # see requirements.txt for package versions used during recent development
    'arrow',
    'attrs',
    'cliff',
    'python-hglib',
    'PyYAML',
]
if sys.version_info[0] == 2:
    install_requires.append('pathlib2')

setup(
    name=__pkg_metadata__.PROJECT,
    version=__pkg_metadata__.VERSION,
    description=__pkg_metadata__.DESCRIPTION,
    long_description=long_description,
    author='Doug Latornell, Michael Dunphy',
    author_email='dlatornell@eoas.ubc.ca, Michael.Dunphy@dfo-mpo.gc.ca',
    #url='http://nemo-cmd.readthedocs.io/en/latest/',   #TODO
    license='Apache License, Version 2.0',
    classifiers=python_classifiers + other_classifiers,
    platforms=['MacOS X', 'Linux'],
    install_requires=install_requires,
    packages=find_packages(),
    entry_points={
        # The fvc command:
        'console_scripts': ['fvc = fvcom_cmd.main:main'],
        # Sub-command plug-ins:
        'fvcom.app': [
            'combine = fvcom_cmd.combine:Combine',
            'deflate = fvcom_cmd.deflate:Deflate',
            'gather = fvcom_cmd.gather:Gather',
            'prepare = fvcom_cmd.prepare:Prepare',
            'run = fvcom_cmd.run:Run',
        ],
    },
)
