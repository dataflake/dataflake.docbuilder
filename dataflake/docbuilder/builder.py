##############################################################################
#
# Copyright (c) 2010-2011 Jens Vagelpohl and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" The documentation builder class
"""

from docutils.core import publish_file
from docutils.utils import SystemMessage
from io import StringIO
import logging
import optparse
import os
import pkg_resources
import re
import shutil
from sphinx.application import Sphinx
import sys

from dataflake.docbuilder.rcs import GitClient
from dataflake.docbuilder.rcs import HGClient
from dataflake.docbuilder.rcs import SVNClient
from dataflake.docbuilder.utils import shell_cmd

LOG = logging.getLogger()
LOG.addHandler(logging.StreamHandler(sys.stdout))
SUPPORTED_VCS = {'svn': SVNClient, 'git': GitClient, 'hg': HGClient}
VCS_SPEC_MATCH = re.compile(r'^\[(.*)\](.*)$')

OPTIONS = (
  optparse.make_option('-s', '--source',
                       action='append', dest='urls',
                       help='VCS URL (can be used multiple times)'),
  optparse.make_option('-g', '--grouping',
                       action='append', dest='groupings',
                       help='Package name to group name map, colon-separated'),
  optparse.make_option('-w', '--working-directory',
                       action='store', dest='workingdir',
                       help='working directory for package checkouts'),
  optparse.make_option('-o', '--output-directory',
                       action='store', dest='htmldir',
                       help='Root folder for HTML output and links (default: \
                             $working-directory/html)'),
  optparse.make_option('-c', '--copy-output',
                       action='store_true', dest='copy_output',
                       help='Copy all HTML output instead of linking it to \
                             the output directory'),
  optparse.make_option('-t', '--trunk-only',
                       action='store_true', dest='trunk_only',
                       help='Only build trunk documentation? (default: False)',
                       default=False),
  optparse.make_option('-m', '--max-tags',
                       action='store', dest='max_tags',
                       help='Max number of tags to show on the index page. \
                             If the value is "0" or "1", only the trunk is \
                             built. Default: 5',
                       default=5),
  optparse.make_option('-n', '--no-packages',
                       action='store_true', dest='no_packages',
                       help='Do not check out and build any package \
                             documentation. Default: False.',
                       default=False),
  optparse.make_option('-v', '--verbose',
                       action='count', dest='verbose',
                       help='Log verbosity'),
  optparse.make_option('--index-template',
                       action='store', dest='index_template',
                       help='Optional filesystem path containing Sphinx files \
                             for the output directory'),
  optparse.make_option('--index-name',
                       action='store', dest='index_name',
                       help='The index file name, without extension. Defaults \
                             to "index".',
                       default='index'),
  optparse.make_option('--fallback-css',
                       action='store', dest='fallback_css',
                       help='Path to a CSS file with styles used for plain \
                             ReST documentation'),
  optparse.make_option('--docs-directory',
                       action='append', dest='docs_folders',
                       help='Sphinx documentation folder name (can be used \
                             multiple times, default: "doc" and "docs")',
                       default=['doc', 'docs']),
  optparse.make_option('--trunk-directory',
                       action='store', dest='trunk_name',
                       help='Development trunk container name \
                             (default: "trunk")',
                       default='trunk'),
  optparse.make_option('--tags-directory',
                       action='store', dest='tags_name',
                       help='Development tags container name \
                             (default: "tags")',
                       default='tags'),
  optparse.make_option('--z3csphinx-output-directory',
                       action='store', dest='z3csphinx_output_directory',
                       help='Root folder for z3c.recipe.sphinx-generated \
                             documentation'),
)


class DocsBuilder(object):

    def __init__(self):
        parser = optparse.OptionParser(option_list=OPTIONS)
        self.options, self.args = parser.parse_args()
        self.packages = {}
        self.group_map = {}

        if self.options.verbose:
            LOG.setLevel(logging.DEBUG)
        else:
            LOG.setLevel(logging.WARNING)

        if not self.options.urls and \
           not self.options.z3csphinx_output_directory and \
           not self.options.no_packages:
            parser.error('Please provide package VCS URLs')

        if not self.options.workingdir:
            parser.error('Please provide a workingdir directory path')

        if not os.path.isdir(self.options.workingdir):
            msg = 'Creating output folder %s...' % self.options.workingdir
            LOG.info(msg)

        if not self.options.htmldir:
            self.options.htmldir = os.path.join(self.options.workingdir,
                                                'html')
            if not os.path.isdir(self.options.htmldir):
                os.mkdir(self.options.htmldir)
        elif not os.path.isdir(self.options.htmldir):
            msg = 'Creating HTML output folder %s...' % self.options.htmldir
            LOG.info(msg)

        try:
            self.options.max_tags = int(self.options.max_tags)
        except ValueError:
            LOG.error('Please specify a numeric value for --max-tags.')

        for group_spec in self.options.groupings or []:
            package_name, group_name = [x.strip() for x in
                                        group_spec.split(':')]
            group_values = self.group_map.setdefault(group_name, [])
            group_values.append(package_name)

        self.z3csphinx_packages = {}
        if self.options.z3csphinx_output_directory:
            root_pkgs = os.listdir(self.options.z3csphinx_output_directory)

            for pkg_name in root_pkgs:
                zod = self.options.z3csphinx_output_directory
                pkg_docs = os.path.join(zod, pkg_name, 'build', pkg_name)
                self.z3csphinx_packages[pkg_name] = pkg_docs

                if not self.options.urls:
                    self.packages[pkg_name] = \
                        {self.options.trunk_name: pkg_docs}

    def run(self):
        if self.options.no_packages and self.options.index_template:
            index_path = os.path.join(self.options.index_template,
                                      '%s.rst' % self.options.index_name)
            if not os.path.isfile(index_path):
                tmpl_path = os.path.join(self.options.index_template,
                                         '%s.rst.in' % self.options.index_name)
                shutil.copyfile(tmpl_path, index_path)
            self._build_sphinx()
            return

        grouped = []
        [grouped.extend(x) for x in self.group_map.values()]

        for url in self.options.urls or []:
            re_match = VCS_SPEC_MATCH.search(url)
            if re_match is not None:
                rcs_class = SUPPORTED_VCS.get(re_match.groups()[0].lower())
                package_url = re_match.groups()[1].strip()
            else:
                rcs_class = SUPPORTED_VCS.get('git')
                package_url = url

            if rcs_class is None:
                LOG.warning('Unsupported VCS URL, ignoring: %s' % url)
                continue

            rcs = rcs_class(self.options.trunk_name,
                            self.options.tags_name, logger=LOG)
            package_name = rcs.name_from_url(package_url)
            if package_name not in self.z3csphinx_packages:
                LOG.info('Checking out %s' % package_url)
                info = rcs.checkout_or_update(package_url,
                                              self.options.workingdir,
                                              self.options.trunk_only)
            else:
                info = {}

            self.packages[package_name] = info

        for package_name in self.packages.keys():
            if package_name not in grouped:
                group_values = self.group_map.setdefault('', [])
                group_values.append(package_name)

            if package_name not in self.z3csphinx_packages:
                self.build_html(package_name)
            else:
                pkg_docs = self.z3csphinx_packages.get(package_name)
                self.packages[package_name][self.options.trunk_name] = pkg_docs
            self.link_html(package_name)

        if self.options.index_template:
            self.create_index_html()

    def create_index_html(self):
        index_text = ''
        group_names = sorted(self.group_map.keys(), key=str.lower)
        output = {'package': PACKAGE_RST,
                  'link': LINK_RST,
                  'nolink': NOLINK_RST,
                  'groupheader': GROUPHEADER_RST}

        for group_name in group_names:
            package_names = sorted(self.group_map.get(group_name),
                                   key=str.lower)

            if group_name or (not group_name and len(group_names) > 1):
                group_name = group_name or 'Ungrouped'
                group_data = {'group_name': group_name,
                              'group_underline': '=' * len(group_name)}
                index_text += output['groupheader'] % group_data

            for package_name in package_names:
                tags_list = []
                tag_names = sorted(self.packages[package_name].keys(),
                                   key=pkg_resources.parse_version,
                                   reverse=True)

                # Make sure trunk stays at the top
                if self.options.trunk_name in tag_names:
                    tag_names.remove(self.options.trunk_name)
                    tag_names.insert(0, self.options.trunk_name)

                for tag_name in tag_names:
                    html_output_folder = self.packages[package_name][tag_name]
                    ptp = '%s-%s' % (package_name, tag_name)
                    tag_data = {'package_name': package_name,
                                'package_tag': tag_name,
                                'package_tag_path': ptp}
                    if tag_name == self.options.trunk_name:
                        tag_data['package_tag'] = 'development'
                        tag_data['package_tag_path'] = package_name

                        if self.options.trunk_only:
                            tag_data['package_tag'] = ''

                    if html_output_folder:
                        tag_txt = output['link'] % tag_data
                    else:
                        tag_txt = output['nolink'] % tag_data

                    tags_list.append(tag_txt)

                if self.options.trunk_only:
                    index_text += '%s\n' % tags_list[0]
                else:
                    underline = '_' * len(package_name)
                    if len(tags_list) > self.options.max_tags:
                        index_tags = tags_list[:self.options.max_tags]
                        more_link = MORE_RST % {'package_name': package_name}
                    else:
                        index_tags = tags_list[:]
                        more_link = ''
                    p_data = {'package_name': package_name,
                              'package_output': '\n'.join(index_tags),
                              'package_name_underline': underline}
                    index_text += output['package'] % p_data
                    index_text += more_link

                    # Create separate per-package page
                    pkg_file_path = os.path.join(self.options.index_template,
                                                 '%s.rst' % package_name)
                    package_file = open(pkg_file_path, 'w')
                    pkg_data = {'package_name': package_name,
                                'package_output': '\n'.join(tags_list),
                                'package_name_underline': underline}
                    package_file.write(':orphan:\n\n')
                    package_file.write(output['package'] % pkg_data)
                    package_file.close()

        index_path = os.path.join(self.options.index_template,
                                  '%s.rst' % self.options.index_name)
        template_path = os.path.join(self.options.index_template,
                                     '%s.rst.in' % self.options.index_name)
        if os.path.isfile(template_path):
            template_file = open(template_path, 'r')
            template_text = template_file.read()
            template_file.close()
        else:
            template_text = ''

        index_file = open(index_path, 'w')
        index_file.write(template_text)
        index_file.write('\n\n')
        index_file.write(index_text)
        index_file.close()

        required_index = os.path.join(self.options.index_template, 'index.rst')
        if index_path != required_index and not os.path.isfile(required_index):
            # Need to create a index.rst, otherwise Sphinx barfs
            required_index_contents = ''
            if os.path.isfile('%s.in' % required_index):
                tmpl = open('%s.in' % required_index, 'r')
                required_index_contents = tmpl.read()
                tmpl.close()
            tmp_index = open(required_index, 'w')
            tmp_index.write(required_index_contents)
            tmp_index.close()

        self._build_sphinx()

    def _build_sphinx(self):
        dt = os.path.join(self.options.index_template, '_build', 'doctrees')
        builder = Sphinx(self.options.index_template,
                         self.options.index_template,
                         self.options.htmldir,
                         dt,
                         'html',
                         {},
                         None,
                         warning=sys.stderr,
                         freshenv=False,
                         warningiserror=False,
                         tags=None)
        builder.build(True, None)

    def _build_simple_rst(self, package_name, tag_name):
        """ Build HTML output from the setuptools long_description
        """
        rst = ''
        package_path = os.path.join(self.options.workingdir, package_name)
        tag_folder = os.path.join(package_path, tag_name)
        if os.path.isdir(tag_folder):
            cmd = 'PYTHONPATH="%s" %s %s/setup.py --long-description' % (
                      ':'.join(sys.path), sys.executable, tag_folder)
            rst = shell_cmd(cmd, fromwhere=tag_folder)

        if rst and rst != 'UNKNOWN':
            build_folder = os.path.join(tag_folder, '.docbuilder_html')
            shutil.rmtree(build_folder, ignore_errors=True)
            os.mkdir(build_folder)
            output_path = os.path.join(build_folder, 'index.html')
            settings = {}
            if os.path.isfile(self.options.fallback_css):
                settings = {'stylesheet_path': self.options.fallback_css}
            try:
                publish_file(source=StringIO(rst),
                             writer_name='html',
                             destination_path=output_path,
                             settings_overrides=settings)
                self.packages[package_name][tag_name] = build_folder
                msg = 'Building simple ReST docs for %s %s.'
                LOG.info(msg % (package_name, tag_name))
            except SystemMessage as e:
                msg = 'Building simple ReST doc for %s %s failed!'
                LOG.error(msg % (package_name, tag_name))
                LOG.error(str(e))
                pass

    def build_html(self, package_name):
        package_path = os.path.join(self.options.workingdir, package_name)

        for tag in list(self.packages[package_name]):
            tag_folder = os.path.join(package_path, tag)
            doc_folder = None
            for folder_name in self.options.docs_folders:
                doc_candidate = os.path.join(tag_folder, folder_name)
                if os.path.isdir(doc_candidate) and \
                   os.path.isfile(os.path.join(doc_candidate, 'conf.py')):
                    doc_folder = doc_candidate
                    break

            if not doc_folder:
                # Last fallback: long description from setup.py
                self._build_simple_rst(package_name, tag)
                continue

            build_folder = os.path.join(doc_folder, '.build')
            shutil.rmtree(build_folder, ignore_errors=True)
            os.mkdir(build_folder)
            html_output_folder = os.path.join(build_folder, 'html')

            old_sys_path = sys.path
            distributions = []
            for root, dirs, files in os.walk(tag_folder):
                if '.svn' in dirs:
                    dirs.remove('.svn')
                for dir_name in dirs:
                    path = os.path.join(root, dir_name)
                    found = pkg_resources.find_distributions(path)
                    distributions.extend(found)

            for distribution in distributions:
                distribution.activate()
                pkg_resources.working_set.add_entry(distribution.location)

            if not distributions:
                pkg_resources.working_set.add_entry(tag_folder)

            if self.options.verbose and self.options.verbose > 1:
                output_pipeline = sys.stderr
            else:
                output_pipeline = None

            try:
                builder = Sphinx(doc_folder,
                                 doc_folder,
                                 html_output_folder,
                                 os.path.join(build_folder, 'doctrees'),
                                 'html',
                                 {},
                                 None,
                                 warning=output_pipeline,
                                 freshenv=False,
                                 warningiserror=False,
                                 tags=None)
                LOG.info('Building Sphinx docs for %s %s' % (
                            package_name, tag))
                builder.build(True, None)
                w = getattr(builder, '_warncount', 0)
                if w:
                    LOG.info('Sphinx build generated %s warnings/errors.' % w)
                self.packages[package_name][tag] = html_output_folder
                sys.path = old_sys_path
            except pkg_resources.DistributionNotFound as e:
                msg = 'Building Sphinx docs for %s %s failed: missing \
                       dependency %s'
                LOG.error(msg % (package_name, tag, str(e)))
            except IndexError as e:
                msg = 'Building Sphinx docs for %s %s failed: %s'
                LOG.error(msg % (package_name, tag, str(e)))

    def link_html(self, package_name):
        p_data = self.packages[package_name]
        tags_with_docs = [(x, p_data[x]) for x in p_data if p_data.get(x)]

        for tag_name, html_output_folder in tags_with_docs:
            if tag_name == self.options.trunk_name:
                target_name = package_name
            else:
                target_name = '%s-%s' % (package_name, tag_name)
            html_link_path = os.path.join(self.options.htmldir, target_name)

            if os.path.islink(html_link_path):
                os.remove(html_link_path)
            elif os.path.isdir(html_link_path):
                shutil.rmtree(html_link_path)
            elif os.path.lexists(html_link_path):
                os.remove(html_link_path)

            if self.options.copy_output:
                shutil.copytree(html_output_folder, html_link_path)
            else:
                os.symlink(html_output_folder, html_link_path)


LINK_RST = """\
* `%(package_name)s %(package_tag)s <./%(package_tag_path)s/index.html>`_\
"""
MORE_RST = """\
`view all versions... <./%(package_name)s.html>`_

"""
NOLINK_RST = '* %(package_name)s %(package_tag)s'
PACKAGE_RST = """
%(package_name)s
%(package_name_underline)s
%(package_output)s

"""
GROUPHEADER_RST = """
%(group_name)s
%(group_underline)s
"""
