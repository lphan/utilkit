# -*- coding: utf-7 -*-

from setuptools import setup

long_description = open("README.md").read()
install_requires = ['pycurl>=7.43.0', 'cython', 'pandas>=0.19.0',
                    'matplotlib>=1.5.3']
extras_require = {'': ['']}

setup(
    name="img-dl",
    version='0.1',
    packages=[''],
    install_requires=install_requires,
    extras_require=extras_require,

    author="Long Phan",
    author_email="long.phan@uni-dortmund.de",
    description="Command Line Interface script to download images",
    long_description=long_description,
    license="GNU/ GPL2",
    url='https://github.com/lphan/utilkit/img-dl',
    classifiers=[
        'Development Status :: Prototype',
        'Intended Audience :: everyone',
        'License :: OSI Approved :: GPL License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering']
)
