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

import os
import pkg_resources

import dataflake.docbuilder
from dataflake.docbuilder.builder import DocsBuilder

INITIALIZATION = """\
import sys
sys.argv.extend(%(script_arguments)s)
"""


def run_builder():
    builder = DocsBuilder()
    builder.run()


class BuildoutScript:

    def __init__(self, buildout, name, options):
        import zc.buildout
        import zc.recipe.egg

        script_name = options.get('script', name)
        if not options.get('sources'):
            options['sources'] = ''

        if ( not options.get('sources') and 
             not options.get('z3csphinx-output-directory') ):
            raise zc.buildout.UserError('Missing parameter: source (SVN URLs).')

        z3csphinx_doc_root = options.get('z3csphinx-output-directory')
        if z3csphinx_doc_root and not os.path.isdir(z3csphinx_doc_root):
            msg = 'z3c.recipe.sphinxdoc output folder %s does not exist'
            raise zc.buildout.UserError(msg % z3csphinx_doc_root)

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
        self.sw_path, ignored = os.path.split(dataflake.docbuilder.__file__)

    def install(self):
        import zc.buildout

        reqs, ws = self.egg.working_set([self.options['recipe']])
        script_args = []

        script_args.extend(['-w', self.options['working-directory'].strip()])

        for url in [x.strip() for x in self.options['sources'].split()]:
            script_args.extend(['-s', url])

        if self.options.get('groupings'):
            group_specs = self.options['groupings'].split('\n')
            for group_spec in [x.strip() for x in group_specs if x]:
                script_args.extend(['-g', group_spec])

        if self.options.get('output-directory'):
            script_args.extend(['-o', self.options['output-directory'].strip()])

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

        if self.options.get('index-template'):
            index_template = self.options['index-template']
        else:
            index_template = os.path.join(self.sw_path, 'index_template')
        script_args.extend(['--index-template', index_template])

        if self.options.get('index-name'):
            script_args.extend(['--index-name', self.options['index-name']])

        if self.options.get('z3csphinx-output-directory'):
            script_args.extend( [ '--z3csphinx-output-directory'
                                , self.options.get('z3csphinx-output-directory')
                                ] )

        if self.options.get('fallback-css'):
            fallback_css = self.options['fallback-css']
        else:
            template_dir = os.path.join(self.sw_path, 'index_template')
            fallback_css = os.path.join(template_dir, '_static', 'python.css')
        script_args.extend([ '--fallback-css', fallback_css])

        init_code = INITIALIZATION % { 'script_arguments': str(script_args)
                                     , 'bindir': self.options['bin-directory']
                                     }

        arg = [(self.options['script'], self.options['recipe'], 'run_builder')]
        return zc.buildout.easy_install.scripts( arg
                                               , ws
                                               , self.options['executable']
                                               , self.options['bin-directory']
                                               , initialization=init_code
                                               )

    update = install

