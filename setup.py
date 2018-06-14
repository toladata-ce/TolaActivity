# -*- coding: utf-8 -*-
import os
from os.path import join, dirname, abspath
from setuptools import setup
from setuptools.command.install import install
import shutil

# Allow setup.py to be run from any path
os.chdir(os.path.normpath(join(abspath(__file__), os.pardir)))


class InstallCommand(install):
    def run(self):
        shutil.copy('__init__.py', '__init__.py.bak')
        shutil.copy('__init__.lib.py', '__init__.py')
        install.run(self)
        shutil.move('__init__.py.bak', '__init__.py')


with open(join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()


def load_requirements(load_dependency_links=False):
    lines = open(join(dirname(__file__), 'requirements/pkg.txt')).readlines()
    requirements = []
    for line in lines:
        if 'https' in line and load_dependency_links:
            requirements.append(line)
        elif 'https' not in line and not load_dependency_links:
            requirements.append(line)
    return requirements


setup(
    name='tola_activity',
    version='2.0',
    install_requires=load_requirements(),
    dependency_links=load_requirements(load_dependency_links=True),
    packages=[
        'factories',
        'formlibrary.migrations',
        'indicators.migrations',
        'search.migrations',
        'workflow',
        'workflow.migrations',
    ],
    py_modules=[
        '__init__',
        # formlibrary
        'formlibrary.admin',
        'formlibrary.models',
        # indicators
        'indicators.admin',
        'indicators.models',
        # search
        'search.admin',
        'search.apps',
        'search.exceptions',
        'search.models',
        'search.utils',
        'search.urls',
        'search.views',
        # search.management.commands
        'search.management.__init__',
        'search.management.commands.__init__',
        'search.management.commands.search-index',
        # tola
        'tola.__init__',
        'tola.track_sync',
        # tola.management.commands
        'tola.management.__init__',
        'tola.management.commands.__init__',
        'tola.management.commands.loadinitialdata',
        'tola.management.commands.synctrack',
    ],
    cmdclass={
        'install': InstallCommand,
    },
    description=('Workflow, visualizations and data services for managing NGO '
                 'projects and programs.'),
    url='https://github.com/toladata/TolaActivity',
    long_description=README,
    author=u'Rafael Muñoz Cárdenas',
    author_email='rafael@humanitec.com',
)
