## SPM: Sofa Package Manager.
If like me your are tired of searching which Sofa component is in which plugin and where this 
plugin is available and of cloning manually git repository... try SPM to search from plugins & install them (including their dependencies):

** This software is in a very drafty state. Please don't use it unless you are willing to put you hand in the code. **

Search plugins that contains specific components by:
```console
dmarchal@dmarchal-Precision-7520:~/projects/DEFROST/dev/spm/test$ ../src/spm.py search CableActuator
The Sofa Package Manager
- searching for 'CableActuator' in 7 plugins descriptions. Found:
  SoftRobots                      A plugin dedicated to SoftRobotics.
```

If not match are found, an approximated search is done to provide you suggestion as in:
```console
dmarchal@dmarchal-Precision-7520:~/projects/DEFROST/dev/spm/test$ ../src/spm.py search CableActutor
The Sofa Package Manager
- searching for 'CableActutor' in 7 plugins descriptions. No exact match...but I found:
  CableActuator                    (get details by typing: 'spm search CableActuator')
```

When you have found the plugin you want to install you can simply ask for as in:
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
spm will install them as well as all their dependencies from their git official repository, 
configure the official repositories as "upstream" remote and generates a dependency friendly ordered 
CMakeLists.txt for direct integration in you SOFA_EXTERNAL_PLUGINS_DIRECTORY. 
spm will also configure mu-repo (http://fabioz.github.io/mu-repo/) so that it is already configure to handle all the 
plugins repositories. 

## How to contribute & TODO
- Reports problems,
- Make PR to add your plugins into the plugin database. 
- Make PR to add a system to automatically update a plugin entry from the actual content of a plugin so that it is 
  always synchronized. 
- Make suggestions on how to handle stuff like other remotes, binary distribution of plugins, private plugin management...
