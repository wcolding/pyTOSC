import io
import zlib
import sys
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
                lua_file = io.open(f'Lua\\{lua_name}', 'r')
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
                            lua_file = io.open(f'Lua\\Submodules\\{submodule_name}', 'r')
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
    xml_iterable_buttons_groups = root.findall(".//*[key='iterableButton']......")

    if len(xml_iterable_buttons_groups) > 0:
        layout_config = ConfigParser()
        layout_config.read('mix_layout.ini')

        grid_start_x = int(layout_config['Default']['GridStartX'])
        grid_start_y = int(layout_config['Default']['GridStartY'])
        button_width = int(layout_config['Default']['ButtonWidth'])
        button_height = int(layout_config['Default']['ButtonHeight'])
        padding_x = int(layout_config['Default']['PaddingX'])
        padding_y = int(layout_config['Default']['PaddingY'])
        auto_channels = int(layout_config['Default']['AutoChannels'])
        buttons_per_row = int(layout_config['Default']['ButtonsPerRow'])
        text_size = int(layout_config['Default']['TextSize'])

        for xml_iterable_buttons_group in xml_iterable_buttons_groups:
            xml_iterable_buttons = xml_iterable_buttons_group.findall(".//*[key='iterableButton']....")
        
            for i in range(auto_channels):
                if i == 0:
                    curButton = xml_iterable_buttons[0]
                else:
                    curButton = copy.deepcopy(xml_iterable_buttons[0])
                
                children = curButton.findall(".//node")

                name = curButton.find(".//*[key='name']")
                tag = curButton.find(".//*[key='tag']")
                iterable = curButton.find(".//*[key='iterableButton']")
                frame = curButton.find(".//*[key='frame']")
                name[1].text = f'Ch{i+1:02}'
                tag[1].text = f'{i+1:02}'
                iterable[1].text = '0'

                if i == 0:
                    # Resize button
                    frame[1][2].text = str(button_width)
                    frame[1][3].text = str(button_height)

                    # Position button
                    frame[1][0].text = str(grid_start_x)
                    frame[1][1].text = str(grid_start_y)

                    # Operate on children (button and label)
                    for child in children:
                        child_frame = child.find(".//*[key='frame']")
                        child_frame[1][2].text = str(button_width)
                        child_frame[1][3].text = str(button_height)
                else:
                    # Reposition duplicate buttons
                    row = math.floor(i / buttons_per_row)
                    column = i % buttons_per_row

                    new_x = grid_start_x + ((button_width + padding_x) * column)
                    new_y = grid_start_y + ((button_height + padding_y) * row)

                    frame[1][0].text = str(new_x)
                    frame[1][1].text = str(new_y)

                # Write default names for button labels and set text size
                for child in children:
                    if child.get('type') == 'LABEL':
                        text_val = child.find(".//*[key='text']")
                        text_val[3].text = name[1].text
                        text_size_val = child.find(".//*[key='textSize']")
                        text_size_val[1].text = str(text_size)
                # Update all UUIDs
                curButton.set('ID', str(uuid.uuid4()))

                for child in children:
                    child.set('ID', str(uuid.uuid4()))
            
                if i > 0:
                    # Append new button
                    xml_iterable_buttons_group.append(curButton)
    
    # Iterate tabs
    xml_auto_pagers = root.findall(".//*[key='autoPager']....")
    
    if len(xml_auto_pagers) > 0:
        tab_config = ConfigParser()
        tab_config.read('tabs.ini')
        tabs = tab_config.sections()
        print(f'Tabs defined: {tabs}')

        for pager in xml_auto_pagers:
            pager_id = int(pager.find(".//*[key='autoPager']")[1].text)
            print(f'Pager id: {pager_id}')
            pager_children = pager.find(".//children")
            current_tab_index = 0

            for tab in tabs:
                if int(tab_config[tab]['Pager']) == pager_id:
                    tab_object = pager.find(".//children/node")
                    if tab_object != None:
                        if current_tab_index > 0:
                            tab_object = copy.deepcopy(tab_object)

                        tab_name = tab_object.find(".//*[key='name']")
                        tab_label = tab_object.find(".//*[key='tabLabel']")
                        tab_name[1].text = tab_config[tab]['Label']
                        tab_label[1].text = tab_config[tab]['Label']

                        tab_group = tab_object.find(".//children/node")
                        if tab_group != None:
                            tab_group_name = tab_group.find(".//*[key='name']")
                            tab_group_tag = tab_group.find(".//*[key='tag']")
                            mix_number = int(tab_config[tab]['Index'])
                            print(f'Creating tab for index {mix_number:02}...')
                            tab_group_name[1].text = tab
                            tab_group_tag[1].text = f'{mix_number:02}'
                            
                            if current_tab_index > 0:
                                # Reassign UUIDs
                                tab_nodes = tab_object.findall(".//children/node")
                                if len(tab_nodes) > 0:
                                    for node in tab_nodes:
                                        node.set('ID', str(uuid.uuid4()))
                                
                                # Add new tab 
                                pager_children.append(tab_object)

                            current_tab_index += 1

    main_data = ET.tostring(root, encoding='unicode')

    # Build specific changes
    build_config = ConfigParser()
    build_config.read('builds.ini')
    sections = build_config.sections()
    print(f'\nBuild configurations found: {sections}\n')


    if len(sections) > 0:
        build_index = 0
        for section in sections:
            build_name = f'Build/{xml_name[0:-4]} ({section}) {version}.tosc'
            temp_data = main_data

            print(section)
            
            # Replace string '$BUILD_NAME' with actual build name. This can automate relabeling things
            temp_data = temp_data.replace('$BUILD_NAME', section)

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