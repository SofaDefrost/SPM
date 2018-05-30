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
import spm.repo
import appdirs
import requests
import io
import platform
import shutil
import zipfile
from zipfile import *
from git import Repo

def extract(self, member, path=None, pwd=None):
    """Extract a member from the archive to the current working directory,
       using its full name. Its file information is extracted as accurately
       as possible. `member' may be a filename or a ZipInfo object. You can
       specify a different directory using `path'.
    """
    if not isinstance(member, ZipInfo):
        member = self.getinfo(member)

    if path is None:
        path = os.getcwd()

    return self._extract_member(member, path, pwd)

class MyZipFile(zipfile.ZipFile):
    def __init__(self, o, withPerm=False):
        super(MyZipFile, self).__init__(o)
        self.withPerm = withPerm

    def extract(self, member, path=None, pwd=None):
        if not isinstance(member, ZipInfo):
            member = self.getinfo(member)

        if path is None:
            path = os.path.abspath(os.getcwd())
        path=os.path.abspath(path)
        ret_val = self._extract_member(member, path, pwd)

        if not self.withPerm:
                return ret_val

        if platform.system() == "Linux":
                if member.external_attr >> (32-4) == 10:
                        print("SYMLINK: "+path +"/"+member.filename)
                        floc = os.path.join(path, member.filename)
                        with open(floc, "r") as f:
                                target = f.read()
                                target = os.path.join(os.path.dirname(floc), target)
                        
                        os.unlink(floc)
                        os.symlink(target, floc)                        
                else:        
                        attr = member.external_attr >> 16
                        os.chmod(ret_val, attr)
        else:
                raise Exception("Binary packages are not yet on "+platform.system())
        
        return ret_val

    
def download_extract_zip(url, destpath, withPerm=False):
        """
        Download a ZIP file and extract its contents in memory
        yields (filename, file-like object) pairs
        """
        response = requests.get(url)
        with MyZipFile(io.BytesIO(response.content), withPerm) as thezip:
            thezip.extractall(destpath)
            return thezip.namelist()[0]
                        
        raise Exception("Unable to fetch data from "+url)

userdblocation = os.path.join(appdirs.user_data_dir("sofa-spm", "Sofa"), "recipes")

if not os.path.exists(userdblocation):
        dbpath = spm.repo.location
else:
        dbpath = userdblocation

def upgrade():
        cachelocation = appdirs.user_data_dir("sofa-spm", "Sofa")
        configlocation = appdirs.user_config_dir("sofa-spm", "Sofa")
        configfile = os.path.join(configlocation, "sources.json")
        print("Package source config location: "+configlocation) 
        print("Package cache location: "+cachelocation)
        
        if not os.path.exists(configlocation):
                os.makedirs(configlocation)
        
        if not os.path.exists(configfile):
                db = {"Main" : "https://github.com/SofaDefrost/SPM-RECIPES/archive/master.zip"} 
                f = open(configfile,"wt")
                f.write(json.dumps(db))
                f.close() 
        
        sources = json.loads(open(configfile).read())
       
        dblocation = os.path.join(appdirs.user_data_dir("sofa-spm", "Sofa"), "recipes")
        for sourcename in sources:
                repo = sources[sourcename]
                
                print("Fetching new recipes for '"+sourcename+"' from: "+repo)                
                dirname = download_extract_zip(repo, dblocation, withPerm=False)
                
                if os.path.exists(os.path.join(dblocation, sourcename)):
                        shutil.rmtree(os.path.join(dblocation, sourcename))
                shutil.move(os.path.join(dblocation, dirname), os.path.join(dblocation, sourcename))
                print("Done. ")
                
 
def loadPluginsEntries(dbpath):
        ### Import the database 
        allfilenames = [] 
        for (basepath, dirnames, filenames) in os.walk(dbpath):
                for f in filenames:
                        absname = os.path.join(basepath, f)
                        location = os.path.relpath(basepath, dbpath)
                        allfilenames.append((f, absname, location))
        return allfilenames

