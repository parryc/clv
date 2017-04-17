"""Setup.py file."""
from setuptools import setup

setup(
    name='command-line-vocab',
    version='1.0alpha',
    py_modules=['clv'],
    # http://python-packaging.readthedocs.io/en/latest/non-code-files.html
    include_package_data=True,
    install_requires=[
        'click'
    ],
    # use clv to call the script
    entry_points='''
        [console_scripts]
        clv=clv:cli
    ''',
)
