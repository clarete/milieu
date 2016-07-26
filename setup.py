# -*- coding: utf-8 -*-
# milieu - Environment variables manager
#
# Copyright (c) 2013-2016  Lincoln Clarete <lincoln@clarete.li>
# Copyright (c) 2013  Yipit, Inc <coders@yipit.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import Command, setup, find_packages

import io
import ast
import os
import pkg_resources
import re
import shlex
import subprocess

import lib2to3.fixer_base
import lib2to3.pgen2.driver
import lib2to3.pgen2.token
import lib2to3.pygram
import lib2to3.pytree
import lib2to3.refactor


PACKAGE = 'milieu'


class VersionFinder(ast.NodeVisitor):
    """Reads the value of the  variable __version__ of an AST tree.

    Take a look in the `read_version()` function below. It uses this
    class with the parsed AST tree from PACKAGE/version.py instead of
    trying to read that dynamically.
    """
    def __init__(self):
        self.version = None

    def visit_Assign(self, node):
        if node.targets[0].id == '__version__':
            self.version = node.value.s


def read_version():
    """Read version from package/version.py without loading any files"""
    finder = VersionFinder()
    finder.visit(ast.parse(local_file(PACKAGE, 'version.py')))
    return finder.version


class FixSetup(lib2to3.fixer_base.BaseFix):
    "lib2to3 will read this class as the `setup` fixer because we're in setup.py"

    _accept_type = lib2to3.pgen2.token.EQUAL

    def match(self, node):
        return (node.parent.children[0].value == '__version__' and
                node.parent.children[2].type == lib2to3.pgen2.token.STRING)

    def transform(self, node, results):
        node_value = node.parent.children[2]
        node_value.value = self.bump(self.options['command'], node_value.value)
        node_value.changed()

    def bump(self, cmd, val):
        val = val.replace('"', '').replace("'", '')
        major, minor, patch = val.split('.')
        if cmd.major:
            major = int(major) + 1
        if cmd.minor:
            minor = int(minor) + 1
        if cmd.patch:
            patch = int(patch) + 1
        return "'{}.{}.{}'".format(major, minor, patch)


class Bump(Command):
    description = 'Bump different parts of the version number'
    user_options = [
        ('patch', 'p', 'Bump the patch part of the version number'),
        ('minor', 'm', 'Bump the minor part of the version number'),
        ('major', 'M', 'Bump the major part of the version number'),
    ]

    boolean_options = ['patch', 'minor', 'major']

    def initialize_options(self):
        self.patch = False
        self.minor = False
        self.major = False

    def finalize_options(self):
        pass

    def run(self):
        if not any([self.patch, self.minor, self.major]):
            print '>> Nothing to do'
        else:
            driver = lib2to3.pgen2.driver.Driver(
                lib2to3.pygram.python_grammar,
                convert=lib2to3.pytree.convert)
            refactor = lib2to3.refactor.RefactoringTool(
                ['setup'], {'command': self})
            parsed = driver.parse_string(local_file(PACKAGE, 'version.py'))
            refactor.refactor_tree(parsed, 'version')
            io.open(local_path(PACKAGE, 'version.py'), 'w').write(unicode(parsed))
            self.git_commit()

    def git_commit(self):
        version = read_version()
        commands = []
        commands.append('git add {}'.format(local_path(PACKAGE, 'version.py')))
        commands.append('git commit -m "New release: {}"'.format(version))
        commands.append('git tag {}'.format(version))
        for cmd in commands:
            if subprocess.call(shlex.split(cmd)) != 0:
                break


def parse_requirements():
    """Rudimentary parser for the `requirements.txt` file

    We just want to separate regular packages from links to pass them to the
    `install_requires` and `dependency_links` params of the `setup()`
    function properly.
    """
    try:
        requirements = \
            map(str.strip, local_file('requirements.txt').splitlines())
    except IOError:
        raise RuntimeError("Couldn't find the `requirements.txt' file :(")

    links = []
    pkgs = []
    for req in requirements:
        if not req:
            continue
        if 'http:' in req or 'https:' in req:
            links.append(req)
            name, version = re.findall("\#egg=([^\-]+)-(.+$)", req)[0]
            pkgs.append('{0}=={1}'.format(name, version))
        else:
            pkgs.append(req)

    return pkgs, links


local_path = lambda *f: os.path.join(os.path.dirname(__file__), *f)
local_file = lambda *f: open(local_path(*f)).read()

install_requires, dependency_links = parse_requirements()


if __name__ == '__main__':
    setup(
        name=PACKAGE,
        version=read_version(),
        description=(
            "A helping hand to manage your settings among "
            "different environments"),
        long_description=local_file('README.md'),
        author=u'Lincoln de Sousa',
        author_email=u'lincoln@clarete.li',
        url='https://github.com/clarete/milieu',
        packages=find_packages(exclude=['*tests*']),
        install_requires=install_requires,
        dependency_links=dependency_links,
        cmdclass={'bump': Bump},
    )
