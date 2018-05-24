from setuptools import setup

setup(name='sofa_spm',
      version='1.0',
      description='A package manager for the simulation framework called Sofa (https://www.sofa-framework.org)',
      url='https://github.com/SofaDefrost/SPM',
      author='Damien Marchal',
      author_email='damien.marchal@univ-lille1.fr',
      license='GPL',
      scripts=['spm/sofa-spm.py'],
      install_requires=['mu-repo', 'GitPython'],
      zip_safe=True)
