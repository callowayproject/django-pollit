import os
from setuptools import setup
import pollit

version = pollit.__version__

try:
    f = open('README.rst')
    long_desc = f.read()
    f.close()
except:
    long_desc = ""

try:
    reqs = open('requirements.txt').read()
except:
    reqs = ''

setup(name='django-pollit',
    version = version,
    description='An application for creating polls and tabulating results',
    long_description = long_desc,
    author='Jose Soares',
    author_email='jose@linux.com',
    url='https://github.com/callowayproject/django-pollit',
    packages = find_packages(),
    include_package_data = True,
    install_requires = reqs,
    classifiers=['Framework :: Django',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
    ],
)
