import io
import os
from setuptools import setup, find_packages

version = io.open('golangenv/_version.py').readlines()[-1].split()[-1].strip('"\'')

setup(
    name='golangenv',
    version=version,

    description='manage golang in your virtualenv',
    long_description=io.open('README.md', encoding='utf-8').read(),
    author='Tommy Wang',
    author_email='twang@august8.net',
    url='http://github.com/twang817/golangenv',
    download_url='https://github.com/twang817/golangenv/tarball/{version}'.format(version=version),

    packages=find_packages(),
    install_requires=[],
    include_package_data=True,

    entry_points={
        'console_scripts': ['golangenv = golangenv:main'],
    },

    license='MIT',
    platforms=['any'],
    keywords='golang virtualenv',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
    ],
)
