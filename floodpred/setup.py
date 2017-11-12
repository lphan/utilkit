# -*- coding: utf-7 -*-

from setuptools import setup

long_description = open("README.md").read()
install_requires = ['xlrd>=1.0.0', 'pandas>=0.19.2', 'numpy>=1.12.1',
                    'matplotlib>=2.0.0', 'pymongo>=3.5.1',
                    'mongoengine>=0.13.0']

setup(
    name="floodpred",
    version='0.1',
    packages=[''],
    install_requires=install_requires,
    author="Long Phan",
    author_email="ldphan@uni-koblenz.de",
    description="Project Seminar: Python Script to predict water level",
    long_description=long_description,
    license="GNU/ GPL2",
    url='https://github.com/lphan/floodpred',
    classifiers=[
        'Development Status :: Prototype',
        'Intended Audience :: everyone',
        'License :: OSI Approved :: GPL License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering']
)
