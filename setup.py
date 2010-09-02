import os
from setuptools import setup, find_packages

def read_file(filename):
    path = os.path.abspath(os.path.dirname(__file__))
    filepath = os.path.join(path, filename)
    try:
        return open(filepath).read()
    except IOError:
        return ''

setup(name='pollit',
    version = __import__('pollit').get_version().replace(' ', '-'),
    description='An application for creating polls and tabulating results',
    long_description = read_file('README'),
    author='Jose Soares',
    author_email='jsoares@washingtontimes.com',
    url='http://opensource.washingtontimes.com/projects/pollit/',
    packages = find_packages(),
    include_package_data = True,
    install_requires=read_file('requirements.txt'),
    classifiers=['Framework :: Django',
        'License :: OSI Approved :: Apache Software License',
        'Development Status :: 4 - Beta',
        'Environment :: Other Environment',
        'Programming Language :: Python',
    ],
)
