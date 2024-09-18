from distutils.core import setup

version = '0.1.0'

setup(
  name='crowd-api',
  packages=['crowd_api'],
  version=version,
  description='Python library for Atlassian Crowd',
  author='Matteo Cerutti',
  author_email='matteo.cerutti@hotmail.co.uk',
  url='https://github.com/m4ce/crowd-api-python',
  download_url='https://github.com/m4ce/crowd-api-python/tarball/%s' % (version,),
  keywords=['crowd'],
  classifiers=[],
  install_requires=["requests"]
)
