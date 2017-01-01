# Copyright 2013-2016 The Salish Sea MEOPAR Contributors
# and The University of British Columbia

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""NEMO-Cmd command plug-in for deflate sub-command.

Deflate variables in netCDF files using Lempel-Ziv compression.
"""
import logging
import shlex

import cliff.command
import subprocess

logger = logging.getLogger(__name__)


class Deflate(cliff.command.Command):
    """Deflate variables in netCDF files using Lempel-Ziv compression.
    """

    def get_parser(self, prog_name):
        parser = super(Deflate, self).get_parser(prog_name)
        parser.description = '''
            Deflate variables in netCDF files using Lempel-Ziv compression.
            Converts files to netCDF-4 format.
            The deflated file replaces the original file.
            This command is effectively the same as running
            ncks -4 -L -O FILEPATH FILEPATH
            for each FILEPATH.
        '''
        parser.add_argument(
            'filepaths',
            nargs='+',
            metavar='FILEPATH',
            help='Path/name of file to be deflated.'
        )
        return parser

    def take_action(self, parsed_args):
        """Execute the :command:`nemo deflate` sub-command.

        Deflate variables in netCDF files using Lempel-Ziv compression.
        Converts files to netCDF-4 format.
        The deflated file replaces the original file.
        This command is effectively the same as
        :command:`ncks -4 -L -O filename filename`.
        """
        deflate(parsed_args.filepaths)


def deflate(filepaths):
    """Deflate variables in each of the netCDF files in filenames using
    Lempel-Ziv compression.

    Converts files to netCDF-4 format.
    The deflated file replaces the original file.

    :param sequence filepaths: Paths/names of files to be deflated.
    """
    for fp in filepaths:
        result = _netcdf4_deflate(fp)
        logger.error(result) if result else logger.info(
            'netCDF4 deflated {fp}'.format(fp=fp)
        )


def _netcdf4_deflate(filename, dfl_lvl=4):
    """Run `ncks -4 -L dfl_lvl` on filename *in place*.

    The result is a netCDF-4 format file with its variables compressed
    with Lempel-Ziv deflation.

    :arg filename: Path/filename of the netCDF file to process.
    :type filename: string

    :arg dfl_lvl: Lempel-Ziv deflation level to use.
    :type dfl_lvl: int

    :returns: Output of the ncks command.
    :rtype: string
    """
    cmd = 'ncks -4 -L{dfl_lvl} -O {filename} {filename}'.format(
        dfl_lvl=dfl_lvl, filename=filename
    )
    result = subprocess.check_output(
        shlex.split(cmd), stderr=subprocess.STDOUT, universal_newlines=True
    )
    return result
