.. Copyright 2013-2017 The Salish Sea MEOPAR contributors
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


.. _RunDescriptionFileStructure:

******************************
Run Description File Structure
******************************

:program:`nemo` run description files are written in YAML_.
They contain key-value pairs that define the names and locations of files and directories that the :program:`nemo` command processor uses to manage NEMO runs and their results.

.. _YAML: http://pyyaml.org/wiki/PyYAMLDocumentation

Run description files are typically stored in a sub-directory of a version controlled directory tree in which you also store your model configuration elements such as coordinates,
bathymetry,
initial conditions fields,
namelists,
etc.


NEMO-3.6 Run Description File
=============================

Example:

.. literalinclude:: nemo.yaml.example-NEMO-3.6
   :language: yaml

The meanings of the key-value pairs are:

:kbd:`config name`
  The name of the NEMO configuration to use for runs.
  It is the name of a directory in :file:`NEMOGCM/CONFIG/` in the :kbd:`NEMO-3.6-code` code directory given by the :kbd:`NEMO` key in the :ref:`NEMO-3.6-Paths`.

  This key may also be spelled :kbd:`config_name` for backward compatibility.

:kbd:`MPI decomposition`
  Specify how the domain is to be distributed over the processors in the :kbd:`i` (longitude) and :kbd:`j` (latitude) directions;
  e.g. :kbd:`8x18`.
  Those values are used to set the :kbd:`nammpp` namelist :kbd:`jpni` and :kbd:`jpnj` values.

:kbd:`run_id`
   The job identifier that appears in the :command:`qstat` listing.

:kbd:`walltime`
  The wall-clock time requested for the run.
  It limits the time that the job will run for on all machines,
  and it also affects queue priority for runs on shared HPC cluster machines such as Westgrid.
  It is important to allow some buffer time when calculating your walltime limits to allow for indeterminacy of the NEMO run,
  as well as the time required to post-process results files at the end of the run.

:kbd:`email`
  The email address at which you want to receive notification of the beginning and end of execution of the run,
  as well as notification of abnormal abort messages.


.. _NEMO-3.6-Paths:

:kbd:`paths` Section
--------------------

The :kbd:`paths` section of the run description file is a collection of directory paths that the :program:`nemo` command processor uses to find files in other repos that it needs.

:kbd:`NEMO code config`
  The path to the :file:`CONFIG/` directory in the :kbd:`NEMO-3.6` code tree
  (typically a version control system clone/checkout)
  where the NEMO configuration directories are to be found;
  e.g. :file:`$HOME/MEOPAR/NEMO-3.6/CONFIG/`.
  An absolute path is required because the path is used in both the current directory and the temporary run directory created in the :kbd:`runs directory`.
  You can use :kbd:`~` or :kbd:`$HOME` in the path,
  if you wish.

  This key may also be spelled :kbd:`NEMO-code-config` for backward compatibility.

:kbd:`XIOS`
  The path to the :kbd:`XIOS` code tree
  (typically a version control system clone/checkout)
  where the XIOS executable for the run is to be found.
  This path may be either absolute or relative.

:kbd:`forcing`
  The path to the directory tree where the netCDF files for the grid coordinates,
  bathymetry,
  initial conditions,
  open boundary conditions,
  etc. are to be found.
  This path may be either absolute or relative.

:kbd:`runs directory`
  The path to the directory where run directories will be created by the :command:`nemo prepare`) sub-command.
  This path may be either absolute or relative.


.. _NEMO-3.6-Grid:

:kbd:`grid` Section
-------------------

The :kbd:`grid` section of the run description file contains 2 key-value pairs that provide:

* the names of the coordinates and bathymetry files to use for the run, or,
* relative paths to the coordinates and bathymetry files to use for the run, or,
* absolute paths to the coordinates and bathymetry files to use for the run

If file names are provided,
those files are presumed to be in the :file:`grid/` sub-directory of the directory tree pointed to by the :kbd:`forcing` key in the :ref:`NEMO-3.6-Paths`.

