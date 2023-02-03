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
from six.moves.urllib.parse import urlparse
import sys

from dataflake.docbuilder.utils import shell_cmd


class RCSClient(object):
    """ RCS client base class.
    """

    def __init__(self, trunk_name='trunk', tags_name='tags',
                 logger=logging.getLogger()):
        self.trunk_name = trunk_name
        self.tags_name = tags_name
        self.logger = logger

    def checkout_or_update(self, url, workingdir, trunk_only=True):
        package_info = {}
        package_name = self.name_from_url(url)
        package_dir = os.path.join(workingdir, package_name)

        if not os.path.isdir(package_dir):
            os.mkdir(package_dir)

        trunk_path = os.path.join(package_dir, self.trunk_name)
        if os.path.isdir(trunk_path):
            self.logger.info('Updating %s trunk' % package_name)
            self.update(trunk_path)
        else:
            self.logger.info('Checking out %s trunk' % package_name)
            self.checkout(url, trunk_path)

        self.activate_egg(trunk_path)
        package_info[self.trunk_name] = None

        if not trunk_only:
            for tag in self.checkout_or_update_tags(url, package_dir):
                package_info[tag] = None

        return package_info

    def checkout_or_update_tags(self, package_url, package_dir):
        """ Check out or update all package tags

        Tags are only checked out once. Presumably, tags never change!
        """
        package_name = self.name_from_url(package_url)
        tag_names = self.get_tag_names(package_url, package_dir)
        for tag in tag_names:
            tag_path = os.path.join(package_dir, tag)
            if not os.path.isdir(tag_path):
                self.logger.info('Checking out %s %s' % (package_name, tag))
                self.checkout_tag(package_url, tag, tag_path)
                self.activate_egg(tag_path)
            else:
                msg = 'Already checked out: %s %s' % (package_name, tag)
                self.logger.info(msg)

        return tag_names

    def activate_egg(self, egg_path):
        """ Create the EGG_INFO structure in a checkout
        """
        if 'setup.py' in os.listdir(egg_path):
            pythonpath = ':'.join(sys.path)
            cmd = 'PYTHONPATH="%s" %s %s/setup.py egg_info' % (
                    pythonpath, sys.executable, egg_path)
            shell_cmd(cmd, fromwhere=egg_path)

    def name_from_url(self, url):
        """ Determine a package name from its VCS URL
        """
        parsed_url = urlparse(url)
        return [x for x in parsed_url[2].split('/') if x][-1]

    def checkout(self, url, targetpath):
        raise NotImplemented()

    def checkout_tag(self, url, tag, tatgetpath):
        raise NotImplemented()

    def update(self, targetpath):
        raise NotImplemented()

    def get_tag_names(self, url, checkout_path):
        raise NotImplemented()


class HGClient(RCSClient):

    def update(self, checkout_path):
        """ Update an existing checkout
        """
        shell_cmd('hg pull -u', fromwhere=checkout_path)

    def checkout(self, url, checkout_path):
        """ Check out from a repository
        """
        shell_cmd('hg clone %s %s' % (url, checkout_path))

    def checkout_tag(self, url, tag, checkout_path):
        """ Check out a specific tag
        """
        shell_cmd('hg clone -r %s %s %s' % (tag, url, checkout_path))

    def get_tag_names(self, url, checkout_path):
        """ Get all tag names from a repository URL
        """
        tags = []
        checkout_path = os.path.join(checkout_path, self.trunk_name)
        output = shell_cmd('hg tags', fromwhere=checkout_path)
        for line in output.split('\n'):
            tag, revision = line.split()
            if tag != 'tip':
                tags.append(tag)
        return sorted(tags)


class GitClient(RCSClient):

    def update(self, checkout_path):
        """ Update an existing checkout
        """
        shell_cmd('git pull -a', fromwhere=checkout_path)

    def checkout(self, url, checkout_path):
        """ Check out from a repository
        """
        shell_cmd('git clone %s %s' % (url, checkout_path))

    def checkout_tag(self, url, tag, checkout_path):
        """ Check out a specific tag
        """
        self.checkout(url, checkout_path)
        shell_cmd('git checkout %s' % tag, fromwhere=checkout_path)

    def get_tag_names(self, url, checkout_path):
        """ Get all tag names from a repository URL
        """
        tags = []
        checkout_path = os.path.join(checkout_path, self.trunk_name)
        output = shell_cmd('git tag', fromwhere=checkout_path)
        if output:
            for line in output.split('\n'):
                tags.append(line.strip())
        return sorted(tags)


class SVNClient(RCSClient):

    def update(self, checkout_path):
        """ Update an existing checkout
        """
        shell_cmd('svn up %s' % checkout_path)

    def checkout(self, url, checkout_path):
        """ Check out from a repository
        """
        shell_cmd('svn co %s/%s %s' % (url, self.trunk_name, checkout_path))

    def checkout_tag(self, url, tag, checkout_path):
        """ Check out a specific tag
        """
        cmd = 'svn co %s/%s/%s %s' % (url, self.tags_name, tag, checkout_path)
        shell_cmd(cmd)

    def get_tag_names(self, url, checkout_path):
        """ Get all tag names from a repository URL
        """
        cmd = 'svn ls %s/%s' % (url, self.tags_name)
        tag_names = [x.replace('/', '') for x in shell_cmd(cmd).split()]
        return sorted(tag_names)
