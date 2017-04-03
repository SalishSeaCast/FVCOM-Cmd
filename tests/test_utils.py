# Copyright 2013-2017 The Salish Sea MEOPAR Contributors
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
"""Unit tests for utils module.
"""
try:
    from pathlib import Path
except ImportError:
    # Python 2.7
    from pathlib2 import Path
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

import pytest

from nemo_cmd import utils


@patch('nemo_cmd.utils.logger')
@patch('nemo_cmd.prepare.remove_run_dir')
class TestGetRunDescValue:
    """Unit tests for get_run_desc_value function.
    """

    def test_non_fatal_key_error(self, m_rm_run_dir, m_logger):
        run_desc = {}
        with pytest.raises(KeyError):
            utils.get_run_desc_value(run_desc, ('foo',), fatal=False)
        assert not m_logger.error.called
        assert not m_rm_run_dir.called

    def test_fatal_key_error_no_run_dir(self, m_rm_run_dir, m_logger):
        run_desc = {}
        with pytest.raises(SystemExit):
            utils.get_run_desc_value(run_desc, ('foo',))
        assert m_logger.error.called_once_with(
            '"foo" key not found - please check your run description YAML file'
        )
        assert not m_rm_run_dir.called

    def test_fatal_key_error_remove_run_dir(self, m_rm_run_dir, m_logger):
        run_desc = {}
        with pytest.raises(SystemExit):
            utils.get_run_desc_value(run_desc, ('foo',), run_dir='run_dir')
        m_logger.error.assert_called_once_with(
            '"foo" key not found - please check your run description YAML file'
        )
        m_rm_run_dir.assert_called_once_with('run_dir')

    def test_value(self, m_rm_run_dir, m_logger):
        run_desc = {'foo': 'bar'}
        value = utils.get_run_desc_value(run_desc, ('foo',))
        assert value == 'bar'

    @patch('nemo_cmd.utils.expanded_path')
    def test_expand_path(self, m_expanded_path, m_rm_run_dir, m_logger):
        run_desc = {'foo': 'bar'}
        value = utils.get_run_desc_value(run_desc, ('foo',), expand_path=True)
        assert value == m_expanded_path('bar')

    @patch('nemo_cmd.utils.resolved_path')
    def test_resolve_path(self, m_resolved_path, m_rm_run_dir, m_logger):
        run_desc = {'foo': 'bar'}
        value = utils.get_run_desc_value(run_desc, ('foo',), resolve_path=True)
        assert value == m_resolved_path('bar')

    @patch('nemo_cmd.utils.resolved_path')
    def test_resolved_path_does_not_exist(
        self, m_resolved_path, m_rm_run_dir, m_logger
    ):
        m_resolved_path().exists.return_value = False
        run_desc = {'foo': 'bar'}
        with pytest.raises(SystemExit):
            utils.get_run_desc_value(run_desc, ('foo',), resolve_path=True)