If relative paths are given,
they are appended to the :file:`grid/` directory of the :kbd:`forcing` path.

If absolute paths are given,
they may use :kbd:`~`,
:kbd:`$HOME`,
or :kbd:`$USER`,
if you wish.

:kbd:`coordinates`
  The name of,
  or path to,
  the coordinates file to use for the run.
  It is symlinked in the run directory as :file:`coordinates.nc`
  (the file name required by NEMO).

:kbd:`bathymetry`
  The name of,
  or path to,
  the bathymetry file to use for the run
  It is symlinked in the run directory as :file:`bathy_meter.nc`
  (the file name required by NEMO).


.. _NEMO-3.6-Forcing:

:kbd:`forcing` Section
----------------------

The :kbd:`forcing` section of the run description file contains sub-sections that provide the names of directories and files that are to be symlinked in the run directory for NEMO to use to read initial conditions and forcing values from.

An example :kbd:`forcing` section:

.. code-block:: yaml

    forcing:
      NEMO-atmos:
        link to: /results/forcing/atmospheric/GEM2.5/operational/
      rivers:
        link to: rivers/

The sub-section keys
(:kbd:`NEMO-atmos` and :kbd:`rivers` above)
are the names of the symlinks that will be created in the run directory.
Those names are expected to appear in the appropriate places in the namelists.
The values associated with the :kbd:`link to` keys are the targets of the symlinks that will be created in the run directory.
The paths may be either absolute or relative.
If relative,
the paths are appended to the :kbd:`forcing` path given in the :ref:`NEMO-3.6-Paths`.

To provide a restart file for a run to use for initialization,
include a sub-section like:

.. code-block:: yaml

    forcing:
      ...
      restart.nc:
        link to: /results/SalishSea/spin-up/8sep17sep/SalishSea_02825280_restart.nc

NEMO requires that the name of the restart file be :kbd:`restart.nc`,
so that is the key that you must use.
For a tracers restart file the required file name (key) is :kbd:`restart_trc.nc`.

Apart from the restart file keys,
you are free to use any keys that you wish with the understanding that the key will be the name of the symlink that will be created in the run directory,
and that name will also need to appear as a directory name in the appropriate namelist.

The :command:`nemo prepare` sub-command and the :py:func:`nemo_cmd.api.prepare` API function confirm that the targets of the symlinks exist,
and exit with an error message if not.


Atmospheric Forcing File Checks
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Additional checking can be performed on the files in the atmospheric forcing directory.
That checking confirms the existence of all of the atmospheric forcing files for the date range of the run.
Doing so ensures that a run won't fail part way through due to a missing atmospheric forcing file.
To enable the additional checking add a :kbd:`check link` section at the same level as the :kbd:`link to` key:

.. code-block:: yaml

    forcing:
      NEMO-atmos:
        link to: /results/forcing/atmospheric/GEM2.5/operational/
        check link:
          type: atmospheric
          namelist filename: namelist_cfg

The :kbd:`type` key provides the type of checking to perform on the link.
The value associated with the :kbd:`namelist filename` key is the name of the namelist file in which the atmospheric forcing link is used.

Link checking can be disabled by excluding the :kbd:`check link` section,
or by setting the value associated with the :kbd:`type` key to :py:obj:`None`.


.. _NEMO-3.6-Namelists:

:kbd:`namelists` Section
------------------------

The :kbd:`namelists` section of the run description file contains a dict of lists of NEMO namelist section files that will be concatenated to construct :file:`namelist*_cfg` files
(the file names required by NEMO)
file for the run.
The paths may be either absolute or relative.
If relative paths are given,
they are appended to the directory containing the run description file.

Here is an example :kbd:`namelist` section:

.. code-block:: yaml

    namelists:
      namelist_cfg:
        - namelist.time
        - namelist.domain
        - namelist.surface
        - namelist.lateral
        - namelist.bottom
        - namelist.tracer
        - namelist.dynamics
        - namelist.vertical
        - namelist.compute
      namelist_top_cfg:
        - namelist_top_cfg
      namelist_pisces_cfg:
        - namelist_pisces_cfg

