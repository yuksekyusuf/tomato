#!/usr/bin/env python
import os
import subprocess
import ConfigParser
import urllib2
import zipfile
from StringIO import StringIO
try:
    from setuptools import setup
    from setuptools.command.install import install as _install
except ImportError:
    from distutils.core import setup
    from distutils.command.install import install as _install


def _get_mcr_binaries():
    """
    Downloads the binaries compiled by MATLAB Runtime Compiler from
    tomato_binaries
    """
    binary_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 'tomato', '_binaries')

    # find os, linux or macosx
    process_out = subprocess.check_output(['uname']).lower()
    if any(ss in process_out for ss in ['darwin', 'macosx']):
        sys_os = 'macosx'
    elif 'linux' in process_out:
        sys_os = 'linux'
    else:
        raise OSError("Unsupported OS.")

    # read configuration file
    config_file = os.path.join('config', 'binaries.cfg')
    config = ConfigParser.ConfigParser()
    config.optionxform = str
    config.read(config_file)

    # Download binaries
    for bin_name, bin_url in config.items(sys_os):
        fpath = os.path.join(binary_folder, bin_name)

        # download
        print("- Downloading binary: " + bin_url)
        response = urllib2.urlopen(bin_url)
        if fpath.endswith('.zip'):
            with zipfile.ZipFile(StringIO(response.read())) as z:
                z.extractall(os.path.dirname(fpath))
            fpath = os.path.splitext(fpath)[0] + '.app'
        else:
            with open(fpath, 'w+') as fp:
                fp.write(response.read())

        # make the binaries executalbe
        subprocess.call(["chmod -R +x " + fpath], shell=True)


class CustomInstall(_install):
    def run(self):
        # download the binaries
        self.execute(_get_mcr_binaries, (),
                     msg="Downloading the binaries from tomato_binaries.")

        # install tomato
        _install.run(self)

        # install requirements
        subprocess.call(["pip install -r requirements"], shell=True)


setup(name='tomato',
      version='0.1',
      author='Sertan Senturk',
      author_email='contact AT sertansenturk DOT com',
      license='agpl 3.0',
      description='Turkish-Ottoman Makam Music Analysis Toolbox',
      url='http://sertansenturk.com',
      packages=['tomato'],
      include_package_data=True,
      install_requires=[
      ],
      cmdclass={'install': CustomInstall},
      )
