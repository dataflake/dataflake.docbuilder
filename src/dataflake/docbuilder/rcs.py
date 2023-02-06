##############################################################################
#
# Copyright (c) 2010-2023 Jens Vagelpohl and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Abstracted revision control
"""

import logging
import os
import sys
from urllib.parse import urlparse

from .utils import shell_cmd


class RCSClient:
    """ RCS client base class.
    """

    def __init__(self, logger=logging.getLogger()):
        self.logger = logger
        self.main_branch = None

    def checkout_or_update(self, url, workingdir, trunk_only=True):
        package_name = self.name_from_url(url)
        package_dir = os.path.join(workingdir, package_name)
        package_info = {
            'name': package_name,
            'url': url,
            'path': package_dir,
            'tags': [],
            'main_branch': self.get_main_branch_name(url, package_dir),
            }

        if os.path.isdir(package_dir):
            self.logger.info(f'Updating {package_name}')
            current = self.get_current_branch_name(package_dir)
            main = self.get_main_branch_name(url, package_dir)
            if current != main:
                self.checkout_tag(url, main, package_dir)
            self.update(package_dir)
        else:
            self.logger.info(f'Cloning {package_name}')
            self.checkout(url, package_dir)

        if not trunk_only:
            package_info['tags'] = self.get_tag_names(url, package_dir)

        return package_info

    def checkout_or_update_tags(self, package_url, package_dir):
        """ Check out or update all package tags

        Tags are only checked out once. Presumably, tags never change!
        """
        package_name = self.name_from_url(package_url)
        tag_names = self.get_tag_names(package_url, package_dir)
        for tag in tag_names:
            self.logger.info(f'Switching {package_name} to tag {tag}')
            self.checkout_tag(package_url, tag, package_dir)
            self.activate_egg(package_dir)

        return tag_names

    def activate_egg(self, egg_path):
        """ Create the EGG_INFO structure in a checkout
        """
        if 'setup.py' in os.listdir(egg_path):
            pythonpath = ':'.join(sys.path)
            cmd = (f'PYTHONPATH="{pythonpath}" {sys.executable}'
                   f' {egg_path}/setup.py egg_info')
            shell_cmd(cmd, fromwhere=egg_path)

    def name_from_url(self, url):
        """ Determine a package name from its VCS URL
        """
        parsed_url = urlparse(url)
        return [x for x in parsed_url[2].split('/') if x][-1]

    def checkout(self, url, targetpath):
        raise NotImplementedError()

    def checkout_tag(self, url, tag, targetpath):
        raise NotImplementedError()

    def update(self, targetpath):
        raise NotImplementedError()

    def get_tag_names(self, url, checkout_path):
        raise NotImplementedError()

    def get_main_branch_name(self, url, checkout_path):
        raise NotImplementedError()

    def get_current_branch_name(self, checkout_path):
        raise NotImplementedError()


class GitClient(RCSClient):

    def __init__(self, logger=logging.getLogger()):
        super().__init__(logger=logging.getLogger())
        version_output = shell_cmd('git --version')
        self.version = version_output.split()[-1]

    def update(self, checkout_path):
        """ Update an existing checkout
        """
        shell_cmd('git fetch -q --all && git pull', fromwhere=checkout_path)

    def checkout(self, url, checkout_path):
        """ Check out from a repository
        """
        shell_cmd(f'git clone -q {url} {checkout_path}')
        # Silence warnings
        shell_cmd('git config --local advice.detachedHead "false"',
                  fromwhere=checkout_path)

    def checkout_tag(self, url, tag, checkout_path):
        """ Check out a specific tag
        """
        shell_cmd(f'git checkout -q {tag}', fromwhere=checkout_path)

    def get_tag_names(self, url, checkout_path):
        """ Get all tag names from a repository URL

        ``git tag`` is doing the sorting here.
        """
        tags = []
        if self.version < '2':
            cmd = 'git tag'
        else:
            cmd = 'git tag --sort=version:refname'
        output = shell_cmd(cmd, fromwhere=checkout_path)
        if output:
            for line in output.split():
                tags.append(line.strip())
        return tags

    def get_main_branch_name(self, url, checkout_path):
        """ Get the main of the main development branch
        """
        if not os.path.isdir(checkout_path):
            self.checkout(url, checkout_path)
        output = shell_cmd('git rev-parse --abbrev-ref origin/HEAD',
                           fromwhere=checkout_path)
        if output:
            return output.strip().split('/')[-1]

    def get_current_branch_name(self, checkout_path):
        """ Get the current branch name
        """
        if self.version < '2':
            output = shell_cmd('git branch', fromwhere=checkout_path)
            for line in output.split('\n'):
                if line.strip().startswith('*'):
                    return line.split()[-1].strip()

        return shell_cmd('git branch --show-current', fromwhere=checkout_path)
