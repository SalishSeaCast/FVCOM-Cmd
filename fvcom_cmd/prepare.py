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
"""FVCOM-Cmd command plug-in for prepare sub-command.

Sets up the necessary symbolic links for a FVCOM run
in a specified directory and changes the pwd to that directory.
"""
from copy import copy
import functools
import logging
import os
try:
    from pathlib import Path
except ImportError:
    # Python 2.7
    from pathlib2 import Path
import shutil
import time
from datetime import datetime
import xml.etree.ElementTree

import arrow
import cliff.command
from dateutil import tz
import hglib

from fvcom_cmd import lib, fspath, resolved_path, expanded_path

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class Prepare(cliff.command.Command):
    """Prepare a FVCOM run
    """

    def get_parser(self, prog_name):
        parser = super(Prepare, self).get_parser(prog_name)
        parser.description = '''
            Set up the FVCOM run described in DESC_FILE
            and print the path to the run directory.
        '''
        parser.add_argument(
            'desc_file',
            metavar='DESC_FILE',
            type=Path,
            help='run description YAML file'
        )
        parser.add_argument(
            '--nocheck-initial-conditions',
            dest='nocheck_init',
            action='store_true',
            help='''
            Suppress checking of the initial conditions link.
            Useful if you are submitting a job to an HPC qsub queue and want
            the submitted job to wait for completion of a previous job.
            '''
        )
        parser.add_argument(
            '-q',
            '--quiet',
            action='store_true',
            help="don't show the run directory path on completion"
        )
        return parser

    def take_action(self, parsed_args):
        """Execute the `fvcom prepare` sub-command.

        A UUID named directory is created and symbolic links are created
        in the directory to the files and directories specified to run FVCOM.
        The path to the run directory is logged to the console on completion
        of the set-up.
        """
        run_dir = prepare(
            parsed_args.desc_file, parsed_args.nocheck_init
        )
        if not parsed_args.quiet:
            logger.info('Created run directory {}'.format(run_dir))
        return run_dir


def prepare(desc_file, nocheck_init):
    """Create and prepare the temporary run directory.

    The temporary run directory is created with a UUID as its name.
    Symbolic links are created in the directory to the files and
    directories specified to run FVCOM.
    The path to the run directory is returned.

    :param desc_file: File path/name of the YAML run description file.
    :type desc_file: :py:class:`pathlib.Path`

    :param boolean fvcom34: Prepare a FVCOM-3.4 run;
                           the default is to prepare a FVCOM-3.6 run

    :param boolean nocheck_init: Suppress initial condition link check;
                                 the default is to check

    :returns: Path of the temporary run directory
    :rtype: :py:class:`pathlib.Path`
    """
    run_desc = lib.load_run_desc(desc_file)
    fvcom_exec = _get_fvcom_exec(run_desc)
    run_set_dir = resolved_path(desc_file).parent
    run_dir = _make_run_dir(run_desc)
    _make_namelists(run_set_dir, run_desc, run_dir)
    _make_executable_links(fvcom_exec, run_dir)
    _make_input_links(run_desc, run_dir)
    #_make_forcing_links(run_desc, run_dir, nocheck_init)
    #_make_restart_links(run_desc, run_dir, nocheck_init)
    _record_vcs_revisions(run_desc, run_dir)
    return run_dir

def _get_fvcom_exec(run_desc):
    """
    Find absolute path of the FVCOM executable.
    """
    fvcom_path = lib.get_run_desc_value(
            run_desc, ('paths', 'FVCOM'),
            resolve_path=True,
            fatal=False
        )
    if fvcom_path.is_dir():
        fvcom_exec = fvcom_path / 'FVCOM_source' / 'fvcom'
    else:
        fvcom_exec = fvcom_path

    if not fvcom_exec.exists():
        logger.error(
            '{} not found - did you forget to build it?'.format(fvcom_exec)
        )
        raise SystemExit(2)
    return fvcom_exec


def _make_run_dir(run_desc):
    """Create the directory from which FVCOM will be run.

    The location is the directory comes from the run description,
    and its name is a hostname- and time-based UUID.

    :param dict run_desc: Run description dictionary.

    :returns: Path of the temporary run directory
    :rtype: :py:class:`pathlib.Path`
    """
    runs_dir = lib.get_run_desc_value(
        run_desc, ('paths', 'runs directory'), resolve_path=True
    )
    run_dir = runs_dir / datetime.utcnow().strftime('%Y%m%d-%Hh%Mm%S.%fs')
    run_dir.mkdir()
    (run_dir / 'output').mkdir()
    return run_dir


