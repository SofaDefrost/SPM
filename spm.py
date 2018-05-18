#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Contributors: damien.marchal@univ-lille.fr
# Copyright CNRS 2018
import os
import re
import sys
import json
import shutil
import difflib
import textwrap
import subprocess
from git import Repo

dbpath = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),"recipes/"))

def loadPluginsEntries(dbpath):
        ### Import the database 
        allfilenames = [] 
        for (basepath, dirnames, filenames) in os.walk(dbpath):
                for f in filenames:
                        absname = os.path.join(basepath, f)		
                        allfilenames.append((f, absname))
        return allfilenames

def loadPluginDesc(dbpath, pluginname):
        for sd in os.listdir(dbpath):               
                path = os.path.join(os.path.join(dbpath, sd), pluginname+".sp")
                if os.path.exists(path):        
                        return json.loads(open(path).read())
        return None
        
def searchInPluginsEntries(pluginsname, query):
        matches = []
        closematches = []
        allwords = []
        for (name, path) in pluginsname:
                try:
                        plugin = json.loads(open(path).read())
                except:
                        print("Unable to process package: "+str(path))
                else:        
                        if re.search(query, plugin["package_name"]):
                                matches.append((name, path, plugin))               
                        elif re.search(query, plugin["description"]):
                                matches.append((name, path, plugin))               
                        elif re.search(query, str(plugin["components"])):
                                matches.append((name, path, plugin))               
                        elif re.search(query, str(plugin["prefabs"])):
                                matches.append((name, path, plugin))      
                
                        if len(matches) == 0:
                             allwords.append(plugin["package_name"])
                             allwords = allwords + plugin["components"]
                             allwords = allwords + plugin["prefabs"]
                        else:
                             allwords = []
                
        if len(matches) == 0:
                ## Do a close search...         
                closematches = difflib.get_close_matches(query, allwords)
                                  
        return (matches, closematches)
     
def installPlugin(name, tgtpath="./"):
        dstpath = os.path.join(tgtpath, name)
        print(" - installing '"+name+"' (destination path "+tgtpath)+")" 
        if os.path.exists(dstpath):
                print("   a file named '"+name+" already exits (skipping install).'")
        else: 
                desc = loadPluginDesc(dbpath, name)
                if desc == None:
                        print("   there is no plugin named '"+name+" in the recipes (skipping this one)'")
                        return 
                if len(desc["ssh-url"]) != 0:
                        print("   cloning from: " + desc["ssh-url"])
                        re = Repo.clone_from(desc["ssh-url"], to_path=dstpath)
                        re.remotes["origin"].rename("upstream")
                else:
                        print("   there is no git repository configured for '"+name+" (skipping this plugin)'")
                        return 
                
        ## Register to mu-repo
        subprocess.call(["mu", "register", dstpath])

def scanPluginsInDir(path):
        plugins = []
        pluginsWithDesc = []
        print(" - scanning directory "+path+ " for plugins.")
        for dirname in os.listdir(path):
                if os.path.exists(os.path.join(dirname,"CMakeLists.txt")) and loadPluginDesc(dbpath, dirname) != None:
                        pluginsWithDesc.append(dirname)        
                elif os.path.isdir(dirname):
                        print("Cannot process "+dirname)        
        return (plugins, pluginsWithDesc)
                        
def sortPlugins(plugins, alreadyProcessed=[]):
        deps = []

        for p in plugins:
                desc = loadPluginDesc(dbpath, p) 
                if desc != None:
                        re = sortPlugins(desc["package_dependencies"], alreadyProcessed+[name])
                        for cdep in re:
                                if cdep not in deps:
                                        deps.append(str(cdep))
                if str(p) not in deps:
                        deps.append(str(p))                        
        return deps                
                        
def generateCMakeList(tgtpath="./"):
        print(" - building CMakeLists.txt for: "+tgtpath)
        plugins, pluginsWithDesc = scanPluginsInDir(tgtpath)       
     
        absfile = os.path.join(tgtpath, "CMakeLists.txt")
        f = open(absfile,"w")

        pluginsWithDesc = sortPlugins(pluginsWithDesc)
        print("Installed plugins: "+str(pluginsWithDesc))
        for plugin in pluginsWithDesc:
                f.write("sofa_add_plugin({} {})\n".format(plugin, plugin))
     
        f.close()
        
def computeDependencies(name, alreadyProcessed=[]):
        desc = loadPluginDesc(dbpath, name)
        if desc == None:
                print("- unable to open the plugin named '"+name+"' (missing dependencies)") 
                return []
        
        deps = []
        for dep in desc["package_dependencies"]:
                re = computeDependencies(dep, alreadyProcessed+[name])
                for cdep in re:
                        if cdep not in deps:
                                deps.append(str(cdep))
                
                deps.append(str(dep))                        
        return deps

def searchFor(query):
        pluginsEntries = loadPluginsEntries(dbpath)
 
        (matches, closematches) = searchInPluginsEntries(pluginsEntries, query)
        if len(matches) != 0:
                print("- searching for '"+query+"' in "+str(len(pluginsEntries))+" plugins descriptions. Found:")
                
                for (f, path, desc) in matches:
                        wraps = textwrap.wrap(desc["description"], 80)
                        print('  {:<30}  {:<30}'.format(desc["package_name"], wraps[0]))
                        for extralines in wraps[1:]:
                                print('  {:<30}  {:<30}'.format("", extralines))
                                
        else:
                print("- searching for '"+query+"' in "+str(len(pluginsEntries))+" plugins descriptions. No exact match...but I found:")
                for value in closematches:
                        print("  {:<30}   (get details by typing: 'spm search {:<}')".format(value,value))
              
if len( sys.argv ) < 2:
        print("The Sofa Package Manager, invalid command line.")
        print("USAGE: spm [search|install] name1 <name2> <name3>")
        sys.exit(0)

if sys.argv[1] == "search":
        print("The Sofa Package Manager")
        searchFor(sys.argv[2])
                        
elif sys.argv[1] == "install":
        print("The Sofa Package Manager")
        names = sys.argv[2:]
        toInstall = []
        
        for name in names:
                pluginsEntries = loadPluginDesc(dbpath, name)
        
                if pluginsEntries == None:
                        print("- unable to open a plugin named '"+name+"' (falling back to search mode)") 
                        searchFor(name)
                        sys.exit(0)
                else:
                        depsToInstall = computeDependencies(name)+[name]
                        for i in depsToInstall:
                                if i not in toInstall:
                                        toInstall.append(i)
       
        if len(toInstall) != 0:                        
                print("- instal list is "+str(toInstall))
                for dep in toInstall:
                        installPlugin(dep)
                generateCMakeList()
