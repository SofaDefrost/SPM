## SPM: Sofa Package Manager.
If like me your are tired of searching which Sofa component is in which plugin and where this 
plugin is available and of cloning manually a lot of git repository maybe you should try SPM .
SPM is a small tool to search from plugins or components & install them (including their dependencies) 
with as few as possible steps. 

### Install
Before using spm you first install two python dependencies:
```console
   pip install GitPython
   pip install mu-repo
```
You also need to have configured your gitlab/github account to authenticate with ssh key.

### Usage
To get a list of the available plugins you can try:
```console
dmarchal@dmarchal-Precision-7520:~/projects/DEFROST/dev/spm/test$ ../src/spm.py list
 Defrost:
      ModelOrderReduction.sp
      SoftRobots.Inverse.sp
      STLIB.sp
      DefrostAllPlugins.sp
      BeamAdapter.sp
      SoftRobots.sp
      sofa-shells.sp
  Consortium:
      HighOrder.sp
      SofaQtQuick.sp
  Mimesis:
      DepthSense.sp
      Meshless.sp
      SofaOR.sp
```

To search for a specific plugins which contains specific components you could try:
```console
dmarchal@dmarchal-Precision-7520:~/projects/DEFROST/dev/spm/test$ ../src/spm.py search CableActuator
The Sofa Package Manager
- searching for 'CableActuator' in 7 plugins descriptions. Found:
  SoftRobots                      A plugin dedicated to SoftRobotics.
```

If not matches are found, an approximated search is done which should provide you suggestions as in:
```console
dmarchal@dmarchal-Precision-7520:~/projects/DEFROST/dev/spm/test$ ../src/spm.py search CableActutor
The Sofa Package Manager
- searching for 'CableActutor' in 7 plugins descriptions. No exact match...but I found:
  CableActuator                    (get details by typing: 'spm search CableActuator')
```

Finally, when you have found the plugins you want to install you can type:
```console
dmarchal@dmarchal-Precision-7520:~/projects/DEFROST/dev/spm/test$ ../src/spm.py install SofaQtQuick SoftRobots.Inverse 
The Sofa Package Manager
- instal list is ['SofaQtQuick', 'STLIB', 'SoftRobots', 'SoftRobots.Inverse']
 - installing 'SofaQtQuick' (destination path ./)
   cloning from: git@github.com:sofa-framework/SofaQtQuick.git
Repository: ./SofaQtQuick skipped, already registered
 - installing 'STLIB' (destination path ./)
   cloning from: git@github.com:SofaDefrost/STLIB.git
Repository: ./STLIB skipped, already registered
 - installing 'SoftRobots' (destination path ./)
   cloning from: git@github.com:SofaDefrost/SoftRobots.git
Repository: ./SoftRobots skipped, already registered
 - installing 'SoftRobots.Inverse' (destination path ./)
   cloning from: git@github.com:SofaDefrost/SoftRobots.git
Repository: ./SoftRobots.Inverse skipped, already registered
 - building CMakeLists.txt for: ./
 - scanning directory ./ for plugins.
 - scanning directory ./ for plugins to generate mu-repo.
```

The 'install' command of spm will install the plugins but also all their dependencies.
The source for installation is the git official repository, these official repositories are renamed as 
"upstream" remotes. The install command also:
- generates a dependency friendly ordered CMakeLists.txt for direct integration in you SOFA_EXTERNAL_PLUGINS_DIRECTORY. 
- configure the plugins repository to be used with mu-repo (http://fabioz.github.io/mu-repo/).

## How to contribute & TODO
- Reports problems,
- Make PR to add your plugins into the plugin database. 
- Make PR to add a system to automatically update a plugin entry from the actual content of a plugin so that it is 
  always synchronized. 
- Make suggestions on how to handle stuff like other remotes, binary distribution of plugins, private plugin management...