def _remove_run_dir(run_dir):
    """Remove all files from run_dir, then remove run_dir.

    Intended to be used as a clean-up operation when some other part
    of the prepare process fails.

    :param run_dir: Path of the temporary run directory.
    :type run_dir: :py:class:`pathlib.Path`
    """
    # Allow time for the OS to flush file buffers to disk
    time.sleep(0.1)
    try:
        for p in run_dir.iterdir():
            p.unlink()
        run_dir.rmdir()
    except OSError:
        pass


def _make_namelists(run_set_dir, run_desc, run_dir):
    """
    Puts the namelist in the right place
    """
    case_name = run_desc['casename']

    keys = ('namelist',)
    namelist = lib.get_run_desc_value(run_desc, keys, run_dir=run_dir)
    namelist_dest = run_dir / Path(case_name + '_run.nml')
    with (namelist_dest).open('wt') as fout:
        nl_path = expanded_path(namelist)
        if not nl_path.is_absolute():
            nl_path = run_set_dir / nl_path
        try:
            with nl_path.open('rt') as f:
                fout.writelines(f.readlines())
                fout.write(u'\n\n')
        except IOError as e:
            logger.error(e)
            _remove_run_dir(run_dir)
            raise SystemExit(2)


def _make_executable_links(fvcom_exec, run_dir):
    """Create symlinks in run_dir to the FVCOM and I/O server executables
    and record the code repository revision(s) used for the run.

    :param fvcom_bin_dir: Absolute path of directory containing FVCOM executable.
    :type fvcom_bin_dir: :py:class:`pathlib.Path`

    :param run_dir: Path of the temporary run directory.
    :type run_dir: :py:class:`pathlib.Path`

    """
    (run_dir / 'fvcom').symlink_to(fvcom_exec)

def _make_input_links(run_desc, run_dir):
    """Create symlinks in run_dir to the file names that FVCOM expects
    to the bathymetry and coordinates files given in the run_desc dict.

    For AGRIF sub-grids, the symlink names are prefixed with the agrif_n;
    e.g. 1_coordinates.nc.

    :param dict run_desc: Run description dictionary.

    :param run_dir: Path of the temporary run directory.
    :type run_dir: :py:class:`pathlib.Path`

    :param int agrif_n: AGRIF sub-grid number.

    :raises: SystemExit
    """

    ##TODO: Refactor this into a public function that can be used by prepare
    ## plug-ins in packages like SalishSeaCmd that extend FVCOM-Cmd

    input_path = lib.get_run_desc_value(
        run_desc, ('paths', 'input'), resolve_path=True, run_dir=run_dir
    )

    (run_dir / 'input').symlink_to(input_path)



def _make_restart_links(run_desc, run_dir, nocheck_init, agrif_n=None):
    """For a FVCOM-3.6 run, create symlinks in run_dir to the restart
    files given in the run description restart section.

    :param dict run_desc: Run description dictionary.

    :param run_dir: Path of the temporary run directory.
    :type run_dir: :py:class:`pathlib.Path`

    :param boolean nocheck_init: Suppress restart file existence check;
                                 the default is to check

    :param int agrif_n: AGRIF sub-grid number.

    :raises: :py:exc:`SystemExit` if a symlink target does not exist
    """

    ##TODO: Refactor this into a public function that can be used by prepare
    ## plug-ins in packages like SalishSeaCmd that extend FVCOM-Cmd

    keys = ('restart',)
    if agrif_n is not None:
        keys = ('restart', 'AGRIF_{agrif_n}'.format(agrif_n=agrif_n))
    try:
        link_names = lib.get_run_desc_value(
            run_desc, keys, run_dir=run_dir, fatal=False
        )
    except KeyError:
        logger.warning(
            'No restart section found in run description YAML file, '
            'so proceeding on the assumption that initial conditions '
            'have been provided'
        )
        return
    for link_name in link_names:
        if link_name.startswith('AGRIF'):
            continue
        keys = ('restart', link_name)
        if agrif_n is not None:
            keys = (
                'restart', 'AGRIF_{agrif_n}'.format(agrif_n=agrif_n), link_name
            )
            link_name = '{agrif_n}_{link_name}'.format(
                agrif_n=agrif_n, link_name=link_name
            )
        source = lib.get_run_desc_value(run_desc, keys, expand_path=True)
        if not source.exists() and not nocheck_init:
            logger.error(
                '{} not found; cannot create symlink - '
                'please check the restart file paths and file names '
                'in your run description file'.format(source)
            )
            _remove_run_dir(run_dir)
            raise SystemExit(2)
        if nocheck_init:
            (run_dir / link_name).symlink_to(source)
        else:
            (run_dir / link_name).symlink_to(source.resolve())


