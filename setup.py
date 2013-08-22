#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup
from distutils.command.install_data import install_data
import glob
import os
import platform
import pwd
import subprocess
import sys

# Get current Python version
python_version = platform.python_version_tuple()

# Setup the default install prefix
prefix = sys.prefix

# Check our python is version 2.6 or higher
if python_version[0] >= 2 and python_version[1] >= 6:
    ## Set file location prefix accordingly
    prefix = '/usr/local'

# Get the install prefix if one is specified from the command line
for arg in sys.argv:
    if arg.startswith('--prefix='):
        prefix = arg[9:]
        prefix = os.path.expandvars(prefix)

user = os.getenv('SUDO_USER')

setup(
    name='wii-monitor',
    version='0.1',
    description='Script that configures wii controller when it detects a game running',
    author='Seppo Erviala',
    author_email='seppo.erviala@iki.fi',
    url='https://github.com/inopia/wii-monitor/',
    scripts=['scripts/wii-monitor'],
    keywords = ['wii', 'wiimote', 'joystick', 'gamepad', 'cwiid', 'wminput'],
    license="GPLv2 or later",

    requires=['pynotify', 'psutil'],
    data_files = [('share/icons/hicolor/16x16/devices', glob.glob('data/icons/hicolor/16x16/devices/*')),
                  ('share/icons/hicolor/22x22/devices', glob.glob('data/icons/hicolor/22x22/devices/*')),
                  ('share/icons/hicolor/32x32/devices', glob.glob('data/icons/hicolor/32x32/devices/*')),
                  ('share/icons/hicolor/48x48/devices', glob.glob('data/icons/hicolor/48x48/devices/*')),
                  ('share/icons/hicolor/scalable/devices', glob.glob('data/icons/hicolor/scalable/devices/*')),
                  ('share/icons/hicolor/24x24/status', glob.glob('data/icons/hicolor/24x24/status/*')),
                  ('share/icons/hicolor/scalable/mimetypes', glob.glob('data/icons/hicolor/scalable/mimetypes/*')),
                  ('/home/%s/.cwiid/' % user, glob.glob('cwiid/game-mappings.json')),
                  ('/home/%s/.cwiid/plugins' % user, glob.glob('cwiid/plugins/*')),
                  ('/home/%s/.cwiid/wminput' % user, glob.glob('cwiid/wminput/*'))]
                  # after installing icons
    )
# Need to call gtk-update-icon-cache -f -t $(datadir)/icons/hicolor

subprocess.call(["gtk-update-icon-cache", "-f", "-t", prefix + "/share/icons/hicolor"])
subprocess.call(["chown", "%s:%s" % (user, user), '/home/%s/.cwiid/' % user, '-R'])
