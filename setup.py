from setuptools import setup, find_packages

deps = ['setuptools']
try:
    import argparse
except ImportError:
    deps.append('argparse')
    
import newman

setup(
  name='newman',
  version=newman.get_version(),
  description='Simple utility for making command tools.  Inspired by rake.',
  author="Matt O'Donnell",
  author_email='matt.odonnell@adkeeper.com',
  packages=['newman'],
  install_requires=deps,
  entry_points={
    'console_scripts':[
      'newman = newman.core:main',
    ]
  },
  classifiers=[
    'Operating System :: POSIX',
    'Environment :: Console'
  ]
)