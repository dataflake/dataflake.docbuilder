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

import commands
import os


def shell_cmd(cmd, fromwhere=None):
    cwd = os.getcwd()
    if fromwhere:
        os.chdir(fromwhere)
    status, output = commands.getstatusoutput(cmd)
    os.chdir(cwd)
    if status:
        print '%s: %s' % (cmd, output)
    return output
