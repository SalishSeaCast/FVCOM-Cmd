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
"""FVCOM-Cmd command plug-in for run sub-command.

Prepare for, execute, and gather the results of a run of the FVCOM model.
"""
from __future__ import division

import datetime
import logging
import math
import os
try:
    from pathlib import Path
except ImportError:
    # Python 2.7
    from pathlib2 import Path
import subprocess

import cliff.command

from fvcom_cmd import api, lib
from fvcom_cmd.fspath import fspath
#from fvcom_cmd.prepare import get_run_desc_value

logger = logging.getLogger(__name__)


class Run(cliff.command.Command):
    """Prepare, execute, and gather results from a FVCOM model run.
    """

    def get_parser(self, prog_name):
        parser = super(Run, self).get_parser(prog_name)
        parser.description = '''
            Prepare, execute, and gather the results from a FVCOM
            run described in DESC_FILE.
            The results files from the run are gathered in RESULTS_DIR.

            If RESULTS_DIR does not exist it will be created.
        '''
        parser.add_argument(
            'desc_file',
            metavar='DESC_FILE',
            type=Path,
            help='run description YAML file'
        )
        parser.add_argument(
            'results_dir',
            metavar='RESULTS_DIR',
            help='directory to store results into'
        )
        parser.add_argument(
            '--max-deflate-jobs',
            dest='max_deflate_jobs',
            type=int,
            default=4,
            help='''
            Maximum number of concurrent sub-processes to
            use for netCDF deflating. Defaults to 4.'''
        )
        parser.add_argument(
            '--nocheck-initial-conditions',
            dest='nocheck_init',
            action='store_true',
            help='''
            Suppress checking of the initial conditions link.
            Useful if you are submitting a job to wait on a
            previous job'''
        )
        parser.add_argument(
            '--no-submit',
            dest='no_submit',
            action='store_true',
            help='''
            Prepare the temporary run directory, and the bash script to execute
            the FVCOM run, but don't submit the run to the queue.
            This is useful during development runs when you want to hack on the
            bash script and/or use the same temporary run directory more than
            once.
            '''
        )
        parser.add_argument(
            '--waitjob',
            type=int,
            default=0,
            help='''
            use -W waitjob in call to qsub, to make current job
            wait for on waitjob.  Waitjob is the queue job number
            '''
        )
        parser.add_argument(
            '-q',
            '--quiet',
            action='store_true',
            help="don't show the run directory path or job submission message"
        )
        return parser

    def take_action(self, parsed_args):
        """Execute the `fvcom run` sub-coomand.

        The message generated upon submission of the run to the queue
        manager is logged to the console.

        :param parsed_args: Arguments and options parsed from the command-line.
        :type parsed_args: :class:`argparse.Namespace` instance
        """
        qsub_msg = run(
            parsed_args.desc_file, parsed_args.results_dir,
            parsed_args.max_deflate_jobs,
            parsed_args.nocheck_init, parsed_args.no_submit,
            parsed_args.waitjob, parsed_args.quiet
        )
        if qsub_msg and not parsed_args.quiet:
            logger.info(qsub_msg)


def run(
    desc_file,
    results_dir,
    max_deflate_jobs=4,
    nocheck_init=False,
    no_submit=False,
    waitjob=0,
    quiet=False
):
    """Create and populate a temporary run directory, and a run script,
    and submit the run to the queue manager.

    The temporary run directory is created and populated via the
    :func:`fvcom_cmd.api.prepare` API function.
    The system-specific run script is stored in :file:`FVCOM.sh`
    in the run directory.
    That script is submitted to the queue manager in a subprocess.

    :param desc_file: File path/name of the YAML run description file.
    :type desc_file: :py:class:`pathlib.Path`

    :param str results_dir: Path of the directory in which to store the run
                            results;
                            it will be created if it does not exist.

    :param int max_deflate_jobs: Maximum number of concurrent sub-processes to
                                 use for netCDF deflating.

    :param boolean nocheck_init: Suppress initial condition link check
                                 the default is to check

    :param boolean no_submit: Prepare the temporary run directory,
                              and the bash script to execute the FVCOM run,
                              but don't submit the run to the queue.

    :param int waitjob: Use -W waitjob in call to qsub, to make current job
                        wait for on waitjob.  Waitjob is the queue job number

    :param boolean quiet: Don't show the run directory path message;
                          the default is to show the temporary run directory path.

    :returns: Message generated by queue manager upon submission of the
              run script.
    :rtype: str
    """
    run_dir = api.prepare(desc_file, nocheck_init)
    if not quiet:
        logger.info('Created run directory {}'.format(run_dir))

    # Make results directory
    results_dir = Path(results_dir)
    results_dir.mkdir()

    # Build the batch script
    batch_script = _build_batch_script(fspath(desc_file), results_dir, run_dir)
    batch_file = run_dir / 'FVCOM.sh'
    with batch_file.open('wt') as f:
        f.write(batch_script)

    # Submission
    if no_submit:
        return
    starting_dir = Path.cwd()
    os.chdir(fspath(run_dir))
    if waitjob:
        cmd = 'qsub -W depend=afterok:{} FVCOM.sh'.format(waitjob)
    else:
        cmd = 'jobsub -c gpsc2.science.gc.ca FVCOM.sh'
    qsub_msg = subprocess.check_output(cmd.split(), universal_newlines=True)
    os.chdir(fspath(starting_dir))
    return qsub_msg


