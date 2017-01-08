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
"""SalishSeaCmd combine sub-command plug-in unit tests
"""
import shlex
from pathlib import Path

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

import nemo_cmd.combine


@pytest.fixture(scope='module')
def combine_cmd():
    import nemo_cmd.combine
    return nemo_cmd.combine.Combine(Mock(spec=cliff.app.App), [])


class TestParser:
    """Unit tests for `nemo combine` sub-command command-line parser.
    """

    def test_get_parser(self, combine_cmd):
        parser = combine_cmd.get_parser('nemo combine')
        assert parser.prog == 'nemo combine'

    def test_parsed_args(self, combine_cmd):
        parser = combine_cmd.get_parser('nemo combine')
        parsed_args = parser.parse_args(['nemo.yaml'])
        assert parsed_args.run_desc_file == Path('nemo.yaml')


class TestTakeAction:
    """Unit test for `nemo combine` sub-command take_action() method.
    """

    @patch('nemo_cmd.combine.combine')
    def test_take_action(self, m_combine, combine_cmd):
        parsed_args = SimpleNamespace(run_desc_file=Path('nemo.yaml'))
        combine_cmd.take_action(parsed_args)
        m_combine.assert_called_once_with(Path('nemo.yaml'))


@patch('nemo_cmd.combine.Path')
@patch('nemo_cmd.combine.logger')
class TestGetResultsFiles:
    def test_get_results_files(self, m_logger, m_path):
        m_path.cwd().glob.return_value = ['foo_0000.nc', 'bar_0000.nc']
        name_roots = nemo_cmd.combine._get_results_files()
        assert name_roots == ['foo', 'bar']

    def test_get_results_files_none_found(self, m_logger, m_path):
        nemo_cmd.combine._get_results_files()
        assert m_logger.info.called


@patch('nemo_cmd.combine.logger')
class TestFindRebuildNemoScript:
    """Unit tests for _find_rebuild_nemo_script function.
    """

    @pytest.mark.parametrize(
        'nemo_code_config', [
            'NEMO-3.6-code/NEMOGCM/CONFIG/',
            'NEMO-3.6/CONFIG/',
        ]
    )
    def test_find_rebuild_nemo_script(
        self, m_logger, nemo_code_config, tmpdir
    ):
        nemo_code_config = tmpdir.ensure_dir(nemo_code_config)
        nemo_code_config.ensure('../TOOLS/REBUILD_NEMO/rebuild_nemo.exe')
        script_path = nemo_code_config.ensure(
            '../TOOLS/REBUILD_NEMO/rebuild_nemo'
        )
        run_desc = {'paths': {'NEMO code config': str(nemo_code_config)}}
        rebuild_nemo_script = nemo_cmd.combine._find_rebuild_nemo_script(
            run_desc
        )
        assert rebuild_nemo_script == Path(str(script_path))

    @pytest.mark.parametrize(
        'nemo_code_config', [
            'NEMO-3.6-code/NEMOGCM/CONFIG/',
            'NEMO-3.6/CONFIG/',
        ]
    )
    def test_no_rebuild_nemo_script(self, m_logger, nemo_code_config, tmpdir):
        nemo_code_config = tmpdir.ensure_dir(nemo_code_config)
        run_desc = {'paths': {'NEMO code config': str(nemo_code_config)}}
        with pytest.raises(SystemExit):
            nemo_cmd.combine._find_rebuild_nemo_script(run_desc)
        assert m_logger.error.called


@patch('nemo_cmd.combine.logger')
@patch('nemo_cmd.combine.Path')
class TestCombineResultsFiles:
    """Unit tests for _combine_results_files function.
    """

    @patch('nemo_cmd.combine.shutil.move')
    def test_single_processor_result(self, m_move, m_path, m_logger):
        m_path.cwd().glob.return_value = ['foo_0000.nc']
        nemo_cmd.combine._combine_results_files('rebuild_nemo', ['foo'])
        assert m_move.call_args == call('foo_0000.nc', 'foo.nc')

    @patch('nemo_cmd.combine.subprocess.check_output')
    @patch('nemo_cmd.combine.os.unlink')
    def test_rebuild_nemo_subprocess(
        self, m_unlink, m_check_output, m_path, m_logger
    ):
        m_path.cwd().glob.return_value = ['foo_0000.nc', 'foo_0001.nc']
        nemo_cmd.combine._combine_results_files('rebuild_nemo', ['foo'])
        assert m_check_output.call_args == call(
            shlex.split('rebuild_nemo foo 2'),
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )


@patch('nemo_cmd.combine.Path')
class TestDeleteResultsFiles:
    """Unit tests for _delete_results_files function.
    """

    def test_delete_results_files(self, m_path):
        m_path.cwd().glob.return_value = [Mock(spec=Path)]
        nemo_cmd.combine._delete_results_files(['foo'])
        assert m_path.cwd().glob()[0].unlink.called
