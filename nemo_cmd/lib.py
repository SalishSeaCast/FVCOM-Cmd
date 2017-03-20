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
"""Utility functions for use by NEMO-Cmd sub-command plug-ins.
"""
import yaml

from nemo_cmd import fspath


def load_run_desc(desc_file):
    """Load the run description file contents into a data structure.

    :arg desc_file: File path/name of YAML run description file.
    :type desc_file: str

    :returns: Contents of run description file parsed from YAML into a dict.
    :rtype: dict
    """
    with open(fspath(desc_file), 'rt') as f:
        run_desc = yaml.load(f)
    return run_desc


def get_n_processors(run_desc):
    """Return the total number of processors required for the run as
    specified by the MPI decomposition key in the run description.

    :arg run_desc: Run description dictionary.
    :type run_desc: dict

    :returns: Number of processors required for the run.
    :rtype: int
    """
    jpni, jpnj = map(int, run_desc['MPI decomposition'].split('x'))
    return jpni * jpnj
