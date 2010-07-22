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
""" Recipe for creating automated doc builder scripts
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
                      , help='Root folder for HTML output (default: $working-directory/html)'
                      ),
  optparse.make_option( '-t'
                      , '--trunk-only'
                      , action='store_true'
                      , dest='trunk_only'
                      , help='Only build trunk documentation? (default: False)'
                      , default=False
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

        if not self.options.urls:
            parser.error('Please provide package SVN URLs')

        if not self.options.workingdir:
            parser.error('Please provide an workingdir directory path')

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

    def run(self):
        for url in self.options.urls:
            package_name, tag_names = self.checkout_or_update(url)
            tag_data = self.build_html(package_name, tag_names)

            for tag_name, html_output_folder in tag_data.items():
                self.link_html(package_name, tag_name, html_output_folder)

            if not self.options.trunk_only:
                self.create_index_html(package_name, tag_names)

        self.create_main_index()

    def _do_shell_command(self, cmd, fromwhere=None):
        cwd = os.getcwd()
        if fromwhere:
            os.chdir(fromwhere)
        status, output = commands.getstatusoutput(cmd)
        os.chdir(cwd)
        if status:
            print '%s: %s' % (cmd, output)
        return output

    def create_main_index(self):
        tags_list = []
        
        for name in os.listdir(self.options.htmldir):
            path = os.path.join(self.options.htmldir, name)
            if os.path.isdir(path) or os.path.islink(path):
                tags_list.append(LINK_HTML % {'name': name})

        index_file = open(os.path.join(self.options.htmldir, 'index.html'), 'w')
        index_file.write( INDEX_HTML % { 'name': ''
                                       , 'tags_text': '\n'.join(tags_list)
                                       } )
        index_file.close()

    def create_index_html(self, package_name, tag_names):
        html_root_path = os.path.join(self.options.htmldir, package_name)
        if not os.path.isdir(html_root_path):
            os.mkdir(html_root_path)
        tags_list = []

        for tag_name in tag_names:
            html_link = os.path.join(html_root_path, tag_name)
            if os.path.exists(html_link):
                tag_txt = LINK_HTML % {'name': tag_name}
            else:
                tag_txt = NOLINK_HTML % tag_name
            tags_list.append(tag_txt)
        
        index_file = open(os.path.join(html_root_path, 'index.html'), 'w')
        index_file.write( INDEX_HTML % { 'name': package_name
                                       , 'tags_text': '\n'.join(tags_list)
                                       } )
        index_file.close()

    def build_html(self, package_name, tag_names):
        if 'trunk' not in tag_names:
            tag_names.append('trunk')
        tag_data = {}.fromkeys(tag_names)

        package_path = os.path.join(self.options.workingdir, package_name)

        for tag in tag_names:
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
            tag_data[tag] = html_output_folder
            sys.path = old_sys_path

        return tag_data

    def link_html(self, package_name, tag_name, html_output_folder):
        if not html_output_folder:
            return

        html_root_path = os.path.join(self.options.htmldir, package_name)

        if not self.options.trunk_only:
            if not os.path.isdir(html_root_path):
                os.mkdir(html_root_path)
            html_link_path = os.path.join(html_root_path, tag_name)
        else:
            html_link_path = html_root_path

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

        if self.options.trunk_only:
            return (package_name, [])

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

        return (package_name, tag_names)
        
INDEX_HTML = """\
<html>
  <head>
    <title>%(name)s documentation</title>
  </head>
  <body>
    <h1>%(name)s dumentation</h1>
    <ul>
%(tags_text)s
    </ul>
  </body>
</html>
"""
LINK_HTML = '<li><a href="./%(name)s/index.html" alt="%(name)s">%(name)s</a></li>'
NOLINK_HTML = '<li>%s (no Sphinx documentation)</li>'

def run_builder():
    builder = DocsBuilder()
    builder.run()

class BuildoutScript:

    def __init__(self, buildout, name, options):
        import zc.buildout
        import zc.recipe.egg

        script_name = options.get('script', name)

        if not options.get('source'):
            raise zc.buildout.UserError('Missing parameter: source (SVN URLs).')

        if not options.get('working-directory'):
            parts = buildout['buildout']['parts-directory']
            options['working-directory'] = os.path.join(parts, script_name)
            if not os.path.isdir(options['working-directory']):
                os.mkdir(options['working-directory'])
        else:
            if not os.path.isdir(options['working-directory']):
                msg = 'Working directory "%s" does not exist!' % (
                                                    options['working-directory'])
                raise zc.buildout.UserError(msg)

        options['script'] = os.path.join( buildout['buildout']['bin-directory']
                                        , script_name
                                        )
        python = options.get('python', buildout['buildout']['python'])
        options['executable'] = buildout[python]['executable']
        options['bin-directory'] = buildout['buildout']['bin-directory']

        self.buildout = buildout
        self.name = name
        self.options = options
        self.egg = zc.recipe.egg.Egg(self.buildout, self.name, self.options)

    def install(self):
        import zc.buildout

        reqs, ws = self.egg.working_set([self.options['recipe']])

        script_args = []
        script_args.extend(['-w', self.options['working-directory'].strip()])
        for url in [x.strip() for x in self.options['source'].split()]:
            script_args.extend(['-s', url])
        if self.options.get('html-directory'):
            script_args.extend(['-o', self.options['html-directory'].strip()])
        if self.options.get('docs-directory'):
            df = [x.strip() for x in self.options['docs-directory'].split()]
            for doc_folder in df:
                script_args.extend(['--docs-directory', doc_folder])
        if self.options.get('trunk-directory'):
            script_args.extend( [ '--trunk-directory'
                                , self.options['trunk-directory']
                                ] )
        if self.options.get('tags-directory'):
            script_args.extend( [ '--tags-directory'
                                , self.options['tags-directory']
                                ] )
        if self.options.get('trunk-only'):
            script_args.extend(['-t', self.options['trunk-only']])
                
        init_code = 'import sys; sys.argv.extend(%s)' % str(script_args)

        arg = [(self.options['script'], self.options['recipe'], 'run_builder')]
        return zc.buildout.easy_install.scripts( arg
                                               , ws
                                               , self.options['executable']
                                               , self.options['bin-directory']
                                               , initialization=init_code
                                               )

    update = install

