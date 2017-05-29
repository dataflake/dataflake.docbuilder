##############################################################################
#
# Copyright (c) 2011 Jens Vagelpohl and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Shared utility functions
"""

import os
import six
import subprocess


def shell_cmd(cmd, fromwhere=None):
    cwd = os.getcwd()
    if fromwhere:
        os.chdir(fromwhere)

    try:
        output = subprocess.check_output(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        output = e.output
        print('%s: %s' % (cmd, output))

    if six.PY3 and isinstance(output, bytes):
        output = output.decode('UTF-8')

    os.chdir(cwd)
    return output
