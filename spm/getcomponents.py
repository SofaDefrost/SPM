import Sofa
import softrobots

if len(sys.argv) != 2 and len(sys.argv) != 3:
        print("USAGE: runSofa getcomponent.py --argv <YourPluginName> <PythonPart>")
        sys.exit(-1)

def createScene(rootNode):                
        plugin = sys.argv[1]
        pyplugin = None
        if len(sys.argv) == 3:
                pyplugin = sys.argv[2]
        rootNode.createObject("RequiredPlugin", name=plugin)
        
        components = {}
        for c in Sofa.getComponentsFromTarget(plugin):
                if c not in components:
                        components[c] = c         
        print('"components" : '+str(components.keys()))
             
        if pyplugin != None:
        
                prefabs = {}                
                print('"components" : '+str(components.keys()))