def loadPluginDesc(dbpath, pluginname):
        ### Try to load manually the plugin
        for (base, dirs, files) in os.walk(dbpath):
                path = os.path.join(base, pluginname+".sp")
                if os.path.exists(path):
                        return json.loads(open(path).read())
        return None
        
def searchInPluginsEntries(pluginsname, query, full=False):
        matches = []
        closematches = []
        allwords = []
        for (name, path, location) in pluginsname:
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
                             allwords = allwords + [(location + "/" + plugin["package_name"])]
                        else:
                             allwords = []
                
        if full or len(matches) == 0:
                ## Do a close search...  
                allwords += getPluginSources(dbpath)
                closematches = difflib.get_close_matches(query, allwords)
                                  
        return (matches, closematches)
     
def installPlugin(name, tgtpath="./"):
        desc = loadPluginDesc(dbpath, name)        
        dstpath = os.path.join(tgtpath, desc["package_name"])
        print(" - installing '"+name+"' (destination path "+tgtpath)+")" 
        if os.path.exists(dstpath):
                print("   a file named '"+name+" already exits (skipping install).'")
        else: 
                if desc == None:
                        print("   there is no plugin named '"+name+" in the recipes (skipping this one)'")
                        return
                if desc["package_type"] == "source":         
                        if len(desc["ssh-url"]) != 0:
                                print("   cloning from: " + desc["ssh-url"])
                                re = Repo.clone_from(desc["ssh-url"], to_path=dstpath)
                                re.remotes["origin"].rename("upstream")
                        else:
                                print("   there is no git repository configured for '"+name+" (skipping this package)'")
                                return 
                elif desc["package_type"] == "binary":
                        if len(desc["http-url"]) != 0:
                                import re
                                url = desc["http-url"]
                                r = re.search("\$OAUTH\{(.*)\}", url)
                                if r:
                                        tokenID = r.groups()[0]
                                        tokens = loadTokens()
                                        if tokenID not in tokens:
                                                print("This URL requires an authentication token for "+str(tokenID)+" which is missing. (try sofa-spm.py token list)")
                                        else:
                                                value = tokens[tokenID] 
                                                url = re.sub("\$OAUTH\{.*\}", value, url)                                       
                                print("   getting file from: " + url)
                                download_extract_zip(url, dstpath, withPerm=True)
                        else:
                                print("   there is no archive file to download for '"+name+" (skipping this package)'")
                                return
                elif desc["package_type"] == "meta":
                        return 
                                            
        ## Register to mu-repo
        subprocess.call(["mu", "register", dstpath])

def getPluginSources(dbpath):
        sources=[]
        for (basedir, dirs, files) in os.walk(dbpath):
                if len(dirs) != 0:
                        sources.append(os.path.relpath(basedir, dbpath))
        return sources

def listPlugins(path, source=None):
        lastgroup = ""
        prefix = ""
        if source != None:
                path = os.path.join(dbpath, source)
                prefix = source
        entries = loadPluginsEntries(path)
        for e in entries:
                if lastgroup != e[2]:
                        lastgroup = e[2]
                        print(os.path.join(prefix,e[2])+":")
                print("   " +str(e[0]))
        if len(entries) == 0:
                searchFor(source, True)
        return 
        
def scanPluginsInDir(path):
        plugins = []
        pluginsWithDesc = []
        print(" - scanning directory "+path+ " for plugins.")
        for dirname in os.listdir(path):
                if os.path.exists(os.path.join(dirname,"CMakeLists.txt")) and loadPluginDesc(dbpath, dirname) != None:
                        pluginsWithDesc.append(dirname)        
                elif os.path.isdir(dirname):
                        print("Probably not a SOFA plugin: "+dirname)        
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

def printPackage(desc):
        wraps = textwrap.wrap(desc["description"], 80)
        print('  {:<30}  {:<30}'.format(desc["package_name"], wraps[0]))
        for extralines in wraps[1:]:
                print('  {:<30}  {:<30}'.format("", extralines))

def infoFor(query):
        print("Info for: "+query)
        if query in os.listdir(dbpath):
                print("   "+query+" is a package source. (spm list "+query+" to get the list of plugin in this source).")
                return
        
        desc = loadPluginDesc(dbpath, query)
        if desc != None:
                printPackage(desc)                
                print('  {:<30}  {:<30}'.format("", "(to install this package type 'spm install "+query+"')"))

