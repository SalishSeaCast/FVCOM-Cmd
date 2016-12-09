.. Copyright 2013-2016 The Salish Sea MEOPAR conttributors
.. and The University of British Columbia
..
.. Licensed under the Apache License, Version 2.0 (the "License");
.. you may not use this file except in compliance with the License.
.. You may obtain a copy of the License at
..
..    http://www.apache.org/licenses/LICENSE-2.0
..
.. Unless required by applicable law or agreed to in writing, software
.. distributed under the License is distributed on an "AS IS" BASIS,
.. WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
.. See the License for the specific language governing permissions and
.. limitations under the License.


.. _NEMO-CmdSubcommands:

****************************
:command:`nemo` Sub-Commands
****************************

The command :kbd:`nemo --help` produces a list of the available :program:`nemo` options and sub-commands::

  usage: nemo [--version] [-v | -q] [--log-file LOG_FILE] [-h] [--debug]

  NEMO Command Processor

  optional arguments:
    --version            show program's version number and exit
    -v, --verbose        Increase verbosity of output. Can be repeated.
    -q, --quiet          Suppress output except warnings and errors.
    --log-file LOG_FILE  Specify a file to log output. Disabled by default.
    -h, --help           Show help message and exit.
    --debug              Show tracebacks on errors.

  Commands:
    complete       print bash completion command
    gather         Gather results from a NEMO run.
    help           print detailed help for another command
    prepare        Prepare a NEMO run


For details of the arguments and options for a sub-command use
:command:`nemo help <sub-command>`.
For example:

.. code-block:: bash

    $ nemo help prepare

::

    usage: nemo prepare [-h] [--nocheck-initial-conditions] [--nemo3.4] [-q]
                        DESC_FILE

    Set up the NEMO run described in DESC_FILE and print the path to the run
    directory.

    positional arguments:
      DESC_FILE             run description YAML file

    optional arguments:
      -h, --help            show this help message and exit
      --nocheck-initial-conditions
                            Suppress checking of the initial conditions link.
                            Useful if you are submitting a job to an HPC qsub
                            queue and want the submitted job to wait for
                            completion of a previous job.
      --nemo3.4             Prepare a NEMO-3.4 run; the default is to prepare a
                            NEMO-3.6 run.
      -q, --quiet           don't show the run directory path on completion


You can check what version of :program:`nemo` you have installed with:

.. code-block:: bash

    nemo --version


.. _nemo-prepare:

:kbd:`prepare` Sub-command
==========================

The :command:`nemo prepare` command sets up a run directory from which to execute the NEMO run described in the specifed run description,
and output file definitions files::

  usage: nemo prepare [-h] [--nocheck-initial-conditions] [--nemo3.4] [-q]
                      DESC_FILE

  Set up the NEMO run described in DESC_FILE and print the path to the run
  directory.

  positional arguments:
    DESC_FILE             run description YAML file

  optional arguments:
    -h, --help            show this help message and exit
    --nocheck-initial-conditions
                          Suppress checking of the initial conditions link.
                          Useful if you are submitting a job to an HPC qsub
                          queue and want the submitted job to wait for
                          completion of a previous job.
    --nemo3.4             Prepare a NEMO-3.4 run; the default is to prepare a
                          NEMO-3.6 run.
    -q, --quiet           don't show the run directory path on completion

See the :ref:`RunDescriptionFileStructure` section for details of the run description file.

The :command:`nemo prepare` command concludes by printing the path to the run directory it created.
Example:

.. code-block:: bash

    $ nemo prepare SalishSea.yaml iodef.xml

    nemo_cmd.prepare INFO: Created run directory ../../runs/SalishSea/38e87e0c-472d-11e3-9c8e-0025909a8461

The name of the run directory created is a `Universally Unique Identifier`_
(UUID)
string because the directory is intended to be ephemerally used for a single run.

.. _Universally Unique Identifier: https://en.wikipedia.org/wiki/Universally_unique_identifier

If the :command:`nemo prepare` command prints an error message,
you can get a Python traceback containing more information about the error by re-running the command with the :kbd:`--debug` flag.


Run Directory Contents for NEMO-3.6
-----------------------------------

For NEMO-3.6 runs,
(initiated by the :command:`nemo prepare ...` command)
the run directory contains:

* The run description file provided on the command line.

* A :file:`namelist_cfg`
  (the file name required by NEMO)
  file that is constructed by concatenating the namelist segments listed in the run description file
  (see :ref:`RunDescriptionFileStructure`).

* A symlink to the :file:`NEMOGCM/CONFIG/SHARED/namelist_ref` file in the :kbd:`NEMO-code` directory specified in the :kbd:`paths` section of the run description file is also created to provide default values to be used for any namelist variables not included in the namelist segments listed in the run description file.

* A symlink called :file:`bathy_meter.nc`
  (the file name required by NEMO)
  to the bathymetry file specified in the :kbd:`grid` section of the run description file.

* A symlink called :file:`coordinates.nc`
  (the file name required by NEMO)
  to the grid coordinates file specified in the :kbd:`grid` section of the run description file.

