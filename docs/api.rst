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


.. _NEMO-CmdAPI:

*******************
:kbd:`NEMO-Cmd` API
*******************

This section documents the NEMO command processor Application Programming Interface (API).
The API provides Python function interfaces to command processor sub-commands for use in other sub-command processor modules,
and by other software.

.. autofunction:: nemo_cmd.api.combine

.. autofunction:: nemo_cmd.api.deflate

.. autofunction:: nemo_cmd.api.gather

.. autofunction:: nemo_cmd.api.prepare

.. autofunction:: nemo_cmd.api.run_description

.. autofunction:: nemo_cmd.api.run_in_subprocess

.. autofunction:: nemo_cmd.api.pbs_common


Functions for Reading Fortran Namelists
=======================================

.. autofunction:: nemo_cmd.namelist.namelist2dict

.. autofunction:: nemo_cmd.namelist.get_namelist_value


.. _FileSystemPathFunctions:

Functions for Working with File System Paths
============================================

.. autofunction:: nemo_cmd.fspath

.. autofunction:: nemo_cmd.expanded_path

.. autofunction:: nemo_cmd.resolved_path


.. _UtilityFunction:

Utility Function
================

.. autofunction:: nemo_cmd.prepare.get_run_desc_value
