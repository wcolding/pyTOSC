import io
import zlib
import xml.etree.ElementTree as ET
import sys

if (len(sys.argv) < 2):
    print('Expected argument\nUsage: "python unpack.py toscFileName"')
    exit()

class TOSCName:
    text = ''
    modifier = ''

class TOSCObject:
    id = ''
    type = ''
    name = TOSCName()
    script = ''

toscNames = list()
toscScripts = list()

toscObjects = list()

def GetNameFrequency(name: TOSCName):
    counter = 0
    if len(toscNames) > 0:
        for elem in toscNames:
            if name.text == elem.text:
                counter += 1
    return counter

def GetRecursiveObjects(element: ET.Element, level = 0):
    cur_object = TOSCObject()
    objs_list = list()
    
    if element == None:
        return objs_list

    # From root, a node
    next = element.find('node')
    if next != None:
        objs_list += GetRecursiveObjects(next, level + 1)
    
    # Check children for new object nodes
    children = element.find('children')
    if children != None:
        next = children.findall('node')
        if len(next) > 0:
            for elem in next:
                objs_list += GetRecursiveObjects(elem, level + 1)

    # Check this level for a script property
    properties = element.find('properties')
    if properties != None:
        # 'element' is a node
        cur_object.id = element.attrib['ID']
        cur_object.type = element.attrib['type']

        for property in properties:
            key = property.find('key')
            value = property.find('value')

            if key.text == 'name':
                cur_object.name = TOSCName()
                if level < 2:
                    cur_object.name.text = 'root' # override calling an exported script "group.lua"
                else:
                    cur_object.name.text = value.text
                cur_object.name.text = '_'.join(cur_object.name.text.split()) # replace whitespace with underscores for filenames

            if key.text == 'script':
                if value.text != '':
                    if toscScripts.count(value.text) == 0:
                        cur_object.script = value.text
                        toscScripts.append(cur_object.script)
                    
                        # Modify names to avoid duplicates
                        freq = GetNameFrequency(cur_object.name)
                        if freq > 0:
                            cur_object.name.modifier = f'_{freq}'
                        #cur_object.name.modifier.replace(' ', '_')
                        toscNames.append(cur_object.name)

                        objs_list.append(cur_object) # only export valid scripts
                        toscObjects.append(cur_object)

                        # Replace script in xml with a reference to the external Lua file
                        value.text = '${' + cur_object.name.text + cur_object.name.modifier + '.lua}'
                    else:
                        # Find the object with a matching script and set a reference to that
                        for obj in toscObjects:
                            if obj.script == value.text:
                                value.text = '${' + obj.name.text + obj.name.modifier + '.lua}'

    return objs_list
    

file = io.open(sys.argv[1], 'rb')
data = file.read()
file.close()

outputFile = 'default.xml'

try:
    uncompressed = zlib.decompress(data)
except:
    print('Could not decompress file. Was this file saved with TouchOSC Editor?')
    uncompressed = data

stringXML = uncompressed.decode('UTF-8')
prettyXML = ET.XML(stringXML)

xmlProperties = prettyXML.findall(".//property")
for p in xmlProperties:
    if p[0].text == 'projectName':
        outputFile = f'{p[1].text}.xml'

ET.indent(prettyXML)

scriptObjs = GetRecursiveObjects(prettyXML)
submoduleStart = 0
submoduleNext = 0
submoduleName = ''
submoduleScript = ''
submoduleFileName = ''

for obj in scriptObjs:
    filename = f'Lua/{obj.name.text}{obj.name.modifier}.lua'
    print(f'Unpacking \'{obj.name.text}{obj.name.modifier}.lua\'...')
    # Look for submodules
    submoduleStart = 0
    while submoduleStart != -1:
        submoduleStart = obj.script.find('--Submodule.start(\'')
        if submoduleStart > -1:
            start = obj.script[0 : submoduleStart]
            end = obj.script[submoduleStart + 19 :]
            submoduleNext = end.find('\')')
            submoduleName = end[0:submoduleNext]
            submoduleFileName = f'Lua/Submodules/{submoduleName}'
            print(f'Unpacking submodule \'{submoduleName}\'...')
            
            end = obj.script[submoduleNext + 2 :]
            submoduleNext = obj.script.find('--Submodule.end()')
            submoduleScript = obj.script[submoduleStart : submoduleNext + 17]

            file = io.open(submoduleFileName, 'w')
            file.write(submoduleScript)
            file.close()

            obj.script = obj.script.replace(submoduleScript, f'--Submodule.include(\'{submoduleName}\')')

    file = io.open(filename, 'w')
    file.write(obj.script)
    file.close()

file = io.open(outputFile, 'w')
file.write(ET.tostring(prettyXML, encoding='unicode', method='xml'))
file.close()