A :kbd:`namelist_cfg` key must be present,
other :kbd:`namelist*_cfg` keys are optional.
Each :kbd:`namelist*_cfg` section must be a list containing at least 1 namelist section file.

Namelist sections that are specific to the run such as :file:`namelist.time` where the starting and ending timesteps and the restart configuration are defined are typically stored in the same directory as the run description file.
That means that they are simply listed by name in the appropriate :kbd:`namelist*_cfg` section:

.. code-block:: yaml

    namelists:
      namelist_cfg:
        - namelist.time

On the other hand,
when you want to use a namelist section that contains your research group's current consensus best values,
list it as a relative or absolute path from the location of your run description file to the "standard" nameslist section files in the directory tree in which you also store your model configuration elements:

.. code-block:: yaml

    namelists:
      namelist_cfg:
        - ../../nemo3.6/namelist.bottom

For each :kbd:`namelist*_cfg` key a :file:`NEMOGCM/CONFIG/config_name/EXP00/namelist*_ref` file is symlinked into the run directory to provide default values that will be used for any namelist variables not included in the namelist section files listed in the :kbd:`namelists` section.
:kbd:`config_name` is the value of the :kbd:`config name` key in the run description file.

So,
:file:`NEMOGCM/CONFIG/config_name/EXP00/namelist_ref` will always be symlinked and,
if the :kbd:`namelist_top_cfg` key is present,
the :file:`NEMOGCM/CONFIG/config_name/EXP00/namelist_top_ref` file will also be symlinked into the run directory.

You can override the use of :file:`*_ref` namelists from :file:`CONFIG/config_name/EXP00/` by including a :file:`*_ref` namelist key.
For example:

.. code-block:: yaml

    config name: SMELT

    ...

    namelists:
      namelist_ref:
        - $HOME/MEOPAR/test-sponge/namelist_ref

will cause the :file:`namelist_ref` file in the :file:`$HOME/MEOPAR/test-sponge/namelist_ref` directory to be symlinked into the temporary run directory instead of :file:`CONFIG/SMELT/EXP00/namelist_ref`.


.. _NEMO-3.6-Output:

:kbd:`output` Section
---------------------

The :kbd:`output` section of the run description file contains key-value pairs that provide the names of the files that define the output files,
domains,
and fields to be used by the XIOS server for the run.
The paths may be either absolute or relative.
If relative paths are given,
they are appended to the directory containing the run description file.

:kbd:`files`
  The path and name of the :file:`iodef.xml` output files definitions file to use for the run.
  It is copied into the run directory as :file:`iodef.xml`
  (the file name required by XIOS).
  The value is typically either:

  * a relative or absolute path to an :file:`iodef.xml` file in the directory tree in which you also store your model configuration elements
  * a relative or absolute run-specific output files definitions file

:kbd:`domain`
  The path and name of the :file:`domain_def.xml` output domains definitions file to use for the run.
  It is copied into the run directory as :file:`domain_def.xml`
  (the file name required by XIOS).
  The value is typically either:

  * a relative or absolute path to a :file:`domain_def.xml` file in the directory tree in which you also store your model configuration elements
  * a relative or absolute run-specific output domains definitions file

:kbd:`fields`
  The path and name of the :file:`field_def.xml` output fields definitions file to use for the run.
  It is copied into the run directory as :file:`field_def.xml`
  (the file name required by XIOS).
  The value is typically a relative or absolute path to :file:`CONFIG/SHARED/field_def.xml`.

The :kbd:`output` section also contains key-value pairs that control how the XIOS server is run and,
in the case where it is run as a separate server,
the number of XIOS servers to run.

:kbd:`separate XIOS server`
  Boolean flag indicating whether the XIOS server should be run on separate processors from NEMO (:py:obj:`True`),
  or in attached mode on every NEMO processor (:py:obj:`False`).
  The :command:`nemo prepare` sub-command sets the value of the :kbd:`using_server` variable in the :kbd:`xios` context in the copy of the :file:`iodef.xml` file in the temporary run directory to reflect the :kbd:`separate XIOS server` value.

