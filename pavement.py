# -*- coding: utf-8 -*-
"""pavement -- setuptools setup file for dyce.

$Author$\n
$Rev: 9 $\n
$Date: 2008-12-09 19:39:47 -0600 (Tue, 09 Dec 2008) $
"""

__author__ = "$Author$"[9:-2]
__revision__ = "$Rev: 9 $"
__date__ = "$Date: 2008-12-09 19:39:47 -0600 (Tue, 09 Dec 2008) $"[7:-2]

__version__ = "0.3"
__release__ = '.r'.join((__version__, __revision__))

__description__ = "Randomizer toolkit, with custom dice expression parser."
__long_description__ = """Dyce is a toolkit for rolling dice. It's a friendly wrapper around python's random module.

Dyce also has a mini-language for expressing random number patterns, including common dice notation (i.e. "3d6+5" for rolling thre six-sided dice and adding 5 to the result), making it ideal for easily storing random number patterns in config files.
"""
__classifiers__ = ["Development Status :: 3 - Alpha",
                   "Environment :: Console",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: MIT License",
                   "Natural Language :: English",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python",
                   "Topic :: Games/Entertainment",
                   "Topic :: Games/Entertainment :: Role-Playing",
                   "Topic :: Software Development :: Libraries",]

import sys
import os

from paver.easy import *
import paver.doctools
from paver.setuputils import setup, find_package_data
from paver.setuputils import install_distutils_tasks

install_distutils_tasks()

from paver.virtual import bootstrap

__path__ = path(__file__).abspath().dirname()

INSTALL_REQUIRES=['ConfigObj>=4.5.3', 
                  ]
ZIP_SAFE = True

setup(
    name = "dyce",
    version = __version__,
    author = "David Eyk",
    author_email = "eykd@eykd.net",
    url = "http://code.google.com/p/dyce/",
    description = __description__,
    long_description = __long_description__,
    download_url = "http://code.google.com/p/dyce/downloads/list",
    classifiers = __classifiers__,

    package_dir = {'': 'src',},
    packages = find_package_data('src', 
                                 exclude=('*.py', '*.pyc', '*~', 
                                          '.*', '*.bak', '*.swp*'), 
                                 exclude_directories=('.*', '.svn', './lib', 
                                                      './build', './dist', 
                                                      'EGG-INFO', 
                                                      '*.egg-info'),),

    include_package_data = True,
    exclude_package_data = {'src':['*.c', '*.h',  '*.pyx', '*.pxd', '*.g']},
    #data_files=['src/data',],

    install_requires=INSTALL_REQUIRES,
    zip_safe = ZIP_SAFE,

    test_suite = "nose.collector",
    )

options(
    minilib=Bunch(
        extra_files=['doctools', 'virtual']
        ), 
    virtualenv=Bunch(
        script_name='bootstrap.py',
        packages_to_install=['epydoc',
                             'sphinx',
                             'nose',
                             'testoob',
                             'ipython',
                             'pyflakes',
                             ],
        paver_command_line="_virtualenv_post",
        ),
    also_install=Bunch(
        zip=[
            'http://www.voidspace.org.uk/cgi-bin/voidspace/downman.py?section=python&file=configobj-4.5.3.zip',
            ],
        tgz=[
            'http://theory.stanford.edu/~amitp/yapps/yapps2.1.1.tar.gz',
            ],
        ),
    )

def shv(cmd):
    """Execute the given shell command inside the virtual environment.
    """
    sh("source ./bin/activate; %s" % cmd)


def install_zipfile(pkg_url, use_ez_setup=False):
    tmp = path(os.tmpnam())
    tmp.mkdir()
    sh('pushd %s; curl -O "%s"; popd' % (tmp, pkg_url))
    sh('pushd %s; unzip "%s" -d %s; popd' % (tmp, tmp.files()[0], tmp))
    install_from_tmpdir(tmp, use_ez_setup)

def install_tarball(pkg_url, use_ez_setup=False, tar_options='xzvf'):
    tmp = path(os.tmpnam())
    tmp.mkdir()
    sh('pushd %s; curl -O "%s"; popd' % (tmp, pkg_url))
    sh('pushd %s; tar -%s "%s"; popd' % (tmp, tar_options, tmp.files()[0]))
    install_from_tmpdir(tmp, use_ez_setup)