* A file called :file:`domain_def.xml`
  (the file name required by NEMO)
  that contains the XIOS output server domain definitions for the run.
  The file that is copied to :file:`domain_def.xml` is specified in the :kbd:`output` section of the run description file.

* A file called :file:`field_def.xml`
  (the file name required by NEMO)
  that contains the XIOS output server field definitions for the run.
  The file that is copied to :file:`field_def.xml` is specified in the :kbd:`output` section of the run description file.

* A file called :file:`iodefs.xml`
  (the file name required by NEMO).
  that file specifies the output files and variables they contain for the run.
  The file that is copied to :file:`iodefs.xml` is specified in the :kbd:`output` section of the run description file.
  It is also sometimes referred to as the NEMO IOM defs file.

* The :file:`nemo.exe` executable found in the :file:`BLD/bin/` directory of the NEMO configuration given by the :kbd:`config name` and :kbd:`NEMO code config` keys in the run description file.
  :command:`nemo prepare` aborts with an error message and exit code 2 if the :file:`nemo.exe` file is not found.
  In that case the run directory is not created.

* The :file:`xios_server.exe` executable found in the :file:`bin/` sub-directory of the directory given by the :kbd:`XIOS` key in the :kbd:`paths` section of the run description file.
  :command:`nemo prepare` aborts with an error message and exit code 2 if the :file:`xios_server.exe` file is not found.
  In that case the run directory is not created.

The run directory also contains symbolic links to forcing directories
(e.g. initial conditions,
atmospheric,
open boundary conditions,
rivers run-off,
etc.)
The names of those symlinks and the directories that they point to are given in the :kbd:`forcing` section of the run description file.
Please see :ref:`NEMO-3.6-Forcing` in the :ref:`RunDescriptionFileStructure` docs for full details.
It is your responsibility to ensure that these symlinks match the forcing directories given in your namelist files.

Finally,
the run directory contains 3 files,
:file:`NEMO-code_rev.txt`,
:file:`NEMO-forcing_rev.txt`,
and :file:`XIOS-code_rev.txt` that contain the output of the :command:`hg parents` command executed in the directories given by the :kbd:`NEMO-code`,
:kbd:`forcing`,
and :kbd:`XIOS` keys in the :kbd:`paths` section of the run description file,
respectively.
Those file provide a record of the last committed changesets in each of those directories,
which is important reproducibility information for the run.


Run Directory Contents for NEMO-3.4
-----------------------------------

For NEMO-3.4 runs,
(initiated by the :command:`nemo prepare --nemo3.4 ...` command)
the run directory contains a :file:`namelist`
(the file name expected by NEMO)
file that is constructed by concatenating the namelist segments listed in the run description file
(see :ref:`RunDescriptionFileStructure`).
That constructed namelist is concluded with empty instances of all of the namelists that NEMO requires so that default values will be used for any namelist variables not included in the namelist segments listed in the run description file.

The run directory also contains symbolic links to:

* The run description file provided on the command line

* The :file:`namelist` file constructed from the namelists provided in the run description file

* A file called :file:`iodefs.xml`
  (the file name required by NEMO).
  that file specifies the output files and variables they contain for the run.
  The file that is copied to :file:`iodefs.xml` is specified in the :kbd:`output` section of the run description file.
  It is also sometimes referred to as the NEMO IOM defs file.

* The :file:`xmlio_server.def` file found in the run-set directory where the run description file resides

* The :file:`nemo.exe` and :file:`server.exe` executables found in the :file:`BLD/bin/` directory of the NEMO configuration given by the :kbd:`config_name` and :kbd:`NEMO-code` keys in the run description file.
  :command:`nemo prepare` aborts with an error message and exit code 2 if the :file:`nemo.exe` file is not found.
  In that case the run directory is not created.
  :command:`nemo prepare` also check to confirm that :file:`server.exe` exists but only issues a warning if it is not found becuase that is a valid situation if you are not using :kbd:`key_iomput` in your configuration.

* The coordinates and bathymetry files given in the :kbd:`grid` section of the run description file

* The initial conditions,
  open boundary conditions,
  and rivers run-off forcing directories given in the :kbd:`forcing` section of the run description file.
  The initial conditions may be specified from a restart file instead of a directory of netCDF files,
  in which case the restart file is symlinked as :file:`restart.nc`,
  the file name expected by NEMO.


.. _nemo-gather:

:kbd:`gather` Sub-command
=========================

The :command:`nemo gather` command moves results from a NEMO run into a results directory::

  usage: nemo gather [-h] RESULTS_DIR

  Gather the results files from the NEMO run in the present working directory
  into files in RESULTS_DIR. The run description file, namelist(s), and other
  files that define the run are also gathered into RESULTS_DIR. If RESULTS_DIR
  does not exist it will be created.

  positional arguments:
    RESULTS_DIR  directory to store results into

  optional arguments:
    -h, --help   show this help message and exit

If the :command:`nemo gather` command prints an error message,
you can get a Python traceback containing more information about the error by re-running the command with the :kbd:`--debug` flag.