:kbd:`XIOS servers`
  The number of XIOS servers to run when the value of :kbd:`separate XIOS server` it :py:obj:`True`.
  The number of XIOS servers is added to the number of NEMO processors calculated from the :kbd:`MPI decomposition` value to specify the total number of processors requested in the :kbd:`#PBS` directives section of the :file:`NEMO.sh` script generated by the :command:`nemo run` sub-command.


.. _NEMO-3.6-VCS-Revisions:

:kbd:`vcs revisions` Section
----------------------------

The optional :kbd:`vcs revisions` section of the run description file contains lists of version control system repositories of which the revision and status will be recorded in the temporary run and run results directories.

An example :kbd:`vcs revisions` section:

.. code-block:: yaml

    vcs revisions:
      hg:
        - $HOME/CANYONS/NEMO-3.6-code/
        - $HOME/CANYONS/XIOS/
        - $HOME/CANYONS/mackenzie_canyon/

The sub-section keys
(:kbd:`hg` above)
are the names of the version control tools to use for the repositories listed below them.
At present only Mercurial
(:kbd:`hg`)
is supported.

The paths listed under the version control tool key are the repositories of which the revision and status will be recorded.
The repository paths may be relative or absolute,
and may contain :kbd:`~` or :envvar:`$HOME` as alternative spellings of the user's home directory,
and :envvar:`$USER` as an alternative spelling of the user's userid.
For each repository,
a file will be created in the temporary run directory.
The file names are the repository directory names with :kbd:`_rev.txt` appended.
So,
from the example above,
the files created will be::

  NEMO-3.6-code_rev.txt
  XIOS_rev.txt
  mackenzie_canyon_rev.txt

Each file will contain the output of the :command:`hg parents -v` command for the repository.
That is a record of the last committed revision of the repository that will be in effect for the run.
For example,
:file:`NEMO-3.6-code_rev.txt` might contain::

  changset:   501:20bcd3fda18ceec47b7d1998118f57b0a526b4d2
  tag:        tip
  user:       Michael Dunphy <mdunphy@eoas.ubc.ca>
  date:       Mon Nov 14 09:49:40 2016 -08:00
  files:      NEMOGCM/CONFIG/SalishSea/MY_SRC/bdyini.F90 NEMOGCM/CONFIG/SalishSea/MY_SRC/tideini.F90
  description:
  Fix uninitialized variables in bdyini.F90 and tideini.F90

If any of the listed repositories contain uncommitted changes,
the :command:`nemo prepare` command will generate a warning message like::

  nemo_cmd.prepare WARNING: There are uncommitted changes in $HOME/CANYONS/mackenzie_canyon/

and the list of uncommitted changes and their status codes,
the output of the :command:`hg status -mardC` command,
will be appended to the :file:`_rev.txt` file.


.. _NEMO-3.6-PBS-resources:

:kbd:`PBS resources` Section
----------------------------

The optional :kbd:`PBS resources` section of the run description file contains a list of HPC resource key-value pairs for which :kbd:`#PBS -l` directives will be added to the :file:`NEMO.sh` script in the temporary run directory.
You will need to use this section if you are running on an HPC system and need to request special resources;
otherwise,
you can omit the :kbd:`PBS resources` section.

.. _HPC resource: http://docs.adaptivecomputing.com/torque/6-1-0/adminGuide/help.htm#topics/torque/2-jobs/requestingRes.htm

An example of a :kbd:`PBS resources` section is:

.. code-block:: yaml

    PBS resources:
      - partition=QDR

That will result in a line like::

  #PBS -l partition=QDR

being included in the :file:`NEMO.sh` script in the temporary run directory.

.. note::
    The :command:`nemo` :ref:`nemo-run` uses information in the run description files to provide the  values for the following resources for you:

    * :kbd:`procs` (number of processors)
    * :kbd:`pmem` (memory per processor)
    * :kbd:`walltime` (maximum run time for job)

    so you should not include them in your :kbd:`PBS resources` section.

