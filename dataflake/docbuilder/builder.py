##############################################################################
#
# Copyright (c) 2010 Jens Vagelpohl and Contributors. All Rights Reserved.
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

import commands
import optparse
import os
import pkg_resources
import shutil
from sphinx.application import Sphinx
import sys
import urlparse

OPTIONS = (
  optparse.make_option( '-s'
                      , '--source'
                      , action='append'
                      , dest='urls'
                      , help='SVN URL (can be used multiple times)'
                      ),
  optparse.make_option( '-g'
                      , '--grouping'
                      , action='append'
                      , dest='groupings'
                      , help='Package name to group name grouping, colon-separated'
                      ),
  optparse.make_option( '-w'
                      , '--working-directory'
                      , action='store'
                      , dest='workingdir'
                      , help='working directory for package checkouts'
                      ),
  optparse.make_option( '-o'
                      , '--output-directory'
                      , action='store'
                      , dest='htmldir'
                      , help='Root folder for HTML output and links (default: $working-directory/html)'
                      ),
  optparse.make_option( '-t'
                      , '--trunk-only'
                      , action='store_true'
                      , dest='trunk_only'
                      , help='Only build trunk documentation? (default: False)'
                      , default=False
                      ),
  optparse.make_option( '--index-template'
                      , action='store'
                      , dest='index_template'
                      , help='Optional filesystem path containing Sphinx files for the output directory'
                      ),
  optparse.make_option( '--index-name'
                      , action='store'
                      , dest='index_name'
                      , help='The index file name, without extension. Defaults to "index".'
                      , default='index'
                      ),
  optparse.make_option( '--docs-directory'
                      , action='append'
                      , dest='docs_folders'
                      , help='Sphinx documentation folder name (can be used multiple times, default: "doc" and "docs")'
                      , default=['doc', 'docs']
                      ),
  optparse.make_option( '--trunk-directory'
                      , action='store'
                      , dest='trunk_name'
                      , help='Development trunk container name (default: "trunk")'
                      , default='trunk'
                      ),
  optparse.make_option( '--tags-directory'
                      , action='store'
                      , dest='tags_name'
                      , help='Development tags container name (default: "tags")'
                      , default='tags'
                      ),
)


