#!/usr/bin/env python

import sys, os, subprocess, urllib2, zipfile

from setuptools import setup, find_packages

long_description = """
long description.
"""

start_dir = os.getcwd()

print "Checking for java"

try:
    java = subprocess.check_output('java -version', shell=True, stderr=subprocess.STDOUT)
except:
    print "Please install Java"
    sys.exit(0)

print "Checking for Ruby"

try:
    ruby = subprocess.check_output('ruby --version', shell=True, stderr=subprocess.STDOUT)
except:
    print "Please install Ruby"
    sys.exit(0)

print "Checking for Compass"

try:
    ruby = subprocess.check_output('compass --version', shell=True, stderr=subprocess.STDOUT)
except:
    print "Please install Compass"
    sys.exit(0)

try:
    os.mkdir('%s/sasquatch/bin' % start_dir)
    compiler = open('%s/sasquatch/bin/compiler.jar' % start_dir)
    compiler.close()
except:
    print "Downloading and unzipping closure compiler"
    u = urllib2.urlopen('http://closure-compiler.googlecode.com/files/compiler-20120710.zip')
    compiler = open(start_dir+'/sasquatch/bin/compiler-20120710.zip', 'w')
    compiler.write(u.read())
    compiler.close()
    zipf = zipfile.ZipFile('%s/sasquatch/bin/compiler-20120710.zip' % start_dir)
    zipf.extractall('%s/sasquatch/bin/' % start_dir)

setup(
    name='Sasquatch',
    version='1.1.1',
    description='All encompassing javascript framework, develop to build',
    long_description=long_description,
    author='Todd Cullen',
    author_email='todd@thoughtleadr.com',
    url='http://www.github.com',
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'sasquatch = sasquatch:main',
        ]
    },
    classifiers=[
          'Development Status :: 5 - Production/Stable',
    ],
    install_requires=[
        "django",
        "watchdog"
    ]

)