Some HPC systems
(`jasper.westgrid.ca`_ for example)
may require or suggest that you use a :kbd:`nodes=n:ppn=p` resource request,
where :kbd:`n` is the number of nodes,
and :kbd:`p` is the number of processors per node.
:command:`nemo run` will calculate :kbd:`n` for you based on the values you give for :kbd:`p`,
:kbd:`MPI decomposition`,
and :kbd:`XIOS servers`.
So,
the value you use for :kbd:`n` is unimportant because it will be replaced in the :file:`NEMO.sh` script in the temporary run directory with the value that is appropriate for the run.
For example,
the following run description file entries:

.. code-block:: yaml

    MPI decomposition: 3x4
    ...
    output:
      ...
      XIOS servers: 1
    ...
    PBS resources:
      - nodes=n:ppn=12

will result in a :kbd:`#PBS -l nodes=2:ppn=12` directive being included in the :file:`NEMO.sh` script.

.. _jasper.westgrid.ca: https://www.westgrid.ca/support/quickstart/jasper


.. _NEMO-3.6-ModulesToLoad:

:kbd:`modules to load` Section
------------------------------

The optional :kbd:`modules to load` section of the run description file contains a list of HPC `environment modules`_ for which :command:`module load` commands will be added to the :file:`NEMO.sh` script in the temporary run directory.
You will need to use this section if you are running on an HPC system that uses environment modules;
otherwise,
you can omit the :kbd:`modules to load` section.

.. _environment modules: http://modules.sourceforge.net/

An example of a :kbd:`modules to load` section is:

.. code-block:: yaml

    modules to load:
      - intel
      - intel/14.0/netcdf-4.3.3.1_mpi
      - intel/14.0/netcdf-fortran-4.4.0_mpi
      - intel/14.0/hdf5-1.8.15p1_mpi
      - intel/14.0/nco-4.5.2
      - python

You will need to determine the specific list of modules to load and how to spell them for the HPC system that you are running on.
In general,
you will probably need to load modules for:

* the compiler you used to build NEMO and XIOS
* the netcdf,
  netcdf-fortran,
  and hdf5 libraries that you used to build NEMO and XIOS
* the nco library to make the :command:`ncks` available for the :command:`nemo` :ref:`nemo-deflate`
* the Python language


NEMO-3.4 Run Description File
=============================

Example:

.. literalinclude:: nemo.yaml.example-NEMO-3.4
   :language: yaml

The meanings of the key-value pairs are:

:kbd:`config name`
  The name of the NEMO configuration to use for runs.
  It is the name of a directory in :file:`NEMOGCM/CONFIG/` in the :kbd:`NEMO-code` code directory given by the :kbd:`NEMO` key in the :ref:`NEMO-3.4-Paths`.

  This key may also be spelled :kbd:`config_name` for backward compatibility.

:kbd:`MPI decomposition`
  Specify how the domain is to be distributed over the processors in the :kbd:`i` (longitude) and :kbd:`j` (latitude) directions;
  e.g. :kbd:`8x18`.
  Those values are used to set the :kbd:`nammpp` namelist :kbd:`jpni` and :kbd:`jpnj` values.

:kbd:`run_id`
   The job identifier that appears in the :command:`qstat` listing.

:kbd:`walltime`
  The wall-clock time requested for the run.
  It limits the time that the job will run for on all machines,
  and it also affects queue priority for runs on on shared HPC cluster machines such as Westgrid.
  It is important to allow some buffer time when calculating your walltime limits to allow for indeterminacy of the NEMO run,
  as well as the time required to post-process results files at the end of the run.

:kbd:`email`
  The email address at which you want to receive notification of the beginning and end of execution of the run,
  as well as notification of abnormal abort messages.


.. _NEMO-3.4-Paths:

:kbd:`paths` Section
--------------------

