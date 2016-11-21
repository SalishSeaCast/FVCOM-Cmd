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
try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch

import cliff.app
import pytest

import nemo_cmd.combine


@pytest.fixture(scope='module')
def combine_cmd():
    import nemo_cmd.combine
    return nemo_cmd.combine.Combine(Mock(spec=cliff.app.App), [])


class TestGetParser:
    """Unit tests for `salishsea combine` sub-command command-line parser.
    """

    def test_get_parser(self, combine_cmd):
        parser = combine_cmd.get_parser('salishsea combine')
        assert parser.prog == 'salishsea combine'


@patch('nemo_cmd.combine.os.path.lexists')
class TestFindRebuildNemoScript:
    @pytest.mark.parametrize('nemo_path, expected', [
        ('NEMO-code', 'NEMO-code/NEMOGCM/TOOLS/REBUILD_NEMO/rebuild_nemo'),
    ])
    @patch('nemo_cmd.combine.os.path.abspath')
    def test_find_rebuild_nemo_script_found(
            self,
            mock_abspath,
            mock_lexists,
            nemo_path,
            expected,
    ):
        """_find_rebuild_nemo_exec returns script name if executable exists
        """
        run_desc = {'paths': {'NEMO-code': 'NEMO-code'}}
        mock_lexists.return_value = True
        mock_abspath.return_value = nemo_path
        script = nemo_cmd.combine._find_rebuild_nemo_script(run_desc)
        assert script == 'NEMO-code/NEMOGCM/TOOLS/REBUILD_NEMO/rebuild_nemo'

    @patch('nemo_cmd.combine.log.error')
    def test_find_rebuild_nemo_script_not_found(self, mock_log, mock_lexists):
        """_find_rebuild_nemo_exec logs error if executable not found
        """
        run_desc = {'paths': {'NEMO-code': 'NEMO-code'}}
        mock_lexists.return_value = False
        with pytest.raises(SystemExit):
            nemo_cmd.combine._find_rebuild_nemo_script(run_desc)
        assert mock_log.called


class TestGetResultsFiles:
    @patch('nemo_cmd.combine.glob.glob')
    def test_get_results_files(self, mock_glob):
        """_get_results_files returns list of name-roots and count of files
        """
        mock_glob.side_effect = (
            ['foo_0000.nc', 'bar_0000.nc'],
            ['foo_0000.nc', 'foo_0001.nc', 'foo_0002.nc'])
        args = Mock(delete_restart=False)
        name_roots = nemo_cmd.combine._get_results_files(args)
        assert name_roots == ['foo', 'bar']

    @patch('nemo_cmd.combine.log.info')
    def test_get_results_files_none_found(self, mock_log):
        """_get_results_files logs info message if no results files exists
        """
        args = Mock(delete_restart=False)
        nemo_cmd.combine._get_results_files(args)
        assert mock_log.called

    @patch('nemo_cmd.combine.glob.glob')
    @patch('nemo_cmd.combine.os.remove')
    def test_get_results_files_delete_restart(self, mock_rm, mock_glob):
        """_get_results_files deletes restart files
        """
        mock_glob.side_effect = (
            ['baz_restart_0000.nc', 'baz_restart_0001.nc'],
            ['foo_0000.nc', 'bar_0000.nc'],
            ['foo_0000.nc', 'foo_0001.nc', 'foo_0002.nc'])
        args = Mock(delete_restart=True)
        nemo_cmd.combine._get_results_files(args)
        assert mock_rm.call_count == 2


class TestCombineResultsFiles:
    @patch('nemo_cmd.combine.glob.glob')
    @patch('nemo_cmd.combine.subprocess.check_output')
    def test_combine_results_files(self, mock_chk_out, mock_glob):
        """_combine_results_files calls subprocess.check_output for each name-root
        """
        mock_glob.side_effect = (
            ['foo_0000.nc', 'foo_0001.nc', 'foo_0002.nc'],
            ['bar_0000.nc', 'bar_0001.nc', 'bar_0002.nc'],)
        nemo_cmd.combine._combine_results_files('rebuild_nemo',
                                                ['foo', 'bar'], 3)
        assert mock_chk_out.call_count == 2


class TestMoveResults:
    @patch('nemo_cmd.combine.shutil.move')
    def test_move_results_pwd(self, mock_move):
        """_move_results does nothing if results_dir is pwd
        """
        nemo_cmd.combine._move_results(['foo'], './')
        assert not mock_move.called

    @patch('nemo_cmd.combine.shutil.move')
    @patch('nemo_cmd.combine.os.makedirs')
    def test_move_results_makedirs(self, mock_makedirs, mock_move):
        """_move_results creates results_dir if it doesn't exist
        """
        nemo_cmd.combine._move_results(['foo', 'bar'], 'baz')
        assert mock_makedirs.called

    @patch('nemo_cmd.combine.os.makedirs')
    @patch('nemo_cmd.combine.shutil.move')
    def test_move_results_renames(self, mock_move, mock_makedirs):
        """_move_results calls shutil.move for each results file
        """
        nemo_cmd.combine._move_results(['foo', 'bar'], 'baz')
        assert mock_move.call_count == 2


class TestResultsFiles:
    def test_result_files(self):
        """_results_files generator yields name-root with .nc appended
        """
        fn = next(nemo_cmd.combine._results_files(['foo', 'bar']))
        assert fn == 'foo.nc'


class TestCompressResults:
    @patch('nemo_cmd.combine._results_files')
    def test_compress_results_no_compress(self, mock_res_files):
        """_compress_results does nothing when args.compress is False
        """
        args = Mock(compress=False)
        nemo_cmd.combine._compress_results(['foo', 'bar'], args)
        assert not mock_res_files.called
