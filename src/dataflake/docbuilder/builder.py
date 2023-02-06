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
""" The documentation builder class
"""

import logging
import optparse
import os
import re
import shutil
import sys

import pkg_resources
from sphinx.application import Sphinx

from .rcs import GitClient
from .rcs import HGClient


LOG = logging.getLogger()
LOG.addHandler(logging.StreamHandler(sys.stdout))
SUPPORTED_VCS = {'git': GitClient, 'hg': HGClient}
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
  optparse.make_option('--docs-directory',
                       action='append', dest='docs_folders',
                       help='Sphinx documentation folder name (can be used \
                             multiple times, default: "doc" and "docs")',
                       default=['doc', 'docs']),
)


class DocsBuilder:

    def __init__(self):
        parser = optparse.OptionParser(option_list=OPTIONS)
        self.options, self.args = parser.parse_args()
        self.packages = {}
        self.group_map = {}
        self.rcs = None

        if self.options.verbose:
            LOG.setLevel(logging.DEBUG)
        else:
            LOG.setLevel(logging.WARNING)

        if not self.options.urls:
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
            package_name, group_name = (x.strip() for x in
                                        group_spec.split(':'))
            group_values = self.group_map.setdefault(group_name, [])
            group_values.append(package_name)

    def run(self):
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
                LOG.warning(f'Unsupported VCS URL, ignoring: {url}')
                continue

            self.rcs = rcs_class(logger=LOG)
            package_name = self.rcs.name_from_url(package_url)
            LOG.info(f'Cloning/updating {package_url}')
            info = self.rcs.checkout_or_update(
                package_url,
                self.options.workingdir,
                trunk_only=self.options.trunk_only)
            self.packages[package_name] = info

        for package_name in self.packages.keys():
            if package_name not in grouped:
                group_values = self.group_map.setdefault('', [])
                group_values.append(package_name)

            self.build_html(package_name)

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
                package_info = self.packages[package_name]
                main_branch = package_info['main_branch']
                tag_names = list(reversed(package_info['tags']))
                if self.options.max_tags:
                    tag_names = tag_names[:self.options.max_tags]
                tag_names.insert(0, main_branch)

                for tag_name in tag_names:
                    html_output_folder = package_info['tag_html'].get(tag_name)
                    tag_data = {'package_name': package_name,
                                'package_tag': tag_name,
                                'package_tag_path': html_output_folder}

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
            template_file = open(template_path)
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
                tmpl = open('%s.in' % required_index)
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

    def build_html(self, package_name):
        package_info = self.packages[package_name]
        package_info['tag_html'] = {}
        package_path = package_info['path']
        main_branch = package_info['main_branch']
        package_tags = list(reversed(package_info['tags']))
        if self.options.max_tags and \
           len(package_tags) > self.options.max_tags:
            package_tags = package_tags[:self.options.max_tags]
        tags = [main_branch] + package_tags

        for tag in tags:
            if tag == main_branch:
                target_name = package_name
            else:
                target_name = f'{package_name}-{tag}'
            html_path = os.path.join(self.options.htmldir, target_name)

            if os.path.isfile(os.path.join(html_path, 'index.html')) and \
               tag != main_branch:
                # Documentation has been built already, don't do any more work
                LOG.info(f'{package_name} tag {tag} done already, skipping.')
                package_info['tag_html'][tag] = html_path
                continue

            self.rcs.checkout_tag(package_info['url'], tag, package_path)

            doc_folder = None
            for folder_name in self.options.docs_folders:
                doc_candidate = os.path.join(package_path, folder_name)
                if os.path.isdir(doc_candidate) and \
                   os.path.isfile(os.path.join(doc_candidate, 'conf.py')):
                    doc_folder = doc_candidate
                    break

            if doc_folder is None:
                LOG.info(f'{package_name} at tag {tag} contains no '
                         'Sphinx docs folder, skipping.')
                continue

            build_folder = os.path.join(doc_folder, '.build')
            shutil.rmtree(build_folder, ignore_errors=True)
            os.mkdir(build_folder)
            html_output_folder = os.path.join(build_folder, 'html')
            old_sys_path = sys.path

            req = pkg_resources.Requirement.parse(package_name)
            distribution = pkg_resources.working_set.find(req)
            distribution.activate()

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
                LOG.info(f'Building Sphinx docs for {package_name} {tag}')
                builder.build(True, None)
                warnings = getattr(builder, '_warncount', 0)
                if warnings:
                    LOG.info(f'Sphinx shows {warnings} warnings/errors.')

                # Copy HTML to its final resting place
                if os.path.isdir(html_path):
                    # This will only ever be true for the main branch, which
                    # is always regenerated.
                    shutil.rmtree(html_path)

                shutil.copytree(html_output_folder, html_path)

                package_info['tag_html'][tag] = html_path

            except pkg_resources.DistributionNotFound as e:
                msg = 'Building Sphinx docs for %s %s failed: missing \
                       dependency %s'
                LOG.error(msg % (package_name, tag, str(e)))
            except Exception as e:
                msg = 'Building Sphinx docs for %s %s failed: %s'
                LOG.error(msg % (package_name, tag, str(e)))
            finally:
                sys.path = old_sys_path


LINK_RST = """\
* `%(package_name)s %(package_tag)s <%(package_tag_path)s/index.html>`_\
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