The :kbd:`paths` section of the run description file is a collection of directory paths that the :program:`nemo` command processor uses to find files in other repos that it needs.

:kbd:`NEMO code config`
  The path to the :file:`CONFIG/` directory in the :kbd:`NEMO-3.4` code tree
  (typically a version control system clone/checkout)
  where the NEMO configuration directories are to be found;
  e.g. :file:`$HOME/MEOPAR/NEMO-3.4/NEMOGCM/CONFIG/`.
  An absolute path is required because the path is used in both the current directory and the temporary run directory created in the :kbd:`runs directory`.
  You can use :kbd:`~` or :kbd:`$HOME` in the path,
  if you wish.

  This key may also be spelled :kbd:`NEMO-code-config` for backward compatibility.

:kbd:`forcing`
  The path to the directory tree where the netCDF files for the grid coordinates,
  coordinates,
  bathymetry,
  initial conditions,
  open boundary conditions,
  etc. are to be found.
  This path may be either absolute or relative.

:kbd:`runs directory`
  The path to the directory where run directories will be created by the :command:`salishsea prepare --nemo3.4` sub-command.
  This path may be either absolute or relative.


.. _NEMO-3.4-Grid:

:kbd:`grid` Section
-------------------

The :kbd:`grid` section of the run description file contains 2 key-value pairs that provide:

* the names of the coordinates and bathymetry files to use for the run, or,
* relative paths to the coordinates and bathymetry files to use for the run, or,
* absolute paths to the coordinates and bathymetry files to use for the run

If file names are provided,
those files are presumed to be in the :file:`grid/` sub-directory of the directory tree pointed to by the :kbd:`forcing` key in the :ref:`NEMO-3.6-Paths`.

If relative paths are given,
they are appended to the :file:`grid/` directory of the :kbd:`forcing` path.

If absolute paths are given,
they may use :kbd:`~`,
:kbd:`$HOME`,
or :kbd:`$USER`,
if you wish.

:kbd:`coordinates`
  The name of,
  or path to,
  the coordinates file to use for the run.
  It is symlinked in the run directory as :file:`coordinates.nc`
  (the file name required by NEMO).

:kbd:`bathymetry`
  The name of,
  or path to,
  the bathymetry file to use for the run
  It is symlinked in the run directory as :file:`bathy_meter.nc`
  (the file name required by NEMO).


.. _NEMO-3.4-Forcing:

:kbd:`forcing` Section
----------------------

The :kbd:`forcing` section of the run description file contains key-value pairss that provide the names of sub-directories in the directory tree in which you also store your model configuration elements pointed to by the :kbd:`forcing` key in the :ref:`NEMO-3.4-Paths` where initial conditions and forcing files are found.
Those directory names are expected to appear in the appropriate places in the namelists.
The paths may be either absolute or relative.
If relative,
the paths are appended to the :kbd:`forcing` path given in the :ref:`NEMO-3.4-Paths`.

:kbd:`atmospheric`
  The path to the directory containing your atmospheric forcing files.
  It is symlinked as :file:`NEMO-atmos/` in the run directory,
  and that directory name must be used in the :kbd:`namelist.surface namsbc_core` and :kbd:`namesbc_apr` namelist.

:kbd:`initial conditions`
  The path to the directory containing your initial temperature and salinity field files.
  It is symlinked as :file:`initial_strat/` in the run directory,
  and that directory name must be used in the :kbd:`namlist.domain namtsd` namelist.

  The :kbd:`initial conditions` key can,
  alternatively,
  be used to give the path to and name of a restart file,
  e.g.:

  .. code-block:: yaml

      initial conditions: /ocean/dlatorne/MEOPAR/SalishSea/results/spin-up/8sep17sep/SalishSea_02825280_restart.nc

  which will be symlinked in the run directory as :file:`restart.nc`.

:kbd:`open boundaries`
  The path to the the directory containing your open boundary conditions files.
  It is symlinked as :file:`open_boundaries/` in the run directory,
  and that directory name must be used in the :kbd:`namelist.lateral nambdy_dat` namelists.

