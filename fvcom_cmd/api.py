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
"""FVCOM command processor API

Application programming interface for the FVCOM command processor.
Provides Python function interfaces to command processor sub-commands
for use in other sub-command processor modules,
and by other software.
"""
import datetime
import logging
import os
try:
    from pathlib import Path
except ImportError:
    # Python 2.7
    from pathlib2 import Path
import subprocess

import cliff.commandmanager
import yaml

from fvcom_cmd import deflate as deflate_plugin
from fvcom_cmd import gather as gather_plugin
from fvcom_cmd import prepare as prepare_plugin

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(name)s %(levelname)s: %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)


def deflate(filepaths, max_concurrent_jobs):
    """Deflate variables in each of the netCDF files in filepaths using
    Lempel-Ziv compression.

    Converts files to netCDF-4 format.
    The deflated file replaces the original file.

    :param sequence filepaths: Paths/names of files to be deflated.

    :param int max_concurrent_jobs: Maximum number of concurrent deflation
                                    processes allowed.
    """
    try:
        return deflate_plugin.deflate(filepaths, max_concurrent_jobs)
    except AttributeError:
        # filepaths is sequence of path strings not Path objects
        return deflate_plugin.deflate(
            map(Path, filepaths), max_concurrent_jobs
        )


def gather(results_dir):
    """Move all of the files and directories from the present working directory
    into results_dir.

    If results_dir doesn't exist, create it.

    Delete any symbolic links so that the present working directory is empty.

    :param results_dir: Path of the directory into which to store the run
                        results.
    :type results_dir: :py:class:`pathlib.Path`
    """
    return gather_plugin.gather(results_dir)


def prepare(run_desc_file, nocheck_init=False):
    """Prepare a FVCOM run.

    A UUID named temporary run directory is created and symbolic links
    are created in the directory to the files and directories specifed
    to run FVCOM.
    The output of :command:`hg parents` is recorded in the directory
    for the FVCOM-code and FVCOM-forcing repos that the symlinks point to.
    The path to the run directory is returned.

    :param run_desc_file: File path/name of the YAML run description file.
    :type run_desc_file: :py:class:`pathlib.Path`

    :arg boolean fvcom34: Prepare a FVCOM-3.4 run;
                         the default is to prepare a FVCOM-3.6 run

    :arg nocheck_init: Suppress initial condition link check the
                       default is to check
    :type nocheck_init: boolean

    :returns: Path of the temporary run directory
    :rtype: :py:class:`pathlib.Path`
    """
    return prepare_plugin.prepare(run_desc_file, nocheck_init)


def run_in_subprocess(run_id, run_desc, results_dir):
    """Execute `fvcom run` in a subprocess.

    :arg str run_id: Job identifier that appears in the :command:`qstat`
                     listing.
                     A temporary run description YAML file is created
                     with the name :file:`{run_id}_subprocess_run.yaml`.

    :arg dict run_desc: Run description data structure that will be
                        written to the temporary YAML file.

    :arg boolean fvcom34: Execute a FVCOM-3.4 run;
                         the default is to execute a FVCOM-3.6 run

    :arg results_dir: Directory to store results into.
    :type results_dir: str
    """
    yaml_file = '{}_subprocess_run.yaml'.format(run_id)
    with open(yaml_file, 'wt') as f:
        yaml.dump(run_desc, f, default_flow_style=False)
    cmd = ['salishsea', 'run']
    cmd.extend([yaml_file, results_dir])
    try:
        output = subprocess.check_output(
            cmd, stderr=subprocess.STDOUT, universal_newlines=True
        )
        for line in output.splitlines():
            if line:
                log.info(line)
    except subprocess.CalledProcessError as e:
        log.error(
            'subprocess {cmd} failed with return code {status}'.
            format(cmd=cmd, status=e.returncode)
        )
        for line in e.output.splitlines():
            if line:
                log.error(line)
    os.unlink(yaml_file)


def _run_subcommand(app, app_args, argv):
    """Run a sub-command with argv as arguments via its plug-in
    interface.

    Based on :py:meth:`cliff.app.run_subcommand`.

    :arg app: Application instance invoking the command.
    :type app: :py:class:`cliff.app.App`

    :arg app_args: Application arguments.
    :type app_args: :py:class:`argparse.Namespace`

    :arg argv: Sub-command arguments.
    :type argv: list
    """
    command_manager = cliff.commandmanager.CommandManager(
        'salishsea.app', convert_underscores=False
    )
    try:
        subcommand = command_manager.find_command(argv)
    except ValueError as err:
        if app_args.debug:
            raise
        else:
            log.error(err)
        return 2
    cmd_factory, cmd_name, sub_argv = subcommand
    cmd = cmd_factory(app, app_args)
    try:
        cmd_parser = cmd.get_parser(cmd_name)
        parsed_args = cmd_parser.parse_args(sub_argv)
        result = cmd.take_action(parsed_args)
    except Exception as err:
        result = 1
        if app_args.debug:
            log.exception(err)
        else:
            log.error(err)
    return result