def searchFor(query, full=False):
        pluginsEntries = loadPluginsEntries(dbpath)
 
        (matches, closematches) = searchInPluginsEntries(pluginsEntries, query, full)
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
                        print("  {:<30}   (get details by typing: 'spm info {:<}')".format(value,value))
              
def loadTokens():
        configlocation = appdirs.user_config_dir("sofa-spm", "Sofa")
        tokenfile = os.path.join(configlocation, "accesstokens.json")
        if not os.path.exists(tokenfile):
                with open(tokenfile,"wt") as f:
                        print("Initializing token file at:" + tokenfile)
                        f.write(json.dumps({}))
        
        return json.loads(open(tokenfile,"r").read())

def saveTokens(t):
        configlocation = appdirs.user_config_dir("sofa-spm", "Sofa")
        tokenfile = os.path.join(configlocation, "accesstokens.json")
        with open(tokenfile,"w") as f:
                f.write(json.dumps(t))

def addToken(key, value):
        t = loadTokens()
        t[key] = value
        saveTokens(t)


def printUsage():
        print("USAGE: sofa-spm <cmd> <cmd-args>")
        print("  list                     print the list of all the available packages.")        
        print("  search <string>          search for <string> in the packages lists & description.")        
        print("  info <name>              print the package description.")        
        print("  install <name> <name2>   install the requested packages & their dependencies.")        
        print("  upgrade                  get a more recent version of the available packages from")
        print("                          the different registered packages sources.")        
        print("  token list               print the list of registerd OAuth token to access private repository.")
        print("  token add <ID> <VAL>     add a new token for entry 'ID' with value 'VAL'.")


print("The Sofa Package Manager")

if len( sys.argv ) < 2:
        printUsage()
        sys.exit(0)

if sys.argv[1] == "search":
        searchFor(sys.argv[2], True)

elif sys.argv[1] == "list":   
        if len(sys.argv) == 2:
                listPlugins(dbpath)
        else:
                listPlugins(dbpath, sys.argv[2])
        
elif sys.argv[1] == "info":   
        infoFor(sys.argv[2])
        
elif sys.argv[1] == "upgrade":
        upgrade()
        sys.exit(0)
                             
elif sys.argv[1] == "install":
        names = sys.argv[2:]
        toInstall = []
        
        for name in names:
                pluginsEntries = loadPluginDesc(dbpath, name)
        
                if pluginsEntries == None:
                        print("- unable to open a plugin named '"+name+"' (falling back to search mode)") 
                        searchFor(name, True)
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

elif sys.argv[1] == "help":
        printUsage()
        sys.exit(0)
        
elif sys.argv[1] == "update-imports":
        name = sys.argv[2]
        desc = loadPluginDesc("./", name)
        print("This project needs :"+str(desc["package_dependencies"]))

elif sys.argv[1] == "token":       
        if len(sys.argv) <3:
                print("Invalid (token) command.")
                print("USAGE: spm token <list|add> ")
                sys.exit(0)

        if sys.argv[2] == "list":
                if len(sys.argv) <3:
                        print("Invalid (token list) command line.")
                        print("USAGE: spm token list")
                        sys.exit(0)
                tokens = loadTokens()
                print("Your access tokens: ")
                for tk in tokens:
                      print("  "+tk+" : "+tokens[tk])  
        elif sys.argv[2] == "add":
                if len(sys.argv) != 5:
                        print("Invalid (token add) command line.")
                        print("USAGE: spm token add <name> <token>")
                        sys.exit(0)
                        
                token_name = sys.argv[3] 
                token_value = sys.argv[4]
                addToken(token_name, token_value)
                print("Adding token "+token_name+" : "+token_value+" to database.")
else:
        printUsage()
                        
if dbpath == spm.repo.location:
        print("")
        print("Notes:")
        print(" You are using the default repository which may be out of date. ")
        print(" Please consider upgrading the packages description by typing sofa-spm.py upgrade")

