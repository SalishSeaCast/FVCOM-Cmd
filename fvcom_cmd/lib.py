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
"""Utility functions for use by FVCOM-Cmd sub-command plug-ins.
"""
import yaml

from fvcom_cmd import fspath, resolved_path, expanded_path

import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def load_run_desc(desc_file):
    """Load the run description file contents into a data structure.

    :param desc_file: File path/name of the YAML run description file.
    :type desc_file: :py:class:`pathlib.Path`

    :returns: Contents of run description file parsed from YAML into a dict.
    :rtype: dict
    """
    with open(fspath(desc_file), 'rt') as f:
        run_desc = yaml.load(f)
    return run_desc


def td2hms(timedelta):
    """Return a string that is the timedelta value formated as H:M:S
    with leading zeros on the minutes and seconds values.

    :arg timedelta: Time interval to format.
    :type timedelta: :py:obj:datetime.timedelta

    :returns: H:M:S string with leading zeros on the minutes and seconds
              values.
    :rtype: unicode
    """
    seconds = int(timedelta.total_seconds())
    periods = (('hour', 60 * 60), ('minute', 60), ('second', 1))
    hms = []
    for period_name, period_seconds in periods:
        period_value, seconds = divmod(seconds, period_seconds)
        hms.append(period_value)
    return u'{0[0]}:{0[1]:02d}:{0[2]:02d}'.format(hms)


def get_run_desc_value(
    run_desc,
    keys,
    expand_path=False,
    resolve_path=False,
    run_dir=None,
    fatal=True
):
    """Get the run description value defined by the sequence of keys.

    :param dict run_desc: Run description dictionary.

    :param sequence keys: Keys that lead to the value to be returned.

    :param boolean expand_path: When :py:obj:`True`, return the value as a
                                :class:`pathlib.Path` object with shell and
                                user variables expanded via
                                :func:`fvcom_cmd.expanded_path`.

    :param boolean resolve_path: When :py:obj:`True`, return the value as an
                                 absolute :class:`pathlib.Path` object with
                                 shell and user variables expanded and symbolic
                                 links resolved via
                                 :func:`fvcom_cmd.resolved_path`.
                                 Also confirm that the path exists,
                                 otherwise,
                                 raise a :py:exc:`SystemExit` exception.

    :param run_dir: Path of the temporary run directory.
    :type run_dir: :py:class:`pathlib.Path`

    :param boolean fatal: When :py:obj:`True`, delete the under construction
                          temporary run directory, and raise a
                          :py:exc:`SystemExit` exception.
                          Otherwise, raise a :py:exc:`KeyError` exception.

    :raises: :py:exc:`SystemExit` or :py:exc:`KeyError`

    :returns: Run description value defined by the sequence of keys.
    """
    try:
        value = run_desc
        for key in keys:
            value = value[key]
    except KeyError:
        if not fatal:
            raise
        logger.error(
            '"{}" key not found - please check your run description YAML file'
            .format(': '.join(keys))
        )
        #if run_dir:
        #    _remove_run_dir(run_dir)
        raise SystemExit(2)
    if expand_path:
        value = expanded_path(value)
    if resolve_path:
        value = resolved_path(value)
        if not value.exists():
            logger.error(
                '{path} path from "{keys}" key not found - please check your '
                'run description YAML file'.format(
                    path=value, keys=': '.join(keys)
                )
            )
            #if run_dir:
            #    _remove_run_dir(run_dir)
            raise SystemExit(2)
    return value


