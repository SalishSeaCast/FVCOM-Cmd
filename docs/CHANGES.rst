**********
Change Log
**********

Next Release
============

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
