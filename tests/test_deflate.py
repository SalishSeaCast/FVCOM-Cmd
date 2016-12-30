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
"""SalishSeaCmd deflate sub-command plug-in unit tests
"""
import subprocess

try:
    from types import SimpleNamespace
except ImportError:
    # Python 2.7
    class SimpleNamespace:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)


try:
    from unittest.mock import call, Mock, patch
except ImportError:
    # Python 2.7
    from mock import call, Mock, patch

import cliff.app
import pytest

import nemo_cmd.deflate


@pytest.fixture
def deflate_cmd():
    return nemo_cmd.deflate.Deflate(Mock(spec=cliff.app.App), [])


class TestGetParser:
    """Unit tests for `nemo deflate` sub-command command-line parser.
    """

    def test_get_parser(self, deflate_cmd):
        parser = deflate_cmd.get_parser('nemo deflate')
        assert parser.prog == 'nemo deflate'

    def test_parsed_args_defaults(self, deflate_cmd):
        parser = deflate_cmd.get_parser('nemo deflate')
        parsed_args = parser.parse_args(['foo.nc', 'bar.nc'])
        assert parsed_args.filepaths == ['foo.nc', 'bar.nc']


class TestTakeAction:
    """Unit test for `nemo deflate` sub-command take_action() method.
    """

    @patch('nemo_cmd.deflate.deflate')
    def test_take_action(self, m_deflate, deflate_cmd):
        parsed_args = SimpleNamespace(filepaths=['foo.nc', 'bar.nc'])
        deflate_cmd.take_action(parsed_args)
        m_deflate.assert_called_once_with(['foo.nc', 'bar.nc'])


@patch('nemo_cmd.deflate.logger')
class TestDeflate:
    """Unit tests for deflate function.
    """

    def test_error(self, m_logger):
        with patch('nemo_cmd.deflate._netcdf4_deflate', return_value='error'):
            nemo_cmd.deflate.deflate(['foo.nc', 'bar.nc'])
        m_logger.error.assert_has_calls([call('error')] * 2)

    def test_success(self, m_logger):
        with patch('nemo_cmd.deflate._netcdf4_deflate', return_value=''):
            nemo_cmd.deflate.deflate(['foo.nc', 'bar.nc'])
        m_logger.info.assert_has_calls([
            call('netCDF4 deflated foo.nc'),
            call('netCDF4 deflated bar.nc'),
        ])


@patch('nemo_cmd.deflate.subprocess.check_output')
class TestNetcdf4Deflate:
    """Unit tests for _netcdf4_deflate function.
    """

    def test_subprocess_check_output(self, m_check_output):
        result = nemo_cmd.deflate._netcdf4_deflate('foo.nc')
        m_check_output.assert_called_once_with(
            ['ncks', '-4', '-L4', '-O', 'foo.nc', 'foo.nc'],
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        assert result == m_check_output()
