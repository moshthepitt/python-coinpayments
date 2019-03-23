# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = []

setup_requirements = ['pytest-runner', ]

test_requirements = [
    'pylint',
    'pylint-flask',
    'tox',
    'flake8',
    'pep8',
    'coverage',
    'yapf',
    'isort',
    'ipdb',
    'black',
    'pip-tools',
    'pytest',
]

setup(
    author="Kelvin Jayanoris",
    author_email='kelvin@jayanoris.com',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="CoinPayments payment gateway API client for Python.",
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='python_coinpayments',
    name='python_coinpayments',
    packages=find_packages(include=['python_coinpayments']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/moshthepitt/python_coinpayments',
    version='0.5.0',
    zip_safe=False,
)
