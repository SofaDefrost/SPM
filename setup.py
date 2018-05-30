from setuptools import setup

setup(name='sofa-spm',
      version='1.0.6',
      description='A package manager for the simulation framework called Sofa (https://www.sofa-framework.org)',
      url='https://github.com/SofaDefrost/SPM',
      author='Damien Marchal',
      author_email='damien.marchal@univ-lille1.fr',
      license='GPL',
      scripts=['sofa-spm.py'],
      packages=["spm"],
      package_data={'spm' : ['spm/recipes/*']},
      install_requires=['mu-repo', 'GitPython', 'requests', 'appdirs'],
      include_package_data=True,
      zip_safe=True)
