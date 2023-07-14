from setuptools import find_packages, setup

# To use a consistent encoding
from codecs import open
from os import path

# The directory containing this file
HERE = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='growcube-client',
    version='1.0.0',
    description='A client for Growcube plant watering devices',
    long_description=long_description,
    long_description_content_type="text/markdown",    
    author='Jonny Bergdahl',
    license='MIT',
    packages=find_packages(include=["growcube_client"],where='src'),
    package_dir={"": "src"},
    setup_requires=['pytest-runner'],
    tests_require=['pytest==4.4.1'],
    test_suite='tests',    
)