def _build_batch_script(desc_file, results_dir, run_dir):
    """Build the Bash script that will execute the run.
    """
    # Common header
    script = (
        u'#!/bin/bash\n\n'
        u'#$ -S /bin/bash\n'
        )

    run_desc = lib.load_run_desc(desc_file)

    if 'run_id' in run_desc:
        script += (
        u'#$ -N {run_id}\n'
        ).format(run_id=run_desc['run_id'])

    if 'email' in run_desc:
        script += (
        u'# email when the job [b]egins and [e]nds, or is [a]borted\n'
        u'#$ -m bea\n'
        u'#$ -M {email}\n'
        ).format(email=run_desc['email'])

    if 'walltime' in run_desc:
        try:
            td = datetime.timedelta(seconds=run_desc['walltime'])
        except TypeError:
            t = datetime.datetime.strptime(
                run_desc['walltime'], '%H:%M:%S'
            ).time()
            td = datetime.timedelta(
                hours=t.hour, minutes=t.minute, seconds=t.second
            )
        walltime = lib.td2hms(td)
        script += (
            u'# job runtime\n'
            u'#$ -l h_rt={walltime}\n'
        ).format(walltime=walltime)

    # stdout/stderr
    script += (
        u'# stdout and stderr file paths/names\n'
        u'#$ -o {results_dir}/stdout\n'
        u'#$ -e {results_dir}/stderr\n'
    ).format(results_dir=results_dir)


    # SGE
    if 'SGE resources' in run_desc:
        script += (
            '# resource(s) requested in run description YAML file\n'
        )
        resources = run_desc['SGE resources']
        for resource in resources:
            if 'res_cpus' in resource:
                _, ppn = resource.rsplit('=', 1)
                nproc = run_desc['nproc']
                nnodes = math.ceil(nproc / int(ppn))
                script += (
                    u'#$ -pe dev {nnodes}\n'.format(nnodes=int(nnodes))
                    )
            script += (
                u'#$ -l {resource}\n'.format(resource=resource)
            )

    script += (
        u'\n'
        u'RUN_ID="{run_id}"\n'
        u'RUN_DESC="{run_desc_file}"\n'
        u'WORK_DIR="{run_dir}"\n'
        u'RESULTS_DIR="{results_dir}"\n'
        u'DEFLATE="{fvcom_cmd} deflate"\n'
        u'GATHER="{fvcom_cmd} gather"\n\n'
    ).format(
    run_id=run_desc['run_id'],
    run_desc_file=desc_file,
    run_dir=run_dir,
    results_dir=results_dir,
    fvcom_cmd=Path('${HOME}/.local/bin/fvc')
    )


    if 'modules to load' in run_desc:
        loadcmd = '. ssmuse-sh -d'
        modules = run_desc['modules to load']
        for module in modules:
            script += (
            u'{loadcmd} {module}\n'.format(loadcmd=loadcmd,module=module)
            )

    # execution part
    script += (
        u'\n'
        u'cd ${WORK_DIR}\n'
        u'echo "Working dir: $(pwd)"\n'
        u'\n'
        u'echo "Starting run at $(date)"\n'
        u'mkdir -p ${RESULTS_DIR}\n'
        u'\n'
    )

    # mpirun
    script += (
        u'time mpirun -np {nproc} ./fvcom --casename={casename} --logfile=fvcom.log\n'
    ).format(nproc=nproc, casename=run_desc['casename'])

    script += (
        u'MPIRUN_EXIT_CODE=$?\n'
        u'echo "Ended run at $(date)"\n'
        u'\n'
        u'echo "Results gathering started at $(date)"\n'
        u'${GATHER} ${RESULTS_DIR} --debug\n'
        u'echo "Results gathering ended at $(date)"\n'
    )

    # Fix permissions
    script += (
        u'chmod go+rx ${RESULTS_DIR}\n'
        u'chmod g+r ${RESULTS_DIR}/*\n'
        u'chmod o+r ${RESULTS_DIR}/*\n'
        u'\n'
    )

    script += (
        u'echo "Deleting run directory"\n'
        u'rmdir $(pwd)\n'
        u'echo "Finished at $(date)"'
        u'exit ${MPIRUN_EXIT_CODE}\n'
        u'\n'
    )
    return script