def _record_vcs_revisions(run_desc, run_dir):
    """Record revision and status information from version control system
    repositories in files in the temporary run directory.

    :param dict run_desc: Run description dictionary.

    :param run_dir: Path of the temporary run directory.
    :type run_dir: :py:class:`pathlib.Path`
    """
    if 'vcs revisions' not in run_desc:
        return
    vcs_funcs = {'hg': get_hg_revision}
    vcs_tools = lib.get_run_desc_value(
        run_desc, ('vcs revisions',), run_dir=run_dir
    )
    for vcs_tool in vcs_tools:
        repos = lib.get_run_desc_value(
            run_desc, ('vcs revisions', vcs_tool), run_dir=run_dir
        )
        for repo in repos:
            write_repo_rev_file(Path(repo), run_dir, vcs_funcs[vcs_tool])


def write_repo_rev_file(repo, run_dir, vcs_func):
    """Write revision and status information from a version control
    system repository to a file in the temporary run directory.

    The file name is the repository directory name with :kbd:`_rev.txt`
    appended.

    :param repo: Path of Mercurial repository to get revision and status
                 information from.
    :type repo: :py:class:`pathlib.Path`

    :param run_dir: Path of the temporary run directory.
    :type run_dir: :py:class:`pathlib.Path`

    :param vcs_func: Function to call to gather revision and status
                     information from repo.
    """
    repo_path = resolved_path(repo)
    repo_rev_file_lines = vcs_func(repo_path, run_dir)
    if repo_rev_file_lines:
        rev_file = run_dir / '{repo.name}_rev.txt'.format(repo=repo_path)
        with rev_file.open('wt') as f:
            f.writelines(u'{}\n'.format(line) for line in repo_rev_file_lines)


def get_hg_revision(repo, run_dir):
    """Gather revision and status information from Mercurial repo.

    Effectively record the output of :command:`hg parents -v` and
    :param run_dir:
    :command:`hg status -mardC`.

    Files named :file:`CONFIG/cfg.txt` and
    :file:`TOOLS/COMPILE/full_key_list.txt` are ignored because they change
    frequently but the changes generally of no consequence;
    see https://bitbucket.org/salishsea/fvcom-cmd/issues/18.

    :param repo: Path of Mercurial repository to get revision and status
                 information from.
    :type repo: :py:class:`pathlib.Path`

    :param run_dir: Path of the temporary run directory.
    :type run_dir: :py:class:`pathlib.Path`

    :returns: Mercurial repository revision and status information strings.
    :rtype: list
    """
    if not repo.exists():
        logger.warning(
            'revision and status requested for non-existent repo: {repo}'
            .format(repo=repo)
        )
        return []
    repo_path = copy(repo)
    while str(repo) != repo_path.root:
        try:
            with hglib.open(fspath(repo)) as hg:
                parents = hg.parents()
                files = [f[1] for f in hg.status(change=[parents[0].rev])]
                status = hg.status(
                    modified=True,
                    added=True,
                    removed=True,
                    deleted=True,
                    copies=True
                )
            break
        except hglib.error.ServerError:
            repo = repo.parent
    else:
        logger.error(
            'unable to find Mercurial repo root in or above '
            '{repo_path}'.format(repo_path=repo_path)
        )
        _remove_run_dir(run_dir)
        raise SystemExit(2)
    revision = parents[0]
    repo_rev_file_lines = [
        'changset:   {rev}:{node}'.format(
            rev=revision.rev.decode(), node=revision.node.decode()
        )
    ]
    if revision.tags:
        repo_rev_file_lines.append(
            'tag:        {tags}'.format(tags=revision.tags.decode())
        )
    if len(parents) > 1:
        repo_rev_file_lines.extend(
            'parent:     {rev}:{node}'.format(
                rev=parent.rev.decode(), node=parent.node.decode()
            ) for parent in parents
        )
    date = arrow.get(revision.date).replace(tzinfo=tz.tzlocal())
    repo_rev_file_lines.extend([
        'user:       {}'.format(revision.author.decode()),
        'date:       {}'.format(date.format('ddd MMM DD HH:mm:ss YYYY ZZ')),
        'files:      {}'.format(' '.join(f.decode() for f in files)),
        'description:',
    ])
    repo_rev_file_lines.extend(
        line.decode() for line in revision.desc.splitlines()
    )
    ignore = (u'CONFIG/cfg.txt', u'TOOLS/COMPILE/full_key_list.txt')
    for s in copy(status):
        if s[1].decode().endswith(ignore):
            status.remove(s)
    if status:
        logger.warning(
            'There are uncommitted changes in {}'.format(resolved_path(repo))
        )
        repo_rev_file_lines.append('uncommitted changes:')
        repo_rev_file_lines.extend(
            '{code} {path}'.format(code=s[0].decode(), path=s[1].decode())
            for s in status
        )
    return repo_rev_file_lines