:kbd:`rivers`
  The path to the directory containing your river runoff files.
  It is symlinked as :file:`rivers/` in the run directory,
  and that directory name must be used in the :kbd:`namlist.domain namsbc_rnf` namelist.


.. _NEMO-3.4-Namelists:

:kbd:`namelists` Section
------------------------

The :kbd:`namelists` section of the run description file contains a list of NEMO namelist section files that will be concatenated to construct the :file:`namelist`
(the file name required by NEMO)
file for the run.
The paths may be either absolute or relative.
If relative paths are given,
they are appended to the directory containing the run description file.

Namelist sections that are specific to the run such as :file:`namelist.time` where the starting and ending timesteps and the restart configuration are defined are typically stored in the same directory as the run description file.
That mean that they are simply listed by name in the :kbd:`namelists` section:

.. code-block:: yaml

    namelists:
      - namelist.time

On the other hand,
when you want to use a namelist section that contains your group's current consensus best values,
list it as a relative path from the location of your run description file to the "standard" nameslist section files in the directory tree in which you also store your model configuration elements:

.. code-block:: yaml

    namlists:
      - ../../namelist.bottom

That constructed :file:`namelist` is concluded with empty instances of all of the namelists that NEMO-3.4 requires so that default values will be used for any namelist variables not included in the namelist section files listed in the run description file.
The blob of empty namelist instances is defined as a constant in the :py:mod:`NEMO-Cmd.nemo_cmd.prepare.py` module.


.. _NEMO-3.4-Output:

:kbd:`output` Section
---------------------

The :kbd:`output` section of the run description file contains a single key-value pair that provides the name of the file that defines the output files
to be used by the XIOS server for the run.
The path may be either absolute or relative.
If relative a path is given,
it is appended to the directory containing the run description file.

:kbd:`files`
  The path and name of the :file:`iodef.xml` output files definitions file to use for the run.
  It is copied into the run directory as :file:`iodef.xml`
  (the file name required by XIOS).
  The value is typically either:

  * a relative or absolute path to an :file:`iodef.xml` file in the directory tree in which you also store your model configuration elements
  * a relative or absolute run-specific output files definitions file


.. _NEMO-3.4-VCS-Revisions:

:kbd:`vcs revisions` Section
----------------------------

The optional :kbd:`vcs revisions` section of the run description file contains lists of version control system repositories of which the revision and status will be recorded in the temporary run and run results directories.

An example :kbd:`vcs revisions` section:

.. code-block:: yaml

    vcs revisions:
      hg:
        - $HOME/Canyons/NEMO-3.6-code/
        - $HOME/Canyons/XIOS/
        - $HOME/Canyons/mackenzie_canyon/

The sub-section keys
(:kbd:`hg` above)
are the names of the version control tools to use for the repositories listed below them.
At present only Mercurial
(:kbd:`hg`)
is supported.

The paths listed under the version control tool key are the repositories of which the revision and status will be recorded.
The repository paths may be relative or absolute,
and may contain :kbd:`~` or :envvar:`$HOME` as alternative spellings of the user's home directory,
and :envvar:`$USER` as an alternative spelling of the user's userid.
For each repository,
a file will be created in the temporary run directory.
The file names are the repository directory names with :kbd:`_rev.txt` appended.
So,
from the example above,
the files created will be::

  NEMO-code_rev.txt
  XIOS_rev.txt
  mackenzie_canyon_rev.txt

Each file will contain the output of the :command:`hg parents -v` command for the repository.
That is a record of the last committed revision of the repository that will be in effect for the run.
For example,
:file:`NEMO-code_rev.txt` might contain::

  changset:   501:20bcd3fda18ceec47b7d1998118f57b0a526b4d2
  tag:        tip
  user:       Michael Dunphy <mdunphy@eoas.ubc.ca>
  date:       Mon Nov 14 09:49:40 2016 -08:00
  files:      NEMOGCM/CONFIG/SalishSea/MY_SRC/bdyini.F90 NEMOGCM/CONFIG/SalishSea/MY_SRC/tideini.F90
  description:
  Fix uninitialized variables in bdyini.F90 and tideini.F90

