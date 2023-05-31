import io
import os
import zlib
import pyTOSC.IterableObject as IObj

from configparser import ConfigParser
import xml.etree.ElementTree as ET
import copy
import uuid
import math

def Pack(xml_name):
    file = io.open('version', 'r')
    version = file.read()
    file.close()

    file = io.open(xml_name, 'r')
    data = file.read()
    file.close()

    replacements = 0
    lua_name = ''
    lua_script = ''
    submodule_start = 0
    submodule_next = 0
    submodule_name = ''
    submodule_script = ''
    start = ''
    end = ''

    root = ET.fromstring(data)
    xml_properties = root.findall(".//property")

    # First pass to replace scripts
    for p in xml_properties:
        if p[0].text == 'script' and p[1].text[0] == '$':
            lua_name = p[1].text[2:-1]
            print(f'Found script reference: {lua_name}')
            
            try:
                lua_file = io.open(os.path.normpath(f'Lua/{lua_name}'), 'r')
                lua_script = lua_file.read()
                lua_file.close()
            except:
                print(f'Unable to open file \'{lua_name}\'\nCheck that file is in Lua folder')
                print('Could not complete packing! Closing...')
                exit()

            # Check luaScript for submodules and insert them as needed
            while submodule_start != -1:
                submodule_start = lua_script.find('--Submodule.include(\'')
                if submodule_start > -1:
                    start = lua_script[0 : submodule_start]
                    end = lua_script[submodule_start + 21 :]
                    submodule_next = end.find('\')')
                    submodule_name = end[0:submodule_next]
                    if submodule_next > -1:
                        print(f'Found submodule reference: \'{submodule_name}\'')
                        
                        try:
                            lua_file = io.open(os.path.normpath(f'Lua/Submodules/{submodule_name}'), 'r')
                            submodule_script = lua_file.read()
                            lua_file.close()
                        except:
                            print(f'Unable to open submodule file \'{submodule_name}\'\nCheck that file is in Lua\Submodules folder')
                            print('Could not complete packing! Closing...')
                            exit()
                        
                        lua_script = lua_script.replace(f'--Submodule.include(\'{submodule_name}\')', submodule_script)
                        replacements += 1
            
            # Replace script reference with actual script
            p[1].text = lua_script
            replacements += 1

    print(f'Total script replacements: {replacements}\n')

    # Second pass to duplicate iterable objects
    iterable_buttons = IObj.IterableButton('mix_layout.ini')
    iterable_buttons.Iterate(root)

    auto_pagers = IObj.AutoPager('tabs.ini')
    auto_pagers.Iterate(root)

    iterable_cameras = IObj.IterableCamera('mix_layout.ini', 'cameras.ini')
    iterable_cameras.Iterate(root)



    main_data = ET.tostring(root, encoding='unicode')

    # Build specific changes
    build_config = ConfigParser()
    build_config.read('builds.ini')
    sections = build_config.sections()
    print(f'Build configurations found: {sections}\n')


    if len(sections) > 0:
        build_index = 0
        for section in sections:
            build_name = f'Build/{xml_name[0:-4]} ({section}) {version}.tosc'
            temp_data = main_data

            print(section)
            
            # Replace string '$BUILD_NAME' with actual build name. This can automate relabeling things
            temp_data = temp_data.replace('$BUILD_NAME', section)
            
            # Replace string '$VERSION' with version
            temp_data = temp_data.replace('$VERSION', f'Version {version}')

            build_root = ET.fromstring(temp_data)
            properties = build_config[section].items()
            for property in properties: 
                xml_properties = build_root.findall(".//property")
                for p in xml_properties:
                    if p[0].text == property[0].upper():
                        print(f'Found {p[0].text}')
                        print(f'Replacing value "{p[1].text}" with "{property[1]}"')
                        p[1].text = property[1]
            
            # Unique UUIDs for each build
            if build_index > 0:
                nodes = build_root.findall(".//node")
                for node in nodes:
                    node.set('ID', str(uuid.uuid4()))
            
            build_data = ET.tostring(build_root)
            compressed = zlib.compress(build_data)

            file = io.open(build_name, 'wb')
            file.write(compressed)
            file.close()
            print(f'Wrote to {build_name}')
            print('----')
            build_index += 1
    else:
        build_name = f'Build/{xml_name[0:-4]} {version}.tosc'
        build_data = main_data.encode('UTF-8')
        compressed = zlib.compress(build_data)
        
        file = io.open(build_name, 'wb')
        file.write(compressed)
        file.close()
        print(f'Wrote to {build_name}')
        print('----')