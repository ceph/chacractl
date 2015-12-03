import re

module_file = open("chacractl/__init__.py").read()
metadata = dict(re.findall("__([a-z]+)__\s*=\s*'([^']+)'", module_file))
long_description = open('README.rst').read()

from setuptools import setup, find_packages

setup(
    name = 'chacractl',
    description = 'client tool for a chacra service',
    packages = find_packages(),
    author = 'Alfredo Deza',
    author_email = 'alfredo [at] deza.pe',
    scripts = ['bin/chacractl'],
    install_requires = ['tambo>=0.1.0', 'requests'],
    version = metadata['version'],
    url = 'https://github.com/ceph/chacractl',
    license = "MIT",
    zip_safe = False,
    keywords = "http api chacra",
    long_description = long_description,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Utilities',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
    ],
    tests_require=[
        'pytest'
    ]
)
