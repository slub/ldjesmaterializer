"""
A Python3 program that takes line-delimited JSON records and some arguments as input and materializes information from other records (stored in an elasticsearch index) into them.
"""

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='ldjesmaterializer',
      version='0.0.1',
      description='a Python3 program that takes line-delimited JSON records and some arguments as input and materializes information from other records (stored in an elasticsearch index) into them',
      url='https://github.com/slub/ldjesmaterializer',
      author='Bo Ferri',
      author_email='zazi@smiy.org',
      license="Apache 2.0",
      packages=[
          'ldjesmaterializer',
      ],
      package_dir={'ldjesmaterializer': 'ldjesmaterializer'},
      install_requires=[
          'argparse>=1.4.0',
          'elasticsearch>=6.3.0'
      ],
      entry_points={
          "console_scripts": ["ldjesmaterializer=ldjesmaterializer.ldjesmaterializer:run"]
      }
      )
