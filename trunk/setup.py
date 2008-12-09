# -*- coding: utf-8 -*-
"""setup -- setuptools setup file for dyce.

$Author$
$Rev$
$Date$
"""

__author__ = "$Author$"
__revision__ = "$Rev$"
__version__ = "0.2"
__release__ = '.r'.join((__version__, __revision__[6:-2]))
__date__ = "$Date$"

import sys

try:
    import setuptools
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()

from setuptools import setup, find_packages

APP = []
DATA_FILES = []
APP_OPTIONS = {'argv_emulation': False,
               'optimize': '2',
               #'excludes': ['pkg_resources',],
               #'includes': ['pkg_resources',],
               }
INSTALL_REQUIRES=['ConfigObj>=4.5.3', 'yapps']
GUI_SCRIPTS = []
SCRIPTS = []
ZIP_SAFE = True

if sys.platform == 'darwin':
    extra_options = dict(
        setup_requires=['py2app',],
        app=APP,
        options={'py2app':APP_OPTIONS},
        )
elif sys.platform == 'win32':
    extra_options = dict(
        setup_requires=['py2exe'],
        app=APP,
        )
else:
    extra_options = dict(
        )

setup(
    name = "dyce",
    version = __version__,
    author = "David Eyk",

    package_dir = {'': 'src',},
    packages = find_packages('src'),

    include_package_data = True,
    exclude_package_data = {'src':['*.c', '*.h',  '*.pyx', '*.pxd', '*.g']},
    #data_files=['src/data',],

    entry_points={'gui_scripts': GUI_SCRIPTS,
                  'scripts': SCRIPTS},
    scripts=APP,

    install_requires=INSTALL_REQUIRES,
    zip_safe = ZIP_SAFE,

    test_suite = "nose.collector",
    **extra_options
    )