class DocsBuilder(object):
    
    def __init__(self):
        parser = optparse.OptionParser(option_list=OPTIONS)
        self.options, self.args = parser.parse_args()
        self.packages = {}
        self.group_map = {}

        if not self.options.urls:
            parser.error('Please provide package SVN URLs')

        if not self.options.workingdir:
            parser.error('Please provide a workingdir directory path')

        if not os.path.isdir(self.options.workingdir):
            msg = 'Output folder %s does not exist.' % self.options.workingdir
            parser.error(msg)

        if not self.options.htmldir:
            self.options.htmldir = os.path.join(self.options.workingdir, 'html')
            if not os.path.isdir(self.options.htmldir):
                os.mkdir(self.options.htmldir)
        elif not os.path.isdir(self.options.htmldir):
            msg = 'HTML output folder %s does not exist.' % self.options.htmldir
            parser.error(msg)

        for group_spec in self.options.groupings or []:
            package_name, group_name = [x.strip() for x in group_spec.split(':')]
            group_values = self.group_map.setdefault(group_name, [])
            group_values.append(package_name)

    def run(self):
        grouped = []
        [grouped.extend(x) for x in self.group_map.values()]
        for url in self.options.urls:
            package_name = self.checkout_or_update(url)
            if package_name not in grouped:
                group_values = self.group_map.setdefault('', [])
                group_values.append(package_name)
            self.build_html(package_name)
            self.link_html(package_name)

        if self.options.index_template:
            self.create_index_html()

    def _do_shell_command(self, cmd, fromwhere=None):
        cwd = os.getcwd()
        if fromwhere:
            os.chdir(fromwhere)
        status, output = commands.getstatusoutput(cmd)
        os.chdir(cwd)
        if status:
            print '%s: %s' % (cmd, output)
        return output

    def create_index_html(self):
        index_text = ''
        group_names = self.group_map.keys()
        group_names.sort(key=str.lower)
        output = { 'package': PACKAGE_RST
                 , 'link': LINK_RST
                 , 'nolink': NOLINK_RST
                 , 'groupheader': GROUPHEADER_RST
                 }

        for group_name in group_names:
            package_names = self.group_map.get(group_name)
            package_names.sort(key=str.lower)

            if group_name or (not group_name and len(group_names) > 1):
                group_name = group_name or 'Ungrouped'
                group_data = { 'group_name': group_name
                             , 'group_underline': '=' * len(group_name)
                             }
                index_text += output['groupheader'] % group_data

            for package_name in package_names:
                tags_list = []
                tag_names = self.packages[package_name].keys()
                tag_names.sort(key=str.lower)
                tag_names.reverse()

                for tag_name in tag_names:
                    html_output_folder = self.packages[package_name][tag_name]
                    tag_data = { 'package_name': package_name
                               , 'package_tag': tag_name
                               , 'package_tag_path': '%s-%s' % ( package_name
                                                               , tag_name
                                                               )
                               }
                    if tag_name == self.options.trunk_name:
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
                    p_data = { 'package_name': package_name
                             , 'package_output': '\n'.join(tags_list)
                             , 'package_name_underline': '_' * len(package_name)
                             }
                    index_text += output['package'] % p_data
        
        index_path = os.path.join( self.options.index_template
                                 , '%s.rst' % self.options.index_name
                                 )
        template_path = os.path.join( self.options.index_template
                                    , '%s.rst.in' % self.options.index_name
                                    )
        if os.path.isfile(template_path):
            template_file = open(template_path, 'r')
            template_text = template_file.read()
            template_file.close()
            index_text = '%s\n\n%s' % (template_text, index_text)

        index_file = open(index_path, 'w')
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

        dt = os.path.join(self.options.index_template, '_build', 'doctrees')
        builder = Sphinx( self.options.index_template
                        , self.options.index_template
                        , self.options.htmldir
                        , dt
                        , 'html'
                        , {}
                        , None
                        , warning=sys.stderr
                        , freshenv=False
                        , warningiserror=False
                        , tags=None
                        )
        builder.build(True, None)


    def build_html(self, package_name):
        package_path = os.path.join(self.options.workingdir, package_name)

        for tag in self.packages[package_name]:
            tag_folder = os.path.join(package_path, tag)
            doc_folder = None
            for folder_name in self.options.docs_folders:
                doc_candidate = os.path.join(tag_folder, folder_name)
                if os.path.isdir(doc_candidate):
                    doc_folder = doc_candidate
                    break

            if not doc_folder:
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
                    distributions.extend(pkg_resources.find_distributions(path))

            for distribution in distributions:
                distribution.activate()
                pkg_resources.working_set.add_entry(distribution.location)

            if not distributions:
                pkg_resources.working_set.add_entry(tag_folder)

            builder = Sphinx( doc_folder
                            , doc_folder
                            , html_output_folder
                            , os.path.join(build_folder, 'doctrees')
                            , 'html'
                            , {}
                            , None
                            , warning=sys.stderr
                            , freshenv=False
                            , warningiserror=False
                            , tags=None
                            )
            builder.build(True, None)
            self.packages[package_name][tag] = html_output_folder
            sys.path = old_sys_path

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
            os.symlink(html_output_folder, html_link_path)

    def checkout_or_update(self, package_url):
        parsed_url = list(urlparse.urlparse(package_url))
        package_name = [x for x in parsed_url[2].split('/') if x][-1]
        package_dir = os.path.join(self.options.workingdir, package_name)
        pythonpath = ':'.join(sys.path)
        self.packages[package_name] = {}

        if not os.path.isdir(package_dir):
            os.mkdir(package_dir)

        trunk_path = os.path.join(package_dir, self.options.trunk_name)
        if os.path.isdir(trunk_path):
            self._do_shell_command('svn up %s' % trunk_path)
        else:
            url_elements = parsed_url[:]
            url_elements[2] = os.path.join(parsed_url[2], self.options.trunk_name)
            cmd = 'svn co %s %s' % (urlparse.urlunparse(url_elements), trunk_path)
            self._do_shell_command(cmd)
        cmd = 'PYTHONPATH="%s" %s %s/setup.py egg_info' % (
                pythonpath, sys.executable, trunk_path)
        self._do_shell_command(cmd, fromwhere=trunk_path)
        self.packages[package_name][self.options.trunk_name] = None

        if not self.options.trunk_only:
            cmd = 'svn ls %s/%s' % (package_url, self.options.tags_name)
            tag_names = [x.replace('/', '') for x in 
                                    self._do_shell_command(cmd).split()]
            tag_names.sort()

            for tag in tag_names:
                tag_path = os.path.join(package_dir, tag)
                if not os.path.isdir(tag_path):
                    # We only check out; tags presumably do not change!
                    cmd = 'svn co %s/%s/%s %s' % (
                            package_url, self.options.tags_name, tag, tag_path)
                    self._do_shell_command(cmd)
                cmd = 'PYTHONPATH="%s" %s %s/setup.py egg_info' % (
                           pythonpath, sys.executable, tag_path)
                self._do_shell_command(cmd, fromwhere=tag_path)
                self.packages[package_name][tag] = None

        return package_name


LINK_RST = """\
* `%(package_name)s %(package_tag)s <./%(package_tag_path)s/index.html>`_\
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
