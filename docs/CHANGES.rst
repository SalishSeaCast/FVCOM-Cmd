**********
Change Log
**********

Next Release
============

* Expand shell and user variables in namelist file paths.

* Use resolved repo path in VCS revisions recording message about uncommitted
  changes.

* Change to copy ref namelists to temporary run dir instead of symlinking them;
  facilitates easier run result archeology and reproducibility.

* Fix bug in atmospheric forcing file links checking function call.


1.0
===

* Enable ``namelist.namelist2dict()`` to handle Fortran boolean values ``true``
  and ``false`` (no leading/trailing dots).

* Confirm that the ``rebuild_nemo.exe`` executable in the ``prepare`` plug-in
  so that a run is not executed without it only to fail when the ``combine``
  plug-in is run.
  See https://bitbucket.org/salishsea/nemo-cmd/issues/19.

* Add find_rebuild_nemo_script() to the API.
  See https://bitbucket.org/salishsea/nemo-cmd/issues/20.

* For NEMO-3.6 only,
  restart file paths/filenames are now specified in a new ``restart`` section
  instead of in the ``forcing`` section.
  See https://nemo-cmd.readthedocs.io/en/latest/run_description_file/3.6_yaml_file.html#restart-section.

* The existence of all paths/files given in the run description YAML file
  is confirmed.
  An informative error message is emitted for paths/files that don't exist.

* Add optional ``filedefs`` item to output section of run description YAML
  file to facilitate the use of a ``file_Def.xml`` file with XIOS-2.

* Change spelling of keys in output section of run description YAML file:

  * ``files`` becomes ``iodefs``
  *  ``domain`` becomes ``domaindefs``
  *  ``fields`` becomes ``fielddefs``

  Old spellings are retained as fall-backs for backward compatibility.

* Fix Python 2.7 Unicode/str issue in Mercurial version control revision
  and status recording.
  See https://bitbucket.org/salishsea/nemo-cmd/issues/16.

* Add option to provide in the run description YAML file a list of
  PBS resource key-value pairs to produce ``#PBS -l`` directives for in the
  run shell script.
  See https://nemo-cmd.readthedocs.io/en/latest/run_description_file/3.6_yaml_file.html#pbs-resources-section,
  and https://bitbucket.org/salishsea/nemo-cmd/issues/10.

* Add option to provide in the run description YAML file a list of
  HPC environment modules to include ``module load`` commands for in the
  run shell script.
  See https://nemo-cmd.readthedocs.io/en/latest/run_description_file/3.6_yaml_file.html#modules-to-load-section,
  and https://bitbucket.org/salishsea/nemo-cmd/issues/11.

* Add the option to use absolute paths for coordinates and bathymetry files
  in the run description YAML file.
  See https://nemo-cmd.readthedocs.io/en/latest/run_description_file/3.6_yaml_file.html#grid-section,
  and https://bitbucket.org/salishsea/nemo-cmd/issues/5.

* Add ``nemo_cmd.fspath()``,
  ``nemo_cmd.expanded_path()``,
  and ``nemo_cmd.resolved_path()`` functions for
  working with file system paths.
  See https://nemo-cmd.readthedocs.io/en/latest/api.html#functions-for-working-with-file-system-paths.

* Port in the SalishSeaCmd ``run`` plug-in in a minimal form sufficient for
  use on TORQUE/PBS systems that don't require special PBS feature (-l)
  directives,
  or loading of environment modules.

* Add optional recording of revision and status of Mercurial version control
  repositories via a new ``vcs revisions`` section in the run description YAML
  file.

* For NEMO-3.6 only,
  enable the use of ref namelists from directories other than from
  ``CONFIG/SHARED/``.
  The default is to symlink to ``CONFIG/SHARED/namelist*_ref`` when there are no
  ``namelist*_ref`` keys in the ``namelists`` section of the run description
  YAML file.

* Change from using pathlib to pathlib2 package for Python 2.7 because the
  latter is the backport from the Python 3 stdlib that is being kept up to date.

* Refactor the ``combine`` plug-in to only run ``rebuild_nemo`` to combine
  per-processor results and/or restart files.

* Add ``deflate`` plug-in to deflate variables in netCDF files using Lempel-Ziv
  compression.

* Fix a bug whereby results directories were gathered with a redundant directory
  layer;
  e.g. the files in ``runs/9e5958d4-cb95-11e6-a99b-00259059edac/restart/``
  were gathered to ``results/25dec16/restart/restart/`` instead of
  ``results/25dec16/restart/``.


0.9
===

* Use `tox`_ for unified Python 2.7 and 3.5 testing.

  .. _tox: https://tox.readthedocs.io/en/latest/

* Refactor the ``gather`` plug-in in a minimal form sufficient for use by the
  ``GoMSS_Nowcast`` package.

* Refactor the ``prepare`` plug-in as the first ``nemo`` subcommand.

* Add token-based Fortran namelist parser from gist.github.com/krischer/4943658.
  That module also exists in the ``tools/SalishSeaTools`` package.
  It was brought into this package to avoid making this package depend on
  ``SalishSeaTools``.

* Adopt yapf for code style management.
  Project-specific style rules are set in ``.style.yapf``.

* Initialize project from the SalishSeaCmd/ directory of the tools repo with::

    hg convert --filemap tools/NEMO-Cmd_filemap.txt tools NEMO-Cmd

  A copy of ``NEMO-Cmd_filemap.txt`` is included in this repo.
