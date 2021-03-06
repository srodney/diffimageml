from setuptools import setup
import os,glob,warnings,sys,fnmatch,subprocess
from distutils.core import setup
import numpy.distutils.misc_util


if sys.version_info < (3,0):
    sys.exit('Sorry, Python 2 is not supported')


AUTHOR = 'SC-SN research team'
AUTHOR_EMAIL = 'srodney@sc.edu'
VERSION = '0.0.1'
LICENSE = ''
URL = ''



def recursive_glob(basedir, pattern):
    matches = []
    for root, dirnames, filenames in os.walk(basedir):
        for filename in fnmatch.filter(filenames, pattern):
            matches.append(os.path.join(root, filename))
    return matches

PACKAGENAME='diffimageml'


# Add the project-global data
#data_files = []
#for dataFolderName in ['test_data']:
#  pkgdatadir = os.path.join(PACKAGENAME, dataFolderName)
#  data_files.extend(recursive_glob(pkgdatadir, '*'))

#data_files = [f[len(PACKAGENAME)+1:] for f in data_files]


setup(
    name=PACKAGENAME,
    setup_requires='numpy',
    install_requires=['numpy','scipy','astropy', 'pytest-astropy','pyyaml',
                      'tensorflow>=2.4'],
    packages=[PACKAGENAME],
    version=VERSION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license=LICENSE,
    include_dirs=numpy.distutils.misc_util.get_numpy_include_dirs(),
    #package_data={PACKAGENAME:data_files},
    #include_package_data=True
)