If any of the listed repositories contain uncommitted changes,
the :command:`nemo prepare` command will generate a warning message like::

  nemo_cmd.prepare WARNING: There are uncommitted changes in $HOME/Canyons/mackenzie_canyon/

and the list of uncommitted changes and their status codes,
the output of the :command:`hg status -mardC` command,
will be appended to the :file:`_rev.txt` file.


.. _NEMO-3.4-PBS-resources:

:kbd:`PBS resources` Section
----------------------------

The optional :kbd:`PBS resources` section of the run description file contains a list of HPC resource key-value pairs for which :kbd:`#PBS -l` directives will be added to the :file:`NEMO.sh` script in the temporary run directory.
You will need to use this section if you are running on an HPC system and need to request special resources;
otherwise,
you can omit the :kbd:`PBS resources` section.

.. _HPC resource: http://docs.adaptivecomputing.com/torque/6-1-0/adminGuide/help.htm#topics/torque/2-jobs/requestingRes.htm

An example of a :kbd:`PBS resources` section is:

.. code-block:: yaml

    PBS resources:
      - partition=QDR

That will result in a line like::

  #PBS -l partition=QDR

being included in the :file:`NEMO.sh` script in the temporary run directory.

.. note::
    The :command:`nemo` :ref:`nemo-run` uses information in the run description files to provide the  values for the following resources for you:

    * :kbd:`procs` (number of processors)
    * :kbd:`pmem` (memory per processor)
    * :kbd:`walltime` (maximum run time for job)

    so you should not include them in your :kbd:`PBS resources` section.

Some HPC systems
(`jasper.westgrid.ca`_ for example)
may require or suggest that you use a :kbd:`nodes=n:ppn=p` resource request,
where :kbd:`n` is the number of nodes,
and :kbd:`p` is the number of processors per node.
:command:`nemo run` will calculate :kbd:`n` for you based on the values you give for :kbd:`p`,
:kbd:`MPI decomposition`,
and :kbd:`XIOS servers`.
So,
the value you use for :kbd:`n` is unimportant because it will be replaced in the :file:`NEMO.sh` script in the temporary run directory with the value that is appropriate for the run.
For example,
the following run description file entries:

.. code-block:: yaml

    MPI decomposition: 3x4
    ...
    output:
      ...
      XIOS servers: 1
    ...
    PBS resources:
      - nodes=n:ppn=12

will result in a :kbd:`#PBS -l nodes=2:ppn=12` directive being included in the :file:`NEMO.sh` script.

.. _jasper.westgrid.ca: https://www.westgrid.ca/support/quickstart/jasper


.. _NEMO-3.4-ModulesToLoad:

:kbd:`modules to load` Section
------------------------------

The optional :kbd:`modules to load` section of the run description file contains a list of HPC `environment modules`_ for which :command:`module load` commands will be added to the :file:`NEMO.sh` script in the temporary run directory.
You will need to use this section if you are running on an HPC system that uses environment modules;
otherwise,
you can omit the :kbd:`modules to load` section.

.. _environment modules: http://modules.sourceforge.net/

An example of a :kbd:`modules to load` section is:

.. code-block:: yaml

    modules to load:
      - intel
      - intel/14.0/netcdf-4.3.3.1_mpi
      - intel/14.0/netcdf-fortran-4.4.0_mpi
      - intel/14.0/hdf5-1.8.15p1_mpi
      - intel/14.0/nco-4.5.2
      - python

You will need to determine the specific list of modules to load and how to spell them for the HPC system that you are running on.
In general,
you will probably need to load modules for:

* the compiler you used to build NEMO and XIOS
* the netcdf,
  netcdf-fortran,
  and hdf5 libraries that you used to build NEMO and XIOS
* the nco library to make the :command:`ncks` available for the :command:`nemo` :ref:`nemo-deflate`
* the Python language