def install_from_tmpdir(tmpdir, use_ez_setup=False):
    setup_dir = list(tmpdir.walkfiles("setup.py"))[0].dirname()
    if use_ez_setup:
        (__path__ / 'ez_setup.py').copy(setup_dir)
    shv('pushd %s; python setup.py install; popd' % (setup_dir,))
    tmpdir.rmtree()


@task
@needs('generate_setup', 'minilib')
def _virtualenv_post():
    """internal command (virtualenv post-install)
    """
    for zip in options.also_install.zip:
        install_zipfile(zip)

    for tgz in options.also_install.tgz:
        install_tarball(tgz)

    shv("python setup.py develop")


@task
@needs('bootstrap', 'mkdirs')
def env():
    """Set up the virtual environment.
    """
    sh('python bootstrap.py')


@task
def quickenv():
    """Make sure that we have a virtual environment available.
    """
    if not (__path__ / 'bin/activate').exists():
        env()


def rmFilePatterns(*patterns):
    """Remove all files under the current path with the given patterns.
    """
    for p in patterns:
        info("Removing %s" % p)
        for f in __path__.walkfiles(p, errors='warn'):
            if f.exists():
                msg = "Removing %s..." % f
                dry(msg, f.remove)


def rmDirPatterns(*patterns):
    """Remove all directories under the current path with the given patterns.
    """
    for p in patterns:
        info("Removing %s" % p)
        for d in __path__.walkdirs(p, errors='warn'):
            if d.exists():
                msg = "Removing %s..." % d
                dry(msg, d.rmtree)


@task
def changelog():
    """Update the changelog.
    """
    sh('svn up')
    sh('svn2cl --include-rev --include-actions')


@task
def ci():
    """Check in changes.
    """
    sh("touch CHANGES")
    sh("echo '' >> CHANGES")
    sh("cat CHANGES|cat ChangeLog > /tmp/out && mv /tmp/out ChangeLog")
    sh("svn ci --force-log -F ./CHANGES")
    sh("svn up")
    sh("svn2cl --include-rev --include-actions")
    sh("rm ./CHANGES")
    sh("touch CHANGES")


@task
def clean():
    """Clean up temporary files.
    """
    rmFilePatterns("*.pyc", "*~", "*.pyo", "*#", ".#*", "*.lock", "*.log*")


@task
def clean_docs():
    """Clean up generated documentation.
    """
    rmDirPatterns('docs')


@task
def clean_build():
    """Clean up generated build files.
    """
    rmDirPatterns('build')


@task
@needs('clean', 'clean_docs', 'clean_build')
def clean_env():
    """Clean up generated environment files.
    """
    rmDirPatterns('downloads', 'develop-eggs', 'parts', 
                  'bin', 'eggs', 'lib', 'include')
    rmFilePatterns('.installed.cfg',)


@task
@needs('clean', 'clean_build')
def clean_dist():
    """Clean up distribution files.
    """
    rmDirPatterns('dist')


@task
@needs('quickenv')
def dcalc():
    shv('yapps2 ./src/dyce/dcalc.g ./src/dyce/dcalc.py')

@task
@needs('quickenv', 'clean_docs', 'mkdirs')
def docs():
    """Generate documentation.
    """
    shv('epydoc -v --config epydoc.config')

@task
@needs('quickenv')
@consume_args
def easy_install():
    """Run easy_install on the given args in the virtualenv.
    """
    args = options.args
    shv('easy_install %s' % ' '.join(args))

@task
def mkdirs():
    """Make directories.
    """
    for p in ("docs", "docs/html", "docs/html/api",):
        p = __path__ / p
        if not p.exists():
            p.makedirs()
    


@task
@needs('quickenv')
def prepare_dist():
    """Prepare a distribution for release.
    """
    shv('python setup.py setopt -c egg_info -o tag_build -r')
    shv('python setup.py setopt -c egg_info -o tag_svn_revision -r')


@task
@needs('prepare_dist', 'upload_docs')
def release_dist():
    """Release a distribution.
    """
    shv('python setup.py register sdist bdist_egg upload')
    shv('python ./googlecode_upload.py --config-dir=~/.subversion/auth'
        '--summary=`pwd|sed -E sN/.+/NN` --project=Owyl --labels=`pwd|'
        'sed -E sN/.+/NN` `ls dist`')

@task
@needs('docs', 'generate_setup', 'minilib')
def sdist():
    """Create a source distribution (tarball, zip file, etc.)
    """
    pass

@task
@needs('quickenv')
def test():
    """Run tests in nose.
    """
    shv('nosetests -vxds')

